"""
ECR Scan information
"""

import json
from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import convert_datetime_to_regscale_string, get_current_datetime, is_valid_fqdn
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.vulnerability import Vulnerability


class ECR(ContainerScan):
    """ECR Scan information"""

    def __init__(self, name: str, app: Application, **kwargs):
        self.name = name
        self.vuln_title = "name"
        self.fmt = "%m/%d/%y"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.image_name = "Name"
        self.headers = [
            "Name",
            "Tag",
            "Severity",
            "CVE",
            "Description",
            "Package Name",
            "Package Version",
            "CVSS2 Score",
            "CVSS2 Vector",
            "URI",
        ]
        self.raw_dict = {}
        file_path = Path(kwargs.get("file_path")) if kwargs.get("file_path") else Path()
        parent_id = kwargs.get("parent_id")
        parent_module = kwargs.get("parent_module")
        logger = create_logger()
        super().__init__(
            logger=logger,
            app=app,
            file_path=file_path,
            name=self.name.lower(),
            headers=self.headers,
            parent_id=parent_id,
            parent_module=parent_module,
            file_type=kwargs.get("file_type", file_path.suffix).replace(".", ""),
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            issue_func=self.create_issue,
        )

    def file_to_list_of_dicts(
        self,
    ) -> tuple[Optional[Sequence[str]], Union[dict, list[Any]]]:
        """
        Override the base method: Converts a json or csv file to a list of dictionaries

        :raises AssertionError: If the headers in the csv/xlsx file do not match the expected headers
        :return: Tuple of header and data from csv file
        :rtype: tuple[Optional[Sequence[str]], Union[dict, list[Any]]]
        """
        header: Optional[Sequence[str]] = []
        data: dict = {}
        with open(self.attributes.file_path, encoding="utf-8") as file:
            if file.name.endswith(".csv"):
                data, header = self.convert_csv_to_dict(file)
            elif file.name.endswith(".json"):
                try:
                    # Filter possible null values
                    self.raw_dict = json.load(file)
                    if not isinstance(self.raw_dict, dict):
                        raise AssertionError("Invalid JSON file")
                    data = self.raw_dict.get("imageScanFindings", {}).get("findings", [])
                except json.JSONDecodeError:
                    raise AssertionError("Invalid JSON file")
            else:
                raise AssertionError("Unsupported file type")
        return header, data

    def create_issue(self, **kwargs: dict) -> Optional[List[Issue]]:
        """
        Create an issue from a row in the ECR file

        :param dict **kwargs: The keyword arguments for this function
        :return: RegScale Issue object or None
        :rtype: Optional[List[Issue]]
        """
        dat = kwargs.get("dat", {})
        if self.raw_dict:
            return self.process_json_issues()

        else:
            return self.process_csv_issue(dat)

    def process_json_issues(self) -> List[Issue]:
        """
        Process the JSON findings from the ECR scan

        :return: The list of issues
        :rtype: List[Issue]
        """
        issues: List[Issue] = []
        repository_name = self.raw_dict.get("repositoryName", "")
        image_id_data = self.raw_dict.get("imageId", {}).get("imageDigest", "").split(":")
        if len(image_id_data) > 1:
            image_id = image_id_data[1]
        else:
            image_id = image_id_data[0]
        name = f"{repository_name}:{image_id}"
        for finding in self.raw_dict.get("imageScanFindings", {}).get("findings", []):
            severity = self.determine_severity(finding.get("severity", ""))  # "" will return info
            if severity == "info":
                return []
            iss = super().create_issue(
                dat=finding,
                severity=severity,
                first_detected_dt=self.scan_date,
                description=finding.get("uri", ""),
                asset_identifier=name,
            )
            if iss:
                issues.append(iss)
        return issues

    def process_csv_issue(self, dat: dict) -> Issue:
        """
        Process the CSV findings from the ECR scan

        :param dict dat: The data from the ECR scan
        :return: The issue
        :rtype Issue
        """
        cve = dat.get("CVE")
        fix_status = dat.get("Fix Status")
        name = dat.get("Name") or dat.get("name")
        ecr_severity = dat.get("Severity")
        description = dat.get("uri", "")
        severity = self.determine_severity(ecr_severity)
        # create an issue
        if self.attributes.app.config["issues"][self.name.lower()]["useKev"]:
            kev_due_date = self.lookup_kev(cve)
        iss = Issue(
            isPoam=severity in ["low", "moderate", "high", "critical"],
            title=f"CVE: {cve} Associated with asset {name}",
            description=description,
            identification="Other",
            status="Open",
            severityLevel=Issue.assign_severity(dat.get("Severity", severity)),
            issueOwnerId=self.attributes.app.config["userId"],
            pluginId=cve,
            assetIdentifier=name,
            securityPlanId=(self.attributes.parent_id if self.attributes.parent_module == "securityplans" else None),
            recommendedActions=(fix_status if fix_status else "Upgrade affected package"),
            cve=cve,
            autoApproved="No",
            parentId=self.attributes.parent_id,
            parentModule=self.attributes.parent_module,
            extra_data={"link": description} if description else {},
            originalRiskRating=Issue.assign_risk_rating(severity),
            dateFirstDetected=convert_datetime_to_regscale_string(self.scan_date),
            basisForAdjustment=f"{self.name} import",
            # Set issue due date to the kev date if it is in the kev list
        )
        iss = self.update_due_dt(iss=iss, kev_due_date=kev_due_date, scanner="ecr", severity=severity)
        return iss

    def create_asset(self, dat: Optional[dict] = None) -> Asset:
        """
        Create an asset from a row in the ECR file

        :param Optional[dict] dat: Data row from file, defaults to None
        :return: RegScale Asset object
        :rtype: Asset
        """
        name = dat.get("Name") or dat.get("name")
        repository_name = dat.get("repositoryName", self.raw_dict.get("repositoryName", ""))
        if repository_name:
            if (image_id_data := self.raw_dict.get("imageId", {}).get("imageDigest", "").split(":")) and len(
                image_id_data
            ) > 1:
                image_id = image_id_data[1]
            else:
                image_id = image_id_data[0]
            name = f"{repository_name}:{image_id}"

        # Check if string has a forward slash
        return Asset(
            **{
                "id": 0,
                "name": name,
                "description": "Container Image" if "/" in name else "",
                "operatingSystem": "Linux",
                "operatingSystemVersion": "",
                "ipAddress": "0.0.0.0",
                "isPublic": True,
                "status": "Active (On Network)",
                "assetCategory": "Software",
                "bLatestScan": True,
                "bAuthenticatedScan": True,
                "scanningTool": self.name,
                "assetOwnerId": self.config["userId"],
                "assetType": "Other",
                "fqdn": name if is_valid_fqdn(name) else None,
                "systemAdministratorId": self.config["userId"],
                "parentId": self.attributes.parent_id,
                "parentModule": self.attributes.parent_module,
            }
        )

    def create_vuln(self, dat: Optional[dict] = None) -> Union[Vulnerability, List[Vulnerability], None]:
        """
        Create a vulnerability from a row in the ECR csv file

        :param Optional[dict] dat: Data row from file, defaults to None
        :return: RegScale Vulnerability object, a list of RegScale Vulnerability objects or None
        :rtype: Union[Vulnerability, List[Vulnerability], None]
        """
        hostname = dat.get("Name") or dat.get("name")
        repository_name = dat.get("repositoryName", self.raw_dict.get("repositoryName", ""))
        if repository_name:
            image_id_data = self.raw_dict.get("imageId", {}).get("imageDigest", "").split(":")
            if len(image_id_data) > 1:
                image_id = image_id_data[1]
            else:
                image_id = image_id_data[0]
            hostname = f"{repository_name}:{image_id}"
        image_scan_findings = dat.get("imageScanFindings")
        if image_scan_findings:
            vulns = self.process_json_vulns(dat, hostname)
        else:
            single_vuln = self.process_csv_vulns(dat, hostname)
            if single_vuln:
                return single_vuln
        return vulns

    def get_asset(self, hostname: str):
        asset_match = [asset for asset in self.data["assets"] if asset.name == hostname]
        return asset_match[0] if asset_match else None

    def create_vulnerability_object(
        self, asset: Asset, hostname: str, cve: str, severity: str, description: str
    ) -> Vulnerability:
        """
        Create a vulnerability from a row in the ECR file

        :param Asset asset: The asset
        :param str hostname: The hostname
        :param str cve: The CVE
        :param str severity: The severity
        :param str description: The description
        :return: The vulnerability
        :rtype: Vulnerability
        """
        config = self.attributes.app.config

        return Vulnerability(
            id=0,
            scanId=0,
            parentId=asset.id,
            parentModule="assets",
            ipAddress="0.0.0.0",
            lastSeen=get_current_datetime(),  # No timestamp on ECR
            # firstSeen=get_current_datetime(), # No timestamp on ECR
            daysOpen=None,
            dns=hostname,
            mitigated=None,
            operatingSystem=asset.operatingSystem,
            severity=severity,
            plugInName=cve,
            cve=cve,
            tenantsId=0,
            title=f"{cve} on asset {asset.name}",
            description=cve,
            plugInText=description,
            createdById=config["userId"],
            lastUpdatedById=config["userId"],
            dateCreated=get_current_datetime(),
        )

    def process_csv_vulns(self, dat: dict, hostname: str) -> Optional[Vulnerability]:
        """
        Process the CSV findings from the ECR scan

        :param dict dat: The data from the ECR scan
        :param str hostname: The hostname
        :return: The vulnerability or None
        :rtype: Optional[Vulnerability]

        """
        cve = dat.get("CVE", "")
        severity = self.determine_severity(dat.get("Severity", "Info"))
        if asset := self.get_asset(hostname):
            return self.create_vulnerability_object(asset, hostname, cve, severity, dat.get("uri", ""))
        return None

    def process_json_vulns(self, dat: dict, hostname: str) -> List[Vulnerability]:
        """
        Process the JSON findings from the ECR scan

        :param dict dat: The data from the ECR scan
        :param str hostname: The hostname
        :return: The list of vulnerabilities
        :rtype: List[Vulnerability]
        """
        vulns: List[Vulnerability] = []
        findings = dat.get("imageScanFindings", {}).get("findings")
        if findings:
            for finding in findings:
                cve = finding.get("name")
                severity = self.determine_severity(finding["severity"])
                asset = self.get_asset(hostname)
                if asset:
                    vuln = self.create_vulnerability_object(asset, hostname, cve, severity, finding.get("uri", ""))
                    vulns.append(vuln)
        return vulns
