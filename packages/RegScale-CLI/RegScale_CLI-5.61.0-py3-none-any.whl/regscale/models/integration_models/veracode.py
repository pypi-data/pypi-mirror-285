from pathlib import Path
from typing import List, Optional

from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import epoch_to_datetime, get_current_datetime
from regscale.models import Asset, Issue, Vulnerability
from regscale.models.integration_models.container_scan import ContainerScan

APP_NAME = "@app_name"
VERSION = "@version"
ACCOUNT_ID = "@account_id"


class Veracode(ContainerScan):
    def __init__(self, name: str, file_path: str, **kwargs):
        self.name = name
        self.file_path = file_path
        logger = create_logger()
        self.vuln_title = "PROBLEM_TITLE"
        self.fmt = "%Y-%m-%d"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.headers = [
            "ISSUE_SEVERITY",
            "PRIORITY_SCORE",
            "PROBLEM_TITLE",
            "CVE",
            "CWE",
            "PROJECT_NAME",
            "PROJECT_URL",
            "EXPLOIT_MATURITY",
            "AUTOFIXABLE",
            "FIRST_INTRODUCED",
            "PRODUCT_NAME",
            "ISSUE_URL",
            "ISSUE_STATUS_INDICATOR",
            "ISSUE_TYPE",
        ]
        super().__init__(
            logger=logger,
            file_path=Path(file_path),
            name=self.name,
            headers=self.headers,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            issue_func=self.create_issue,
            file_type=".xlsx",
            extra_headers_allowed=False,
            **kwargs,
        )

    def create_asset(self, dat: Optional[dict] = None) -> List[Asset]:
        """
        Create a RegScale asset from an asset  in the Veracode export file

        :param Optional[dict] dat: The data from the Veracode export file
        :return: List of RegScale Asset objects
        :rtype: List[Asset]
        """
        version = None
        # Veracode is a Web Application Security Scanner, so these will be software assets, scanning a single web application
        if "detailedreport" in dat.keys():
            name = dat.get("detailedreport", {}).get(APP_NAME, "")
            account_id = dat.get("detailedreport", {}).get(ACCOUNT_ID, "")
            version = dat.get("detailedreport", {}).get(VERSION, "")
        else:
            name = dat.get("Source", "")
            account_id = str(dat.get("ID", ""))
        asset = Asset(
            **{
                "id": 0,
                "name": name,
                "otherTrackingNumber": account_id,
                "ipAddress": "0.0.0.0",
                "isPublic": True,
                "status": "Active (On Network)",
                "assetCategory": "Software",
                "bLatestScan": True,
                "bAuthenticatedScan": True,
                "scanningTool": self.name,
                "assetOwnerId": self.config["userId"],
                "assetType": "Other",
                "softwareVendor": "Veracode",
                "softwareName": name,
                "softwareVersion": version,
                "systemAdministratorId": self.config["userId"],
                "parentId": self.attributes.parent_id,
                "parentModule": self.attributes.parent_module,
            }
        )
        return [asset]

    def create_issue(self, dat: dict = None) -> List[Issue]:
        """
        Create a RegScale issue from a vulnerability in the Veracode export file

        :param dict dat: The data from the Veracode export file
        :return: List of RegScale Issue
        :rtype: List[Issue]
        """
        scan_issues = []
        severity_data = None
        cves = ""
        import_type = "xml" if "detailedreport" in dat.keys() else "csv"
        # Veracode is a Web Application Security Scanner, so these will be software assets, scanning a single web application
        if import_type == "xml":
            name = dat.get("detailedreport", {}).get(APP_NAME, "")
            severity_data = self.severity_info(dat.get("detailedreport", {}).get("severity", []))
            cves = dat.get("detailedreport", {}).get("cve", "")
            severity = severity_data[0] if severity_data else "low"
            cwes = severity_data[1].get("cwe", [])  # Multiple cwes per asset in official XML
        else:
            name = dat.get("Source", "")
            severity = dat.get("Sev").lower()
            cwes = [dat.get("CWE ID & Name", [])]  # Coalfire should flatten data for asset -> cwes

        if not severity_data and import_type == "xml":
            return scan_issues
        kev_due_date = None
        if self.attributes.app.config["issues"][self.name.lower()]["useKev"]:
            kev_due_date = self.lookup_kev(cves)
        for vuln in cwes:
            iss = self.build_issue(
                name=name,
                vuln=vuln,
                severity=severity,
                severity_data=severity_data,
                kev_due_date=kev_due_date,
                cves=cves,
                is_csv=import_type == "csv",
            )
            scan_issues.append(iss)
        return scan_issues

    def build_issue(
        self, name: str, vuln: dict, severity: str, severity_data: dict, kev_due_date: str, cves: str, is_csv=False
    ):
        iss = Issue(
            isPoam=severity in ["low", "moderate", "high", "critical"],
            title=vuln.get("@cwename") if not is_csv else vuln,
            description=vuln.get("description", {}).get("text", {}).get("@text", "") if not is_csv else "",
            status="Open",
            severityLevel=Issue.assign_severity(severity),
            issueOwnerId=self.attributes.app.config["userId"],
            pluginId=severity_data[1].get("@categoryid") if not is_csv and severity_data else None,
            assetIdentifier=name,
            securityPlanId=self.attributes.parent_id if self.attributes.parent_module == "securityplans" else None,
            recommendedActions=(
                severity_data[1].get("recommendations", {}).get("para", {}).get("@text", "")
                if not is_csv and severity_data
                else "Upgrade affected package"
            ),
            cve=cves,
            autoApproved="No",
            identification="Other",
            parentId=self.attributes.parent_id,
            parentModule=self.attributes.parent_module,
        )
        iss.originalRiskRating = Issue.assign_risk_rating(severity)
        iss.dateFirstDetected = epoch_to_datetime(self.create_epoch)
        iss.basisForAdjustment = f"{self.name} import"
        issue = self.update_due_dt(iss=iss, kev_due_date=kev_due_date, scanner="veracode", severity=severity)
        return issue

    def create_vuln(self, dat: Optional[dict] = None) -> List[Vulnerability]:
        """
        Create a RegScale vulnerability from a vulnerability in the Veracode export file

        :param Optional[dict]  dat: The data from the Veracode export file
        :return: List of RegScale Vulnerability objects
        :rtype: List[Vulnerability]
        """
        import_type = "xml" if isinstance(dat, str) else "csv"
        # Veracode is a Web Application Security Scanner, so these will be software assets, scanning a single web application
        if import_type == "xml":
            name = self.file_data.get("detailedreport", {}).get(APP_NAME, "")
            all_sev_data = self.file_data.get("detailedreport", {}).get("severity", [])
            severity = self.severity_info(all_sev_data)[0] if all_sev_data else "low"
            severity_data = self.severity_info(all_sev_data)
            cwes = [
                c["@cweid"] + " " + c["@cwename"] for c in severity_data[1].get("cwe", [])
            ]  # Multiple cwes per asset in official XML
        else:
            name = dat.get("Source", "")
            severity = dat.get("Sev").lower()
            cwes = [dat.get("CWE ID & Name", [])]  # Coalfire should flatten data for asset -> cwes

        return self.process_csv_vulns(name, cwes, severity)

    def process_csv_vulns(self, hostname: str, cwes: List[str], severity: str) -> List[Vulnerability]:
        """
        Process the CSV findings from the ECR scan

        :param str hostname: The hostname
        :param List[str] cwes: The CWEs
        :param str severity: The severity
        :return: A list of vulnerabilities
        :rtype: List[Vulnerability]
        """
        vulns = []
        for cwe in cwes:
            severity = self.determine_severity(severity)
            if asset := self.get_asset(hostname):
                vuln = self.create_vulnerability_object(asset, hostname, cwe, severity, "")
                vulns.append(vuln)
        return vulns

    def create_vulnerability_object(
        self, asset: Asset, hostname: str, cwe: str, severity: str, description: str
    ) -> Vulnerability:
        """
        Create a vulnerability from a row in the Veracode file

        :param Asset asset: The asset
        :param str hostname: The hostname
        :param str cwe: The CWE
        :param str severity: The severity
        :param str description: The description
        :return: The vulnerability
        :rtype: Vulnerability
        """
        config = self.attributes.app.config

        return Vulnerability(  # type: ignore
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
            plugInName=cwe,
            cve="",
            tenantsId=0,
            title=f"{cwe} on asset {asset.name}",
            description=cwe,
            plugInText=description,
            createdById=config["userId"],
            lastUpdatedById=config["userId"],
            dateCreated=get_current_datetime(),
        )

    def get_asset(self, hostname: str):
        asset_match = [asset for asset in self.data["assets"] if asset.name == hostname]
        return asset_match[0] if asset_match else None

    def severity_info(self, severity_list: list) -> Optional[tuple]:
        """
        Get the severity level and category of the vulnerability

        :param list severity_list: List of severity levels
        :return: Severity level and category
        :rtype: Optional[tuple]
        """
        hit = [sev for sev in severity_list if sev.get("category")]
        if hit:
            return (self.hit_mapping().get(hit[0].get("@level"), "low"), hit[0].get("category"))
        return None

    def hit_mapping(self) -> dict:
        """
        Mapping of severity levels

        :return: Mapping of severity levels
        :rtype: dict
        """
        return {
            "5": "critical",
            "4": "high",
            "3": "moderate",
            "2": "low",
            "1": "low",
            "0": "info",
        }
