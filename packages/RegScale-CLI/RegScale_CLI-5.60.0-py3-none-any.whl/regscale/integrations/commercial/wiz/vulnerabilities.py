"""
Vulnerabilities Integration
"""

import json
import logging
import os
from datetime import timedelta, datetime
from enum import Enum
from typing import List, Dict, Optional

from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime, check_file_path
from regscale.core.utils.date import date_str, days_from_today, datetime_obj, date_obj
from regscale.integrations.commercial.wiz.constants import (
    VULNERABILITY_QUERY,
    CONTENT_TYPE,
    VULNERABILITY_FILE_PATH,
    CLOUD_CONFIG_FINDING_QUERY,
    HOST_VULNERABILITY_QUERY,
    DATA_FINDING_QUERY,
    HOST_VULNERABILITY_FILE_PATH,
    CLOUD_CONFIG_FINDINGS_FILE_PATH,
    DATA_FINDINGS_FILE_PATH,
)
from regscale.models.regscale_models import Vulnerability, Asset, SecurityPlan, ScanHistory
from regscale.utils import PaginatedGraphQLClient, get_value
from regscale.models import regscale_models

logger = logging.getLogger(__name__)

WIZ_ASSET_ID = "vulnerableAsset.id"
SOURCE_RULE_ID = "sourceRule.id"


class WizVulnerabilityType(Enum):
    """
    Enum for Wiz vulnerability types
    """

    HOST_FINDING = "host_finding"
    DATA_FINDING = "data_finding"
    VULNERABILITY = "vulnerability"
    CONFIGURATION = "configuration_finding"


