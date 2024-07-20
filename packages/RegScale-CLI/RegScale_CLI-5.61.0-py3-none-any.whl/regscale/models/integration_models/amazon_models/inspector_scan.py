"""
AWS Inspector Scan information
"""

import re
from typing import List, Optional, Tuple, Union

from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime, is_valid_fqdn
from regscale.models.integration_models.amazon_models.inspector import InspectorRecord
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.vulnerability import Vulnerability


class InspectorScan(ContainerScan):
    """
    AWS Inspector Scan
    """

    def __init__(self, **kwargs: dict):
        self.name = "amazon"
        self.vuln_title = "Vulnerability Name"
        self.fmt = "%m/%d/%Y"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.image_name = "Image Name"
        self.ffi = "First Found on Image"
        self.headers = [
            "AWS Account Id",
            "Severity",
            "Fix Available",
            "Finding Type",
            "Title",
            "Description",
            "Finding ARN",
            "First Seen",
            "Last Seen",
            "Last Updated",
            "Resource ID",
            "Container Image Tags",
            "Region",
            "Platform",
            "Resource Tags",
            "Affected Packages",
            "Package Installed Version",
            "Fixed in Version",
            "Package Remediation",
            "File Path",
            "Network Paths",
            "Age (Days)",
            "Remediation",
            "Inspector Score",
            "Inspector Score Vector",
            "Status",
            "Vulnerability Id",
            "Vendor",
            "Vendor Severity",
            "Vendor Advisory",
            "Vendor Advisory Published",
            "NVD CVSS3 Score",
            "NVD CVSS3 Vector",
            "NVD CVSS2 Score",
            "NVD CVSS2 Vector",
            "Vendor CVSS3 Score",
            "Vendor CVSS3 Vector",
            "Vendor CVSS2 Score",
            "Vendor CVSS2 Vector",
            "Resource Type",
            "Ami",
            "Resource Public Ipv4",
            "Resource Private Ipv4",
            "Resource Ipv6",
            "Resource Vpc",
            "Port Range",
            "Epss Score",
            "Exploit Available",
            "Last Exploited At",
            "Lambda Layers",
            "Lambda Package Type",
            "Lambda Last Updated At",
            "Reference Urls",
            "Detector Name",
            "Package Manager",
        ]

        logger = create_logger()
        super().__init__(
            logger=logger,
            headers=self.headers,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            issue_func=self.create_issue,
            **kwargs,
        )

    def file_to_list_of_dicts(self) -> Tuple[dict, List[InspectorRecord]]:
        """
        Override the base class method to handle the AWS Inspector CSV or JSON file format

        :raises ValueError: If the file format is not supported
        :return: Tuple of a header and a list of inspector objects
        :rtype: Tuple[dict, List[InspectorRecord]]
        """
        file_path = self.attributes.file_path
        file_ext = file_path.suffix
        if file_ext == ".csv":
            header, res = InspectorRecord.process_csv(file_path)
            assert header == self.headers
        elif file_ext == ".json":
            header, res = InspectorRecord.process_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        return header, res

    def create_asset(self, dat: Optional[InspectorRecord] = None) -> Asset:
        """
        Create an asset from a row in an Inspector Record

        :param Optional[InspectorRecord] dat: Data row from an Inspector Record, defaults to None
        :return: RegScale Asset object
        :rtype: Asset
        """
        hostname = dat.resource_id
        distro = dat.platform
        # Container Image, Virtual Machine (VM), etc.
        asset_type = self.amazon_type_map().get(dat.resource_type, "Other")

        return Asset(
            **{
                "id": 0,
                "name": hostname,
                "awsIdentifier": hostname,
                "ipAddress": "",
                "isPublic": True,
                "status": "Active (On Network)",
                "assetCategory": "Hardware",
                "bLatestScan": True,
                "bAuthenticatedScan": True,
                "scanningTool": self.name,
                "assetOwnerId": self.config["userId"],
                "assetType": asset_type,
                "fqdn": hostname if is_valid_fqdn(hostname) else None,
                "operatingSystem": Asset.find_os(distro),
                "systemAdministratorId": self.config["userId"],
                "parentId": self.attributes.parent_id,
                "parentModule": self.attributes.parent_module,
            }
        )

    def create_vuln(self, dat: Optional[InspectorRecord] = None) -> Optional[Vulnerability]:
        """
        Create a vulnerability from an Inspector Record

        :param Optional[InspectorRecord] dat: Data row an Inspector Record, defaults to None
        :return: RegScale Vulnerability object or None
        :rtype: Optional[Vulnerability]
        """
        hostname = dat.resource_id
        distro = dat.platform
        cve: str = dat.vulnerability_id
        description: str = dat.description
        title = dat.title if dat.title else dat.description
        regscale_vuln = None
        aws_severity = dat.severity
        severity = self.severity_mapper(aws_severity)
        config = self.attributes.app.config
        asset_match = [asset for asset in self.data["assets"] if asset.name == hostname]
        asset = asset_match[0] if asset_match else None
        if dat and asset_match:
            regscale_vuln = Vulnerability(
                id=0,
                scanId=0,  # set later
                parentId=asset.id,
                parentModule="assets",
                ipAddress="0.0.0.0",  # No ip address available
                lastSeen=dat.last_seen,
                firstSeen=dat.first_seen,
                daysOpen=None,
                dns=hostname,
                mitigated=None,
                operatingSystem=(Asset.find_os(distro) if Asset.find_os(distro) else None),
                severity=severity,
                plugInName=dat.title,
                plugInId=self.convert_cve_string_to_int(dat.vulnerability_id),
                cve=cve,
                vprScore=None,
                tenantsId=0,
                title=(f"{description} on asset {asset.name}"),
                description=description,
                plugInText=title,
                createdById=config["userId"],
                lastUpdatedById=config["userId"],
                dateCreated=get_current_datetime(),
                extra_data={
                    "solution": dat.remediation,
                    "proof": dat.finding_arn,
                },
            )
        return regscale_vuln

    def create_issue(self, dat: Optional[InspectorRecord] = None) -> Issue:
        """
        Create an issue from a row an Inspector Record

        :param Optional[InspectorRecord] dat: Data row from an Inspector Record, defaults to None
        :return: RegScale Issue object
        :rtype: Issue
        """
        hostname = dat.resource_id
        description: str = dat.description
        cve: str = dat.vulnerability_id
        aws_severity = self.severity_mapper(dat.severity).lower()
        severity = Issue.assign_severity(self.severity_mapper(dat.severity).lower())
        kev_due_date = None
        if self.attributes.app.config["issues"][self.name.lower()]["useKev"]:
            kev_due_date = self.lookup_kev(cve)
        iss = Issue(
            isPoam=aws_severity in ["low", "moderate", "high", "critical"],
            title=dat.title,
            description=description,
            identification="Other",
            status="Open",
            severityLevel=severity,
            issueOwnerId=self.attributes.app.config["userId"],
            pluginId=dat.vulnerability_id,
            assetIdentifier=hostname,
            securityPlanId=(self.attributes.parent_id if self.attributes.parent_module == "securityplans" else None),
            recommendedActions=(dat.remediation if dat.remediation else "Upgrade affected package"),
            cve=cve,
            autoApproved="No",
            parentId=self.attributes.parent_id,
            parentModule=self.attributes.parent_module,
            extra_data={"link": dat.vendor_advisory},
            # Set issue due date to the kev date if it is in the kev list
        )
        iss.originalRiskRating = iss.assign_risk_rating(severity)
        # Date not provided, we must use the creation date of the file
        iss.dateFirstDetected = dat.first_seen
        iss.basisForAdjustment = f"{self.name} import"
        iss = self.update_due_dt(iss=iss, kev_due_date=kev_due_date, scanner="amazon", severity=severity)

        return iss

    def amazon_type_map(self) -> dict:
        """
        Map Amazon Inspector resource types to RegScale asset types
        """
        return {
            "AWS_EC2_INSTANCE": "Virtual Machine (VM)",
            "AWS_ECR_CONTAINER_IMAGE": "Container Image",
        }

    def cvss_score(self, dat):
        """
        Get the CVSS score from the data
        """
        if dat.nvd_cvss3_score:
            return dat.nvd_cvss3_score
        if dat.nvd_cvss2_score:
            return dat.vendor_cvss2_score
        if dat.vendor_cvss3_score:
            return dat.vendor_cvss3_score
        if dat.vendor_cvss2_score:
            return dat.vendor_cvss2_score
        return None

    def severity_mapper(self, aws_severity):
        """
        Map AWS Inspector severity to RegScale severity
        """

        severity_map = {"CRITICAL": "high", "HIGH": "high", "LOW": "low", "MEDIUM": "medium", "UNTRIAGED": "high"}
        return severity_map.get(aws_severity, "low")

    def convert_cve_string_to_int(self, s: str) -> int:
        """
        Convert a CVE string to an integer

        :param str s: CVE string
        :return: CVE integer
        :rtype: int
        """
        numbers = re.findall(r"\d+", s)
        # merge numbers to string
        return int("".join(numbers))
