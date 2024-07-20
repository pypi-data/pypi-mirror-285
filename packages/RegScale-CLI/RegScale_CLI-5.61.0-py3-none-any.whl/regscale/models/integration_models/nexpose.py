"""
Nexpose Scan information
"""

from pathlib import Path
from typing import Optional

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import epoch_to_datetime, get_current_datetime, is_valid_fqdn
from regscale.models.app_models.mapping import Mapping
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.regscale_models import Asset, Issue, Vulnerability

VULNERABILITY_TITLE = "Vulnerability Title"
VULNERABILITY_ID = "Vulnerability ID"
CVSS3_SCORE = "CVSSv3 Score"
IP_ADDRESS = "IP Address"


class Nexpose(ContainerScan):
    """
    Prisma/Nexpose Scan information
    """

    def __init__(self, name: str, file_path: str, regscale_ssp_id: int, **kwargs):
        self.name = name
        self.vuln_title = VULNERABILITY_TITLE
        self.vuln_id = VULNERABILITY_ID
        self.cvss3_score = CVSS3_SCORE
        logger = create_logger()
        kwargs, mapping = self.update_mapping(kwargs)
        self.mapping = mapping
        super().__init__(
            logger=logger,
            app=Application(),
            file_path=Path(file_path),
            name=self.name,
            headers=self.mapping.to_header(),
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            issue_func=self.create_issue,
            extra_headers_allowed=True,
            **kwargs,
        )

    def create_issue(self, **kwargs: dict) -> Optional[Issue]:
        """
        Create an issue from a row in the Nexpose csv file

        :param dict **kwargs: The keyword arguments for this function
        :return: RegScale Issue object or None
        :rtype: Optional[Issue]
        """
        dat = kwargs.get("dat")
        cvss3_score = self.mapping.get_value(dat, self.cvss3_score)
        severity = Vulnerability.determine_cvss3_severity_text(cvss3_score) if cvss3_score else "low"
        kev_due_date = None

        if self.attributes.app.config["issues"][self.name.lower()]["useKev"]:
            kev_due_date = self.lookup_kev(self.mapping.get_value(dat, "CVEs"))
        iss = Issue(
            isPoam=severity in ["low", "moderate", "high", "critical"],
            title=self.mapping.get_value(dat, self.vuln_title),
            description=self.mapping.get_value(dat, "Description"),
            status="Open",
            severityLevel=Issue.assign_severity(severity),
            issueOwnerId=self.attributes.app.config["userId"],
            pluginId=self.mapping.get_value(dat, self.vuln_id),
            assetIdentifier=self.mapping.get_value(dat, "Hostname"),
            securityPlanId=(self.attributes.parent_id if self.attributes.parent_module == "securityplans" else None),
            recommendedActions=self.mapping.get_value(dat, "Solution"),
            cve=self.mapping.get_value(dat, "CVEs"),
            autoApproved="No",
            identification="Other",
            parentId=self.attributes.parent_id,
            parentModule=self.attributes.parent_module,
            # Set issue due date to the kev date if it is in the kev list
        )
        iss.originalRiskRating = iss.assign_risk_rating(severity)
        # Date not provided, we must use the creation date of the file
        iss.dateFirstDetected = epoch_to_datetime(self.create_epoch)
        iss.basisForAdjustment = f"{self.name} import"
        iss = self.update_due_dt(iss=iss, kev_due_date=kev_due_date, scanner="prisma", severity=severity)

        return iss

    def create_asset(self, dat: Optional[dict] = None) -> Asset:
        """
        Create an asset from a row in the Nexpose csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale Asset object
        :rtype: Asset
        """
        hostname = self.mapping.get_value(dat, "Hostname")
        return Asset(
            **{
                "id": 0,
                "name": hostname,
                "ipAddress": self.mapping.get_value(dat, IP_ADDRESS),
                "isPublic": True,
                "status": "Active (On Network)",
                "assetCategory": "Hardware",
                "bLatestScan": True,
                "bAuthenticatedScan": True,
                "scanningTool": self.name,
                "assetOwnerId": self.config["userId"],
                "assetType": "Other",
                "fqdn": hostname if is_valid_fqdn(hostname) else None,
                "operatingSystem": Asset.find_os(self.mapping.get_value(dat, "OS")),
                "systemAdministratorId": self.config["userId"],
                "parentId": self.attributes.parent_id,
                "parentModule": self.attributes.parent_module,
            }
        )

    def create_vuln(self, dat: Optional[dict] = None) -> Optional[Vulnerability]:
        """
        Create a vulnerability from a row in the Prisma/Nexpose csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale Vulnerability object or None
        :rtype: Optional[Vulnerability]
        """
        regscale_vuln = None
        cvss3_score = self.mapping.get_value(dat, self.cvss3_score)
        hostname: str = self.mapping.get_value(dat, "Hostname")
        os: str = self.mapping.get_value(dat, "OS")
        description: str = self.mapping.get_value(dat, "Description")
        severity = Vulnerability.determine_cvss3_severity_text(float(cvss3_score)) if cvss3_score else "low"
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
                lastSeen=get_current_datetime(),
                firstSeen=epoch_to_datetime(self.create_epoch),
                daysOpen=None,
                dns=hostname,
                mitigated=None,
                operatingSystem=(Asset.find_os(os) if Asset.find_os(os) else None),
                severity=severity,
                plugInName=self.mapping.get_value(dat, self.vuln_title),
                plugInId=self.mapping.get_value(dat, self.vuln_id),
                cve=self.mapping.get_value(dat, "CVEs"),
                vprScore=None,
                tenantsId=0,
                title=description[:255],
                description=description,
                plugInText=self.mapping.get_value(dat, self.vuln_title),
                createdById=config["userId"],
                lastUpdatedById=config["userId"],
                dateCreated=get_current_datetime(),
                extra_data={
                    "solution": self.mapping.get_value(dat, "Solution"),
                    "proof": self.mapping.get_value(dat, "Proof"),
                },
            )
        return regscale_vuln

    @staticmethod
    def default_mapping() -> Mapping:
        """
        Default mapping for the Nexpose csv file if one is not provided
        """
        mapping_dict = {
            IP_ADDRESS: IP_ADDRESS,
            "Hostname": "Hostname",
            "OS": "OS",
            VULNERABILITY_TITLE: VULNERABILITY_TITLE,
            VULNERABILITY_ID: VULNERABILITY_ID,
            "CVSSv2 Score": "CVSSv2 Score",
            CVSS3_SCORE: CVSS3_SCORE,
            "Description": "Description",
            "Proof": "Proof",
            "Solution": "Solution",
            "CVEs": "CVEs",
        }

        return Mapping(mapping=mapping_dict)