class VulnerabilitiesIntegration:
    """
    Fetches vulnerabilities from Wiz
    """

    def __init__(
        self,
        wiz_project_id: str,
        parent_id: int,
        scan_tool: str,
        parent_module: str = SecurityPlan.get_module_slug(),
        filter_by_override: str = None,
    ):
        self.parent_id = parent_id
        self.parent_module = parent_module
        self.app = Application()
        self.config = self.app.config
        self.scan_tool = scan_tool
        self.name = "Vulnerabilities"
        self.file_path = VULNERABILITY_FILE_PATH
        self.findings: List[Vulnerability] = []
        self.issues: List[regscale_models.Issue] = []
        self.issues_updated: List[regscale_models.Issue] = []
        self.assets: List[regscale_models.Asset] = []
        self.asset_dict = {}
        self.assets: List[Asset] = []
        self.scan_history: Optional[ScanHistory] = None
        self.low = 0
        self.medium = 0
        self.high = 0
        self.critical = 0
        self.filter_by = {"projectId": wiz_project_id.split(",")}
        if filter_by_override:
            self.filter_by = json.loads(filter_by_override)
        self.variables = {
            "first": 100,
            "filterBy": self.filter_by,
            "fetchTotalCount": False,
        }
        self.pull_limit_hours = self.config.get("wizFullPullLimitHours", 1)
        self.low_days = self.config.get("issues.wiz.high", 60)
        self.medium_days = self.config.get("issues.wiz.medium", 210)
        self.high_days = self.config.get("issues.wiz.low", 394)
        self.due_date_map = {
            regscale_models.IssueSeverity.High: date_str(days_from_today(self.low_days)),
            regscale_models.IssueSeverity.Moderate: date_str(days_from_today(self.medium_days)),
            regscale_models.IssueSeverity.Low: date_str(days_from_today(self.high_days)),
        }
        self.interval_hours = self.config.get("wizFullPullLimitHours", 8)
        self.asset_lookup = "vulnerableAsset"
        self.wiz_vulnerability_type = WizVulnerabilityType.VULNERABILITY
        self.query = VULNERABILITY_QUERY
        self.topic_key = "vulnerabilityFindings"

        self.wiz_vulnerability_types = [
            {
                "type": WizVulnerabilityType.VULNERABILITY,
                "query": VULNERABILITY_QUERY,
                "topic_key": "vulnerabilityFindings",
                "file_path": VULNERABILITY_FILE_PATH,
                "asset_lookup": "vulnerableAsset",
                "variables": {
                    "first": 200,
                    "filterBy": self.filter_by,
                    "fetchTotalCount": False,
                },
            },
            {
                "type": WizVulnerabilityType.CONFIGURATION,
                "query": CLOUD_CONFIG_FINDING_QUERY,
                "topic_key": "configurationFindings",
                "file_path": CLOUD_CONFIG_FINDINGS_FILE_PATH,
                "asset_lookup": "resource",
                "variables": {
                    "first": 200,
                    "quick": True,
                    "filterBy": {
                        "rule": {},
                        "resource": {"projectId": [wiz_project_id]},
                    },
                },
            },
            {
                "type": WizVulnerabilityType.HOST_FINDING,
                "query": HOST_VULNERABILITY_QUERY,
                "topic_key": "hostConfigurationRuleAssessments",
                "file_path": HOST_VULNERABILITY_FILE_PATH,
                "asset_lookup": "resource",
                "variables": {
                    "first": 200,
                    "filterBy": {
                        "resource": {"projectId": [wiz_project_id]},
                        "frameworkCategory": [],
                    },
                },
            },
            {
                "type": WizVulnerabilityType.DATA_FINDING,
                "query": DATA_FINDING_QUERY,
                "topic_key": "dataFindingsGroupedByValue",
                "file_path": DATA_FINDINGS_FILE_PATH,
                "asset_lookup": "resource",
                "variables": {
                    "first": 200,
                    "filterBy": {"projectId": [wiz_project_id]},
                    "orderBy": {"field": "FINDING_COUNT", "direction": "DESC"},
                    "groupBy": "GRAPH_ENTITY",
                },
            },
        ]

    def run(self):
        """
        Fetches vulnerabilities from Wiz and creates them in the application
        """
        self.fetch_assets()
        for wiz_vulnerability_type in self.wiz_vulnerability_types:
            self.wiz_vulnerability_type = wiz_vulnerability_type.get("type")
            self.query = wiz_vulnerability_type.get("query")
            self.topic_key = wiz_vulnerability_type.get("topic_key")
            self.file_path = wiz_vulnerability_type.get("file_path")
            self.variables = wiz_vulnerability_type.get("variables")
            self.asset_lookup = wiz_vulnerability_type.get("asset_lookup")
            self.findings = []
            self.issues = []
            self.issues_updated = []
            self.fetch_data_and_create_vulnerabilities()

    def fetch_data_and_create_vulnerabilities(self):
        """
        Fetches data and creates vulnerabilities
        """
        nodes = self.fetch_data_if_needed()
        self.map_node_data(nodes)
        logger.info(f"Found total of {len(self.findings)} vulnerabilities from Wiz.")
        vulnerabilities = regscale_models.Vulnerability.batch_create(items=self.findings)
        if vulnerabilities:
            logger.info(f"Created total of {len(vulnerabilities)} vulnerabilities from Wiz.")
        logger.info(f"Found total of {len(self.issues)} issues from Wiz.")
        issues = regscale_models.Issue.batch_create(items=self.issues)
        if issues:
            logger.info(f"Created total of {len(issues)} issues from Wiz.")

        # Update the issues that were already created
        if self.issues_updated:
            self.issues_updated = list(set(self.issues_updated))

            with open("artifacts/issues_updated.json", "w") as f:
                json.dump([i.model_dump() for i in self.issues_updated], f)
            issues = regscale_models.Issue.batch_update(items=self.issues_updated)
            logger.info(f"Updated total of {len(issues)} issues from Wiz.")

    def fetch_assets(self):
        """
        Fetches assets from the application
        """
        self.assets = Asset.get_all_by_parent(parent_id=self.parent_id, parent_module=self.parent_module)
        self.asset_dict = {asset.wizId: asset for asset in self.assets} if self.assets else {}

    def set_severity_count(self, severity: str):
        """
        Increments the count of the severity
        :param str severity: Severity of the vulnerability
        """
        if severity == "LOW":
            self.low += 1
        elif severity == "MEDIUM":
            self.medium += 1
        elif severity == "HIGH":
            self.high += 1
        elif severity == "CRITICAL":
            self.critical += 1

    def update_counts(self):
        """
        Updates the counts of the vulnerabilities in the scan history
        """
        if not self.scan_history:
            return
        self.scan_history.vLow = self.low
        self.scan_history.vMedium = self.medium
        self.scan_history.vHigh = self.high
        self.scan_history.vCritical = self.critical
        self.scan_history.save()

    def fetch_data_if_needed(self) -> List[Dict]:
        """
        Fetches data if the file is not present or is older than the fetch interval
        :returns: List[Dict] of data nodes
        :rtype: List[Dict]
        """
        fetch_interval = timedelta(hours=self.interval_hours)  # Interval to fetch new data
        current_time = datetime.now()

        # Check if the file exists and its last modified time
        if os.path.exists(self.file_path):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(self.file_path))
            if current_time - file_mod_time < fetch_interval:
                nodes = self.load_file()
                return nodes
        nodes = self.fetch_data()
        self.write_to_file(nodes)
        return nodes

    def write_to_file(self, nodes: List[Dict]):
        """
        Writes the nodes to a file
        :param List[Dict] nodes: List of nodes to write
        """
        check_file_path("artifacts")
        with open(self.file_path, "w") as file:
            json.dump(nodes, file)

    def load_file(self) -> List[Dict]:
        """
        Loads the file and maps the nodes to Vulnerability objects
        Returns: List of Dict
        :rtype: List[Dict]
        """
        check_file_path("artifacts")
        with open(self.file_path, "r") as file:
            return json.load(file)

    @staticmethod
    def set_severity_count_for_scan(severity: str, scan_history: regscale_models.ScanHistory):
        """
        Increments the count of the severity
        :param str severity: Severity of the vulnerability
        :param regscale_models.ScanHistory scan_history: Scan history object
        """
        if severity == "LOW":
            scan_history.vLow += 1
        elif severity == "MEDIUM":
            scan_history.vMedium += 1
        elif severity == "HIGH":
            scan_history.vHigh += 1
        elif severity == "CRITICAL":
            scan_history.vCritical += 1
        scan_history.save()

    def map_node_data(self, nodes: List[Dict]):
        """
        Maps the node to a Vulnerability object
        :param List[Dict] nodes: Node from the Wiz API
        """
        for node in nodes:
            if self.asset_lookup not in node or not node.get(self.asset_lookup, {}):
                continue
            asset = self.asset_dict.get(node.get(self.asset_lookup, {}).get("id"))
            scan_date = node.get("publishedDate", node.get("analyzedAt"))
            if asset:
                existing_scan = self.find_existing_scan(asset, scan_date)
                scan_history = self.set_existing_scan(existing_scan, asset, scan_date)

                self.set_severity_count(node.get("severity", "").upper())
                name: str = node.get("name")
                cve = name if name and name.startswith("CVE") and not node.get("cve") else node.get("cve")
                self.set_severity_count_for_scan(severity=node.get("severity", "").upper(), scan_history=scan_history)
                existing_issues = regscale_models.Issue.get_all_by_parent(
                    parent_id=self.parent_id, parent_module=self.parent_module
                )
                existing_issues_dict = {issue.parentId: issue for issue in existing_issues} if existing_issues else {}
                existing_vulnerabilities_list = regscale_models.Vulnerability.get_all_by_parent(
                    parent_id=scan_history.id,
                )
                existing_vulnerabilities = {
                    v.title: v for v in existing_vulnerabilities_list if existing_vulnerabilities_list
                }
                self.handle_vulnerabilities(
                    existing_vulnerabilities=existing_vulnerabilities,
                    node=node,
                    existing_issues_dict=existing_issues_dict,
                    name=name,
                    asset=asset,
                    cve=cve,
                    scan_history=scan_history,
                )

    def find_existing_scan(self, asset: regscale_models.Asset, scan_date: str) -> regscale_models.ScanHistory:
        """
        Finds the existing scan history
        :param regscale_models.Asset asset: Asset object
        :param str scan_date: Scan date
        :returns: Scan history object
        :rtype: regscale_models.ScanHistory
        """
        existing_scan_histories = (
            regscale_models.ScanHistory.get_all_by_parent(parent_id=asset.id, parent_module="assets") or []
        )
        existing_scan = None
        for scan in existing_scan_histories:
            if scan.scanningTool == self.scan_tool and date_obj(scan.scanDate) == date_obj(scan_date):
                existing_scan = scan
                break
        return existing_scan

    def set_existing_scan(
        self, existing_scan: regscale_models.ScanHistory, asset: regscale_models.Asset, scan_date: str
    ) -> regscale_models.ScanHistory:
        """
        Sets the existing scan history
        :param regscale_models.ScanHistory existing_scan: Existing scan history
        :param regscale_models.Asset asset: Asset object
        :param str scan_date: Date of the scan
        :returns: Scan history object
        :rtype: regscale_models.ScanHistory
        """
        if not existing_scan:
            scan_history = regscale_models.ScanHistory(
                scanningTool=self.scan_tool,
                parentId=asset.id,
                parentModule="assets",
                scanDate=scan_date,
            ).create()
        else:
            scan_history = existing_scan
        return scan_history

    def handle_vulnerabilities(
        self,
        existing_vulnerabilities: Dict[str, regscale_models.Vulnerability],
        node: Dict,
        existing_issues_dict: Dict[str, regscale_models.Issue],
        name: str,
        asset: regscale_models.Asset,
        cve: str,
        scan_history: regscale_models.ScanHistory,
    ):
        """
        Handles the vulnerabilities
        :param Dict[str, regscale_models.Vulnerability] existing_vulnerabilities: Existing vulnerabilities
        :param Dict node: Nodes from the Wiz API
        :param Dict[str, regscale_models.Issue] existing_issues_dict: Existing issues
        :param str name: Name of the vulnerability
        :param regscale_models.Asset asset: Asset object
        :param str cve: CVE of the vulnerability
        :param regscale_models.ScanHistory scan_history: Scan history object
        """
        if existing_vulnerabilities and name in existing_vulnerabilities:
            vulnerability = existing_vulnerabilities.get(name)

            if existing_issues_dict and name in existing_issues_dict:
                issue = existing_issues_dict.get(str(asset.id))
                updated_issue = self.update_issue(issue=issue, vulnerability=vulnerability, node=node, asset=asset)
                if updated_issue not in self.issues_updated:
                    self.issues_updated.append(updated_issue)
        else:
            vulnerability = self.create_vulnerability_from_node(
                name=name,
                cve=cve,
                asset=asset,
                node=node,
                scan_history=scan_history,
            )
            self.create_issue_from_vulnerability(vulnerability, node, asset=asset)
            if vulnerability not in self.findings:
                self.findings.append(vulnerability)

    @staticmethod
    def map_fields_from_node(
        name: str, cve: str, asset: regscale_models.Asset, node: Dict, scan_history: regscale_models.ScanHistory
    ) -> Dict:
        """
        Maps fields from a node to a dictionary for creating a vulnerability
        :param str name: Name of the vulnerability
        :param str cve: CVE of the vulnerability
        :param regscale_models.Asset asset: Asset object
        :param Dict node: Node from the Wiz API
        :param regscale_models.ScanHistory scan_history: Scan history object
        :returns: Dictionary with mapped fields
        :rtype: Dict
        """
        return {
            "uuid": node.get("id"),
            "title": name,
            "description": node.get("description"),
            "severity": node.get("severity"),
            "cve": cve,
            "cvsSv3BaseScore": node.get("score"),
            "firstSeen": node.get("firstDetectedAt"),
            "lastSeen": node.get("lastDetectedAt"),
            "exploitAvailable": node.get("hasExploit", False),
            "parentId": asset.id,
            "parentModule": "assets",
            "dns": "unknown",
            "ipAddress": "unknown",
            "mitigated": False,
            "port": "",
            "plugInId": 0,
            "scanId": scan_history.id,
        }

    @staticmethod
    def map_fields_from_configuration_node(
        node: Dict, asset: regscale_models.Asset, scan_history: regscale_models.ScanHistory
    ) -> Dict:
        """
        Maps fields from a configuration node to a dictionary for creating a vulnerability
        :param Dict node: Node from the GraphQL query
        :param regscale_models.Asset asset: Asset object
        :param regscale_models.ScanHistory scan_history: Scan history object
        :returns: Dictionary with mapped fields
        :rtype: Dict
        """
        return {
            "uuid": node.get("id"),
            "title": node.get("name"),
            "description": node.get("rule", {}).get("description"),
            "severity": node.get("severity", "Low"),
            "firstSeen": node.get("firstSeenAt"),
            "lastSeen": node.get("analyzedAt"),  # Using analyzedAt as both first and last seen date
            "exploitAvailable": False,  # Assuming exploitAvailable is not provided in this context
            "parentId": asset.id,
            "parentModule": "assets",
            "dns": "unknown",
            "ipAddress": "unknown",
            "mitigated": False,  # mitigated is not provided in this context
            "port": "",  # there's no direct mapping for Port
            "plugInId": 0,  # there's no direct mapping for Plugin ID
            "scanId": scan_history.id,  # there's no direct mapping for Scan ID
        }

    def create_vulnerability_from_node(
        self, name: str, cve: str, asset: regscale_models.Asset, node: Dict, scan_history: regscale_models.ScanHistory
    ) -> regscale_models.Vulnerability:
        """
        Creates a vulnerability from a node
        :param str name: Name of the vulnerability
        :param str cve: CVE of the vulnerability
        :param regscale_models.Asset asset: Asset object
        :param Dict node: Node from the Wiz API
        :param regscale_models.ScanHistory scan_history: Scan history object
        :returns: Vulnerability object
        :rtype: regscale_models.Vulnerability
        """
        fields = {}
        if self.wiz_vulnerability_type == WizVulnerabilityType.VULNERABILITY:
            fields = self.map_fields_from_node(name, cve, asset, node, scan_history)
        else:
            fields = self.map_fields_from_configuration_node(node, asset, scan_history)

        vulnerability = regscale_models.Vulnerability(**fields)
        return vulnerability

    @staticmethod
    def update_vulnerability(
        vulnerability: regscale_models.Vulnerability,
        name: str,
        cve: str,
        asset: regscale_models.Asset,
        node: Dict,
        scan_history: regscale_models.ScanHistory,
    ):
        """
        Updates the vulnerability from a node
        :param regscale_models.Vulnerability vulnerability: Vulnerability object
        :param str name: Name of the vulnerability
        :param str cve: CVE of the vulnerability
        :param regscale_models.Asset asset: Asset object
        :param Dict node: Node from the Wiz API
        :param regscale_models.ScanHistory scan_history: Scan history object
        """
        try:
            vulnerability.title = name
            vulnerability.description = node.get("description")
            vulnerability.severity = node.get("severity")
            vulnerability.cve = cve
            vulnerability.cvss_v3_base_score = node.get("score")
            vulnerability.first_seen = node.get("firstDetectedAt")
            vulnerability.last_seen = node.get("lastDetectedAt")
            vulnerability.exploit_available = node.get("hasExploit", False)
            vulnerability.parent_id = asset.id
            vulnerability.parent_module = "assets"
            vulnerability.dns = name
            vulnerability.ip_address = "unknown"
            vulnerability.mitigated = False
            vulnerability.port = ""
            vulnerability.plugin_id = 0
            vulnerability.scan_id = scan_history.id
            vulnerability.save()
        except Exception as e:
            logger.info(f"Not able to updating vulnerability: {e}")

    @staticmethod
    def map_issue_to_vulnerability_severity(severity: str) -> str:
        """
        Maps the vulnerability severity to issue severity
        :param str severity: vulnerability severity
        :returns: Issue severity
        :rtype: str
        """
        if severity == "Low":
            return regscale_models.IssueSeverity.Low
        elif severity == "Medium":
            return regscale_models.IssueSeverity.Moderate
        elif severity == "High" or severity == "Critical":
            return regscale_models.IssueSeverity.High
        return regscale_models.IssueSeverity.Low

    @staticmethod
    def convert_first_seen_to_days(first_seen: str) -> int:
        """
        Converts the first seen date to days
        :param str first_seen: First seen date
        :returns: Days
        :rtype: int
        """
        first_seen_date = datetime_obj(first_seen)
        if not first_seen_date:
            return 0
        first_seen_date_naive = first_seen_date.replace(tzinfo=None)
        return (datetime.now() - first_seen_date_naive).days

    def determine_is_poam_from_days_since_last_seen_and_severity(
        self, days_since_last_seen: int, severity: str
    ) -> bool:
        """
        Determines if the issue is a POAM from the days since last seen
        :param int days_since_last_seen: Days since last seen
        :param str severity: Severity of the issue
        :returns: True if the issue is a POAM, False otherwise
        :rtype: bool
        """
        if severity == "Low":
            return days_since_last_seen > self.low_days
        elif severity == "Medium":
            return days_since_last_seen > self.medium_days
        elif severity == "High":
            return days_since_last_seen > self.high_days
        return False

    def check_for_default_control(self) -> Optional[regscale_models.SecurityControl]:
        """
        Check if the default control is present
        :returns: Security control object or None
        :rtype: Optional[regscale_models.SecurityControl]
        """
        controls: List[regscale_models.SecurityControl] = regscale_models.SecurityControl.get_all_by_parent(
            parent_id=self.parent_id, parent_module=self.parent_module
        )
        for control in controls:
            if control.controlId == "CM-6(5)":
                return control
        return None

    def create_issue_from_vulnerability(
        self, vulnerability: regscale_models.Vulnerability, node: Dict, asset: regscale_models.Asset
    ):
        """
        Creates an issue from a vulnerability
        :param regscale_models.Vulnerability vulnerability: Vulnerability object
        :param Dict node: Node from the Wiz API
        :param regscale_models.Asset asset: Asset object
        """
        severity: str = self.map_issue_to_vulnerability_severity(vulnerability.severity)
        days_open = self.convert_first_seen_to_days(vulnerability.firstSeen)
        due_date: str = self.due_date_map.get(severity, date_str(days_from_today(days_open)))
        days_since_first_seen = self.convert_first_seen_to_days(vulnerability.firstSeen)
        is_poam = self.determine_is_poam_from_days_since_last_seen_and_severity(days_since_first_seen, severity)
        status = self.map_status_to_issue_status(node.get("status"))
        issue = regscale_models.Issue(
            parentId=asset.id,
            parentModule=asset.get_module_slug(),
            title=(
                vulnerability.title[:450] if vulnerability and vulnerability.title else "Unknown vulnerbilty"
            ),  # Truncate to 450 characters
            dateCreated=vulnerability.dateCreated,
            dateLastUpdated=vulnerability.dateCreated,
            status=status,
            severityLevel=severity,
            issueOwnerId=self.config.get("userId"),
            createdById=self.config.get("userId"),
            securityPlanId=self.parent_id,
            identification=self.scan_tool,
            dateFirstDetected=vulnerability.firstSeen,
            dateCompleted=self.determine_closed_date(node),
            dueDate=due_date,
            description=vulnerability.description,
            sourceReport=self.scan_tool,
            recommendedActions=vulnerability.description,
            assetIdentifier=get_value(node, "vulnerableAsset.name"),
            remediationDescription=vulnerability.description,
            otherIdentifier=get_value(node, WIZ_ASSET_ID),
            wizId=get_value(node, WIZ_ASSET_ID),
            poamComments=vulnerability.description,
            securityChecks=get_value(node, SOURCE_RULE_ID),
            pluginId=get_value(node, SOURCE_RULE_ID),
            isPoam=is_poam,
            controlId=self.check_for_default_control().controlId if self.check_for_default_control() else None,
        )
        if issue not in self.issues:
            self.issues.append(issue)

    @staticmethod
    def map_status_to_issue_status(status: str) -> str:
        """
        Maps the status to issue status
        :param str status: Status of the vulnerability
        :returns: Issue status
        :rtype: str
        """
        if status.lower() == "open":
            return regscale_models.IssueStatus.Open
        elif status.lower() == "resolved":
            return regscale_models.IssueStatus.Closed
        elif status.lower() == "rejected":
            return regscale_models.IssueStatus.Closed

    @staticmethod
    def determine_closed_date(node: Dict) -> Optional[str]:
        """
        Determines the closed date of the issue
        :param Dict node: Node from the Wiz API
        :returns: Closed date or None
        :rtype: Optional[str]
        """
        if node.get("status").lower() == "resolved" or node.get("status").lower() == "rejected":
            if resolved_date := get_value(node, "resolvedAt") or get_value(node, "statusChangedAt"):
                return resolved_date
            else:
                return get_value(node, "lastDetectedAt") or get_value(node, "statusChangedAt") or get_current_datetime()
        return None

    def update_issue(
        self,
        issue: regscale_models.Issue,
        vulnerability: regscale_models.Vulnerability,
        node: Dict,
        asset: regscale_models.Asset,
    ) -> regscale_models.Issue:
        """
        Updates the issue from a vulnerability
        :param regscale_models.Issue issue: Issue object
        :param regscale_models.Vulnerability vulnerability: Vulnerability object
        :param Dict node: Node from the Wiz API
        :param regscale_models.Asset asset: Asset object
        :returns: Issue object
        :rtype: regscale_models.Issue
        """

        severity: str = self.map_issue_to_vulnerability_severity(vulnerability.severity)
        days_open = self.convert_first_seen_to_days(vulnerability.firstSeen)
        due_date: str = self.due_date_map.get(severity, date_str(days_from_today(days_open)))
        days_since_first_seen = self.convert_first_seen_to_days(vulnerability.firstSeen)
        is_poam = self.determine_is_poam_from_days_since_last_seen_and_severity(days_since_first_seen, severity)
        status = self.map_status_to_issue_status(node.get("status"))
        issue.parentId = asset.id
        issue.parentModule = asset.get_module_slug()
        issue.title = vulnerability.title[:450]  # Truncate to 450 characters
        issue.dateCreated = vulnerability.dateCreated
        issue.status = status
        issue.severityLevel = severity
        issue.issueOwnerId = self.config.get("userId")
        issue.securityPlanId = self.parent_id
        issue.identification = "Wiz"
        issue.dateFirstDetected = vulnerability.firstSeen
        issue.dueDate = due_date
        issue.wizId = get_value(node, WIZ_ASSET_ID)
        issue.pluginId = get_value(node, SOURCE_RULE_ID)
        issue.description = vulnerability.description
        issue.sourceReport = "Wiz"
        issue.recommendedActions = vulnerability.description
        issue.assetIdentifier = get_value(node, "vulnerableAsset.name")
        issue.remediationDescription = vulnerability.description
        issue.otherIdentifier = get_value(node, WIZ_ASSET_ID)
        issue.poamComments = vulnerability.description
        issue.securityChecks = get_value(node, SOURCE_RULE_ID)
        issue.isPoam = is_poam
        issue.dateCompleted = (
            self.determine_closed_date(node) or get_current_datetime()
            if status == regscale_models.IssueStatus.Closed
            else None
        )
        issue.controlId = self.check_for_default_control().id if self.check_for_default_control() else None
        return issue

    def create_scan_history(self):
        """
        Creates scan history record
        """
        self.scan_history = regscale_models.ScanHistory(
            scanningTool=self.scan_tool,
            parentId=self.parent_id,
            parentModule=self.parent_module,
            scanDate=get_current_datetime(),
        ).create()

    def fetch_data(self) -> List[Dict]:
        """
        Fetches data from Wiz
        :returns: List of nodes
        :rtype: List[Dict]
        """
        client = None
        api_endpoint_url = self.app.config.get("wizUrl")
        if token := self.app.config.get("wizAccessToken"):
            client = PaginatedGraphQLClient(
                endpoint=api_endpoint_url,
                query=self.query,
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Authorization": "Bearer " + token,
                },
            )

        logger.info(f"Fetching data from Wiz on topic key for {self.topic_key}")
        # Fetch all results using the client's pagination logic
        data = client.fetch_all(variables=self.variables, topic_key=self.topic_key) if client else []
        return data
