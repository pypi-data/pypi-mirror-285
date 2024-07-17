"""
Qualys Scan information
"""

import concurrent

# pylint: disable=C0415
import csv
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, TypeVar, Union, Optional

from dateutil.parser import parse

from regscale.core.app import create_logger
from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    check_file_path,
    convert_datetime_to_regscale_string,
    create_progress_object,
    epoch_to_datetime,
    error_and_exit,
    get_current_datetime,
    is_valid_fqdn,
)
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models import Issue
from regscale.models.regscale_models import Asset, File, Scan, Vulnerability
from regscale.models.regscale_models.checklist import ChecklistStatus

T = TypeVar("T")


class Qualys(ContainerScan):
    """Qualys Scan information"""

    title = "Qualys Scanner Export Integration"
    asset_identifier_field = "fqdn"

    def __init__(self, name: str, **kwargs):
        self.name = name
        # Override for coalfire
        self.vuln_title = "PROBLEM_TITLE"
        self.fmt = "%Y-%m-%d"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.headers = [
            "IP",
            "DNS",
            "NetBIOS",
            "QG Host ID",
            "IP Interfaces",
            "Tracking Method",
            "OS",
            "IP Status",
            "QID",
            "Title",
            "Vuln Status",
            "Type",
            "Severity",
            "Port",
            "Protocol",
            "FQDN",
            "SSL",
            "First Detected",
            "Last Detected",
            "Times Detected",
            "Date Last Fixed",
            "First Reopened",
            "Last Reopened",
            "Times Reopened",
            "CVE ID",
            "Vendor Reference",
            "Bugtraq ID",
            "CVSS3.1",
            "CVSS3.1 Base",
            "CVSS3.1 Temporal",
            "Threat",
            "Impact",
            "Solution",
            "Exploitability",
            "Associated Malware",
            "Results",
            "PCI Vuln",
            "Ticket State",
            "Instance",
            "Category",
            "Associated Tags",
            "EC2 Instance ID",
            "Public Hostname",
            "Image ID",
            "VPC ID",
            "Instance State",
            "Private Hostname",
            "Instance Type",
            "Account ID",
            "Region Code",
            "Subnet ID",
            "QDS",
            "ARS",
            "ACS",
            "TruRisk Score",
        ]
        logger = create_logger()
        app = Application()
        super().__init__(
            logger=logger,
            app=app,
            name=self.name,
            headers=self.headers,
            header_line_number=129,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            issue_func=self.create_issue,
            **kwargs,
        )
        # header is line# 11
        # start self.file_data from line #12

    def create_issue(self, dat: Optional[dict] = None) -> Optional[Issue]:
        """
        Create an issue from a row in the Qualys file

        :param Optional[dict] dat: Data row from CSV file
        :return: RegScale Issue object or None
        :rtype: Optional[Issue]
        """
        from regscale.integrations.commercial.qualys import map_qualys_severity_to_regscale

        severity = dat["Severity"]
        regscale_severity = map_qualys_severity_to_regscale(int(severity))[1]
        status = "Open" if regscale_severity in ["moderate", "high", "critical"] else "Closed"
        name = dat["Title"]
        description = dat["Exploitability"]
        cve = dat["CVE ID"]
        solution = dat["Solution"]
        # create an issue
        if self.attributes.app.config["issues"][self.name.lower()]["useKev"]:
            kev_due_date = self.lookup_kev(cve)
        iss = Issue(
            isPoam=severity in ["low", "moderate", "high", "critical"],
            title=f"CVE: {cve} Associated with asset {name}",
            description=description,
            identification="Other",
            status=status,
            severityLevel=regscale_severity,
            issueOwnerId=self.attributes.app.config["userId"],
            pluginId=cve,
            assetIdentifier=name,
            securityPlanId=(self.attributes.parent_id if self.attributes.parent_module == "securityplans" else None),
            recommendedActions=(solution if solution else "Upgrade affected package"),
            cve=cve,
            dateCompleted=convert_datetime_to_regscale_string(self.scan_date) if status == "Closed" else None,
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

    def create_asset(self, dat: Optional[dict] = None) -> Optional[Asset]:
        """
        Create an asset from a row in the Qualys file

        :param Optional[dict] dat: Data row from CSV file
        :return: RegScale Issue object or None
        :rtype: Optional[Asset]
        """
        return Asset(
            **{
                "id": 0,
                "name": dat["DNS"],
                "ipAddress": dat["IP"],
                "isPublic": True,
                "status": "Active (On Network)",
                "assetCategory": "Hardware",
                "qualysId": dat["QG Host ID"],  # UUID from Nessus HostProperties tag
                "bLatestScan": True,
                "bAuthenticatedScan": True,
                "scanningTool": "Qualys",
                "assetOwnerId": self.attributes.app.config["userId"],
                "netBIOS": dat["NetBIOS"],
                "assetType": "Other",
                "fqdn": dat["FQDN"],
                "operatingSystem": Asset.find_os(dat["OS"]),
                "operatingSystemVersion": dat["OS"],
                "systemAdministratorId": self.attributes.app.config["userId"],
                "parentId": self.attributes.parent_id,
                "parentModule": self.attributes.parent_module,
            }
        )

    def create_vuln(self, dat: Optional[dict] = None) -> None:
        """
        Create a vuln from a row in the Qualys file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :rtype: None
        """
        pass

    @staticmethod
    def determine_cvss_severity(dat: dict) -> str:
        """
        Determine the CVSS severity of the vulnerability

        :param dict dat: Data row from CSV file
        :return: A severity derived from the CVSS scores
        :rtype: str
        """
        precedence_order = [
            "NVD CVSS v3 Severity",
            "NVD CVSS v2 Severity",
            "Vendor CVSS v3 Severity",
            "Vendor CVSS v2 Severity",
        ]
        severity = "info"
        for key in precedence_order:
            if dat.get(key):
                severity = dat[key].lower()
                break
        # remap crits to highs
        if severity == "critical":
            severity = "high"
        return severity
