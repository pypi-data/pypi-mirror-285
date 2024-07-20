""" Container Scan Abstract """

import ast
import csv
import json
import re
import shutil
from abc import ABC, abstractmethod
from collections import namedtuple
from datetime import datetime, timedelta
from typing import Any, Callable, List, Optional, Sequence, TextIO, Union

import click
import requests
import xmltodict
from openpyxl.reader.excel import load_workbook

from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import (
    check_file_path,
    convert_datetime_to_regscale_string,
    create_progress_object,
    creation_date,
    error_and_exit,
    get_current_datetime,
)
from regscale.core.app.utils.report_utils import ReportGenerator
from regscale.integrations.public.cisa import pull_cisa_kev
from regscale.models.app_models.mapping import Mapping
from regscale.models.regscale_models import Asset, File, Issue, ScanHistory, Vulnerability

DT_FORMAT = "%Y-%m-%d"


class ContainerScan(ABC):
    """
    Abstract class for container scan integration

    :param dict **kwargs: Keyword arguments
    """

    def __init__(self, **kwargs: dict):
        self.field_names = [
            "logger",
            "headers",
            "file_type",
            "app",
            "file_path",
            "name",
            "parent_id",
            "parent_module",
            "scan_date",
            "asset_func",
            "vuln_func",
            "issue_func",
            "extra_headers_allowed",
            "mapping",
            "ignore_validation",
            "header_line_number",
        ]
        _attributes = namedtuple(
            "Attributes",
            self.field_names,
            defaults=[None] * len(self.field_names),
        )
        self.attributes = _attributes(**kwargs)
        self.file_type = kwargs.get("file_type", ".csv")
        self.extra_headers_allowed = kwargs.get("extra_headers_allowed", False)
        self.scan_date = kwargs.get("scan_date", datetime.now()).date()
        self.attributes.logger.info("Processing %s...", self.attributes.file_path.name)
        self.formatted_headers = None
        self.config = self.attributes.app.config
        self.cisa_kev = pull_cisa_kev()
        self.header, self.file_data = self.file_to_list_of_dicts()
        self.data = {
            "assets": [],
            "issues": [],
            "scans": [],
            "vulns": [],
        }
        self.create_epoch = str(int(creation_date(self.attributes.file_path)))
        self.create_assets(kwargs["asset_func"])  # Pass in the function to create an asset
        self.create_vulns(kwargs["vuln_func"])  # Pass in the function to create a vuln
        self.create_scan()
        self.create_issues(kwargs["issue_func"])  # Pass in the function to create an issue
        self.clean_up()

    def file_to_list_of_dicts(self) -> tuple[Optional[Sequence[str]], list[Any]]:
        """
        Converts a csv file to a list of dictionaries

        :raises AssertionError: If the headers in the csv/xlsx file do not match the expected headers
        :return: Tuple of header and data from csv file
        :rtype: tuple[Optional[Sequence[str]], list[Any]]
        """
        header = []
        data = []
        start_line_number = 0 if not self.attributes.header_line_number else self.attributes.header_line_number
        with open(self.attributes.file_path, encoding="utf-8") as file:
            # Skip lines until the start line is reached
            for _ in range(start_line_number):
                next(file)
            if file.name.endswith(".csv"):
                data, header = self.convert_csv_to_dict(file)
            elif file.name.endswith(".xlsx"):
                header, data = self.convert_xlsx_to_dict(file)
            elif file.name.endswith(".json"):
                try:
                    # Filter possible null values
                    file_data = json.load(file)
                    if isinstance(file_data, dict):
                        data = file_data
                    if isinstance(file_data, list):
                        data = [dat for dat in file_data if dat]
                except json.JSONDecodeError:
                    raise AssertionError("Invalid JSON file")
            elif file.name.endswith(".xml"):
                data = self.convert_xml_to_dict(file)
            else:
                raise AssertionError("Unsupported file type")
        return header, data

    def validate_headers(self, header: list) -> None:
        """
        Validate the headers in the csv file

        :param list header: The headers from the csv file
        :raises AssertionError: If the headers in the csv file do not match the expected headers
        """
        ignore_validation = self.attributes.ignore_validation
        if header != self.attributes.headers and not ignore_validation:
            # Strict validation
            raise AssertionError(
                f"The headers in the csv file do not match the expected headers\nEXPECTED:{self.attributes.headers}\nACTUAL:{header}"
            )
        if ignore_validation and not all(item in header for item in self.mapping.expected_field_names):
            raise AssertionError(
                "The expected field names from the default mapping OR user provided mapping are not in the file header"
                "\nMINIMUM REQUIRED HEADERS:{self.mapping.expected_field_names}\nACTUAL HEADERS:{header}"
            )

    def handle_extra_headers(self, header: list) -> None:
        """
        Handle extra headers in the csv file

        :param list header: The headers from the csv file
        :raises AssertionError: If the headers in the csv file do not contain the required headers
        """
        extra_headers = [column for column in header if column not in self.attributes.headers]
        required_headers = [column for column in header if column in self.attributes.headers]

        if not all(item in self.attributes.headers for item in required_headers):
            raise AssertionError(
                "The headers in the csv file do not contain the required headers "
                + f"headers, is this a valid {self.attributes.name} {self.file_type} file?"
            )

        if extra_headers:
            self.attributes.logger.warning(
                "The following extra columns were found and will be ignored: %s",
                ", ".join(extra_headers),
            )

    def convert_csv_to_dict(self, file: TextIO) -> tuple:
        """
        Converts a csv file to a list of dictionaries

        :param TextIO file: The csv file to convert
        :return: Tuple of header and data from csv file
        :rtype: tuple
        """
        reader = csv.DictReader(file)
        header = list(reader.fieldnames)

        self.validate_headers(header=header)

        if self.extra_headers_allowed:
            self.handle_extra_headers(header=header)

        data = list(reader)
        return data, header

    def convert_xlsx_to_dict(self, file: TextIO) -> tuple:
        """
        Converts a xlsx file to a list of dictionaries

        :param TextIO file: The xlsx file to convert
        :return: Tuple of header and data from xlsx file
        :rtype: tuple
        """
        # Load the workbook
        workbook = load_workbook(filename=file.name)

        # Select the first sheet
        sheet = workbook.active

        # Get the data from the sheet
        data = list(sheet.values)

        # Get the header from the first row
        header = list(data[0])

        # Get the rest of the data
        data = data[1:]

        # Convert the data to a dictionary
        data_dict = [dict(zip(header, row)) for row in data]

        # Loop through the data and convert any string lists to lists
        for dat in data_dict:
            for key, val in dat.items():
                if isinstance(val, str) and val.startswith("["):
                    try:
                        dat[key] = ast.literal_eval(dat[key])
                    except SyntaxError as rex:
                        # Object is probably not a list, so just leave it as a string
                        self.attributes.app.logger.debug("SyntaxError: %s", rex)
        return header, data_dict

    def count_vuln_by_severity(self, severity: str, asset_id: int) -> int:
        """
        Count the number of vulnerabilities by the provided severity

        :param str severity: The severity to count
        :param int asset_id: The asset id to match the vulnerability's parentId
        :return: The number of vulnerabilities
        :rtype: int
        """
        return len([vuln for vuln in self.data["vulns"] if vuln.parentId == asset_id and vuln.severity == severity])

    def create_scan(self) -> None:
        """
        Create scans in RegScale from file

        :rtype: None
        """
        insert_vulns = []
        scanned_assets = [
            asset for asset in self.data["assets"] if asset.id in {vuln.parentId for vuln in self.data["vulns"]}
        ]

        with create_progress_object() as scan_progress:
            scan_task = scan_progress.add_task(
                f"Creating a scan record  for {len(scanned_assets)} asset(s) in RegScale...",
                total=len(scanned_assets),
            )
            for asset in scanned_assets:
                count_low = self.count_vuln_by_severity("low", asset.id)
                count_medium = self.count_vuln_by_severity("moderate", asset.id)
                count_high = self.count_vuln_by_severity("high", asset.id)
                count_critical = self.count_vuln_by_severity("critical", asset.id)
                # Create a scan
                scan = ScanHistory(
                    **{
                        "id": 0,
                        "scanningTool": self.name,
                        "scanDate": str(self.scan_date),
                        "scannedIPs": len([ass for ass in scanned_assets if ass.ipAddress == asset.ipAddress]),
                        "checks": count_low + count_medium + count_high + count_critical,
                        "vInfo": 0,
                        "vLow": count_low,
                        "vMedium": count_medium,
                        "vHigh": count_high,
                        "vCritical": count_critical,
                        "parentId": asset.id,
                        "parentModule": "assets",
                        "createdById": self.attributes.app.config["userId"],
                        "lastUpdatedById": self.attributes.app.config["userId"],
                        "isPublic": True,
                        "tenantsId": 0,
                        "dateCreated": get_current_datetime(),
                        "dateLastUpdated": get_current_datetime(),
                    }
                )

                posted_scan = ScanHistory.post_scan(self.attributes.app, Api(), scan)

                if isinstance(posted_scan, ScanHistory):
                    asset_vulns = [vuln for vuln in self.data["vulns"] if vuln.parentId == asset.id]
                    # update vuln scan id
                    for vuln in asset_vulns:
                        vuln.scanId = posted_scan.id
                        insert_vulns.append(vuln)
                scan_progress.advance(scan_task, advance=1)
        Vulnerability.post_vulnerabilities(self.attributes.app, insert_vulns, output_to_console=True)

    def create_assets(self, func: Callable) -> None:
        """
        Create assets in RegScale from csv file

        :param Callable func: Function to create asset
        :rtype: None
        """
        existing_assets = self.get_existing_assets()
        self.process_assets(func)
        self.insert_new_assets(existing_assets)
        self.update_existing_assets(existing_assets)
        self.refresh_assets()

    def refresh_assets(self) -> None:
        """
        Refresh the assets in the data
        """
        self.data["assets"] = self.get_existing_assets()

    def get_existing_assets(self) -> List[Asset]:
        """
        Get existing assets from RegScale
        """
        return Asset.get_all_by_parent(self.attributes.parent_id, self.attributes.parent_module)

    def process_assets(self, func: Callable) -> None:
        """
        Process the assets in the data
        """
        if isinstance(self.file_data, list):
            for dat in self.file_data:
                self.process_asset_data(dat, func)
        elif isinstance(self.file_data, dict):
            self.data["assets"] = func(self.file_data)

    def process_asset_data(self, dat: Any, func: Callable) -> None:
        """
        Process the asset data

        :param Any dat: The data to process
        :param Callable func: The function to process the data
        :rtype: None
        """

        res = func(dat)
        if isinstance(res, Asset) and res not in self.data["assets"]:
            self.data["assets"].append(res)
        elif isinstance(res, list):
            for asset in res:
                if asset not in self.data["assets"]:
                    self.data["assets"].append(asset)

    def insert_new_assets(self, existing_assets: List[Asset]) -> None:
        """
        Insert new assets in RegScale

        :param List[Asset] existing_assets: List of existing assets
        """

        insert_assets = [asset for asset in self.data["assets"] if asset not in existing_assets]
        if insert_assets:
            self.log_and_report("Creating", len(insert_assets), insert_assets, "insert_assets")
            self.check_status_codes(Asset.batch_create(items=insert_assets))

    def update_existing_assets(self, existing_assets: List[Asset]) -> None:
        """
        Update existing assets in RegScale

        :param List[Asset] existing_assets: List of existing assets
        """
        update_assets = [asset for asset in self.data["assets"] if asset in existing_assets]
        for asset in update_assets:
            asset.id = existing_assets[existing_assets.index(asset)].id
        if update_assets:
            self.log_and_report("Updating", len(update_assets), update_assets, "update_assets")
            self.check_status_codes(Asset.batch_update(items=update_assets))

    def log_and_report(self, action: str, count: int, assets: List[Asset], report_suffix: str) -> None:
        """
        Log and report the action

        :param str action: The action to log
        :param int count: The count of assets
        :param List[Asset] assets: List of assets
        :param str report_suffix: The report suffix
        """
        self.attributes.logger.info(f"{action} %i unique assets in RegScale...", count)
        ReportGenerator(
            objects=assets,
            to_file=True,
            report_name=f"{self.attributes.name}_{report_suffix}",
            regscale_id=self.attributes.parent_id,
            regscale_module=self.attributes.parent_module,
        )

    @staticmethod
    def check_status_codes(response_list: list) -> None:
        """
        Check if any of the responses are not 200

        :param list response_list: List of responses
        :raises AssertionError: If any of the responses are not 200
        :rtype: None
        """
        for response in response_list:
            if isinstance(response, requests.Response) and response.status_code != 200:
                raise AssertionError(
                    f"Unable to {response.request.method} asset to RegScale.\n"
                    f"Code: {response.status_code}\nReason: {response.reason}"
                    f"\nPayload: {response.text}"
                )

    def lookup_kev(self, cve: str) -> str:
        """
        Determine if the cve is part of the published CISA KEV list

        :param str cve: The CVE to lookup.
        :return: A string containing the KEV CVE due date.
        :rtype: str
        """
        kev_data = None
        kev_date = None
        if self.cisa_kev:
            try:
                # Update kev and date
                kev_data = next(
                    dat
                    for dat in self.cisa_kev["vulnerabilities"]
                    if "vulnerabilities" in self.cisa_kev and cve and dat["cveID"].lower() == cve.lower()
                )
            except (StopIteration, ConnectionRefusedError):
                kev_data = None
        if kev_data:
            # Convert YYYY-MM-DD to datetime
            kev_date = convert_datetime_to_regscale_string(datetime.strptime(kev_data["dueDate"], DT_FORMAT))
        return kev_date

    def update_due_dt(self, iss: Issue, kev_due_date: Optional[str], scanner: str, severity: str) -> Issue:
        """
        Find the due date for the issue

        :param Issue iss: RegScale Issue object
        :param Optional[str] kev_due_date: The KEV due date
        :param str scanner: The scanner
        :param str severity: The severity of the issue
        :return: RegScale Issue object
        :rtype: Issue
        """
        fmt = "%Y-%m-%d %H:%M:%S"
        days = 30
        if severity == "medium":
            severity = "moderate"
        if severity == "important":
            severity = "high"
        if severity not in ["low", "moderate", "high", "critical"]:
            # An odd severity should be treated as low.
            severity = "low"
        try:
            days = self.attributes.app.config["issues"][scanner][severity]
        except KeyError:
            self.attributes.logger.error(
                "Unable to find severity '%s'\n defaulting to %i days\nPlease add %s to the init.yaml configuration",
                severity,
                days,
                severity,
            )
        if kev_due_date and (datetime.strptime(kev_due_date, fmt) > datetime.now()):
            iss.dueDate = kev_due_date
        else:
            iss.dueDate = datetime.strftime(
                datetime.now() + timedelta(days=days),
                fmt,
            )
        return iss

    def _check_issue(self, issue: Issue) -> None:
        """
        Check if the issue is in the data

        :param Issue issue: The issue to check to prevent duplicates
        :rtype: None
        """
        if issue and issue not in self.data["issues"]:
            self.data["issues"].append(issue)

    def _check_issues(self, issues: List[Issue]) -> None:
        """
        Check if the issues are in the data

        :param List[Issue] issues: The issues to check to prevent duplicates
        """
        for issue in issues:
            self._check_issue(issue)

    def create_issues(self, func: Callable) -> None:
        """
        Create an issue in RegScale from csv file

        :param Callable func: Function to create issue
        :rtype: None
        """

        existing_issues = Issue.get_all_by_parent(
            parent_id=self.attributes.parent_id,
            parent_module=self.attributes.parent_module,
        )
        with create_progress_object() as issue_progress:
            issue_task = issue_progress.add_task("Processing issues...", total=len(self.file_data))

            for dat in self.file_data:
                if isinstance(self.file_data, dict):
                    # File data is a dict, lets process as a whole.
                    issues = func(dat=self.file_data)
                    self._check_issues(issues)
                    # break the loop
                    break
                response = func(dat=dat)
                if isinstance(response, Issue):
                    issue = response
                    self._check_issue(issue)
                if isinstance(response, list):
                    issues = response
                    for iss in issues:
                        self._check_issue(iss)
                issue_progress.advance(issue_task, advance=1)
        self.attributes.logger.info("Found %i issues for processing in RegScale.", len(self.data["issues"]))
        if insert_issues := [issue for issue in self.data["issues"] if issue not in existing_issues]:
            self.attributes.logger.info("Creating %i unique issue(s) in RegScale...", len(insert_issues))
            new_issues = Issue.bulk_insert(self.attributes.app, insert_issues)
            self.handle_link_creation(new_issues, insert_issues)
        for issue in self.data["issues"]:
            if issue in existing_issues:
                issue.id = existing_issues[existing_issues.index(issue)].id
        if update_issues := [issue for issue in self.data["issues"] if issue in existing_issues]:
            self.attributes.logger.info("Updating %i unique issue(s) in RegScale...", len(update_issues))
            Issue.bulk_update(self.attributes.app, update_issues)
        self.check_and_close_issues(existing_issues)

    def check_and_close_issues(self, existing_issues: list[Issue]) -> None:
        """
        Function to close issues that are no longer being reported in the export file

        :param list[Issue] existing_issues: List of existing issues in RegScale
        :rtype: None
        """
        existing_cves = self.group_issues_by_cve_id(existing_issues)
        parsed_cves = {issue.cve for issue in self.data["issues"] if issue.cve}
        closed_issues = []
        with create_progress_object() as close_issue_progress:
            closing_issues = close_issue_progress.add_task(
                "Comparing parsed issue(s) and existing issue(s)...",
                total=len(existing_cves),
            )
            for cve, issues in existing_cves.items():
                if cve not in parsed_cves:
                    for issue in issues:
                        if issue.status == "Closed":
                            continue
                        self.attributes.logger.debug("Closing issue #%s", issue.id)
                        issue.status = "Closed"
                        issue.dateCompleted = self.scan_date.strftime("%Y-%m-%d %H:%M:%S")
                        if issue.save():
                            self.attributes.logger.debug("Issue #%s closed", issue.id)
                            closed_issues.append(issue)
                close_issue_progress.advance(closing_issues, advance=1)
        self.log_and_save_closed_issues(closed_issues)

    @staticmethod
    def group_issues_by_cve_id(existing_issues: list[Issue]) -> dict[str, list[Issue]]:
        """
        Function to group existing issues from RegScale by cve and returns a dictionary of cveId and issues

        :param list[Issue] existing_issues: List of existing issues in RegScale
        :returns: A dictionary of cveId and list of issues with the same cveId
        :rtype: dict[str, list[Issue]]
        """
        from collections import defaultdict

        # create a dict with an empty list for each cve, so we can close issues that have duplicate CVEs
        existing_cves = defaultdict(list)
        # group issues by cve
        for issue in existing_issues:
            if issue.cve:
                existing_cves[issue.cve].append(issue)
        return existing_cves

    def log_and_save_closed_issues(self, closed_issues: list[Issue]) -> None:
        """
        Log and save the closed issues if any

        :param list[Issue] closed_issues: List of closed issues to log and save
        :rtype: None
        """
        if len(closed_issues) > 0:
            self.attributes.logger.info("Closed %i issue(s) in RegScale.", len(closed_issues))
            ReportGenerator(
                objects=closed_issues,
                to_file=True,
                report_name=f"{self.attributes.name}_closed_issues",
                regscale_id=self.attributes.parent_id,
                regscale_module=self.attributes.parent_module,
            )

    def handle_link_creation(self, new_issues: list[Issue], parsed_issues: list[Issue]) -> None:
        """
        Function to create child link records for issues

        :param list[Issue] new_issues: List of new issues that were just created in RegScale
        :param list[Issue] parsed_issues: List of issues parsed from the export file
        :rtype: None
        """
        new_issue_dict = {issue.cve: issue for issue in new_issues}
        parsed_issues = {issue.cve: issue for issue in parsed_issues}
        for cve, issue in new_issue_dict.items():
            if cve in parsed_issues:
                # check if there is a link to be created
                if vuln_link := parsed_issues[cve].extra_data.get("link"):
                    from regscale.models.regscale_models.link import Link

                    self.attributes.logger.debug("Creating link for issue #%s, url: %s", issue.id, vuln_link)
                    for link in self.extract_links(vuln_link):
                        new_link = Link(
                            url=link,
                            parentID=issue.id,
                            parentModule="issues",
                            title=link,
                        )
                        created_link = new_link.create()
                        self.attributes.logger.debug("Link created: #%s", created_link.id)

    def create_vulns(self, func: Callable) -> None:
        """
        Create vulns in RegScale from csv file

        :param Callable func: Function to create vuln
        :rtype: None
        """

        def check_vuln(vuln_to_check: Vulnerability) -> None:
            """
            Check if the vuln is in the data

            :param Vulnerability vuln_to_check: The vulnerability to check to prevent duplicates
            :rtype: None
            """
            if vuln_to_check and vuln_to_check not in self.data["vulns"]:
                self.data["vulns"].append(vuln_to_check)

        with create_progress_object() as vuln_progress:
            vuln_task = vuln_progress.add_task("Processing vulnerabilities...", total=len(self.file_data))
            for dat in self.file_data:
                vuln = func(dat)
                if isinstance(vuln, Vulnerability):
                    check_vuln(vuln)
                if isinstance(vuln, list):
                    for v in vuln:
                        check_vuln(v)
                vuln_progress.advance(vuln_task, advance=1)
        self.attributes.logger.info(
            "Found %i vulnerabilities for processing in RegScale.",
            len(self.data["vulns"]),
        )

    def clean_up(self) -> None:
        """
        Move the Nexpose file to the processed folder

        :rtype: None
        """
        processed_dir = self.attributes.file_path.parent / "processed"
        check_file_path(str(processed_dir.absolute()))
        api = Api()
        try:
            if self.attributes.parent_id:
                file_name = (
                    f"{self.attributes.file_path.stem}_" + f"{get_current_datetime('%Y%m%d-%I%M%S%p')}"
                ).replace(" ", "_")
                # Rename to friendly file name and post to Regscale
                new_name = (self.attributes.file_path.parent / file_name).with_suffix(self.attributes.file_path.suffix)
                new_file_path = self.attributes.file_path.rename(new_name)
                self.attributes.logger.info(
                    "Renaming %s to %s, and uploading it to RegScale...",
                    self.attributes.file_path.name,
                    new_file_path.name,
                )
                File.upload_file_to_regscale(
                    file_name=str(new_file_path.absolute()),
                    parent_id=self.attributes.parent_id,
                    parent_module=self.attributes.parent_module,
                    api=api,
                )
                shutil.move(new_file_path, processed_dir)
                self.attributes.logger.info("File uploaded to RegScale and moved to %s", processed_dir)
        except shutil.Error:
            self.attributes.logger.debug(
                "File %s already exists in %s",
                new_file_path.name,
                processed_dir,
            )

    def gen_issue(self, **kwargs: dict) -> Issue:
        """
        Generate an issue

        :param dict **kwargs: The keyword arguments for this function
        :rtype: Issue
        """
        severity = kwargs.get("severity", "low")
        title = kwargs.get("title", "")
        description = kwargs.get("description", "")
        asset_identifier = kwargs.get("assetIdentifier", "")
        solution = kwargs.get("solution", "")
        first_detected_dt = kwargs.get("first_detected_dt")
        iss = Issue(
            isPoam=severity in ["low", "medium", "high", "critical"],
            title=title,
            description=description,
            status="Open",
            severityLevel=Issue.assign_severity(severity),
            issueOwnerId=self.attributes.app.config["userId"],
            assetIdentifier=asset_identifier,
            securityPlanId=(self.attributes.parent_id if self.attributes.parent_module == "securityplans" else None),
            recommendedActions=solution if solution else "Upgrade affected package",
            cve=title,
            autoApproved="No",
            identification="Other",
            parentId=self.attributes.parent_id,
            parentModule=self.attributes.parent_module,
            # Set issue due date to the kev date if it is in the kev list
        )
        iss.originalRiskRating = iss.assign_risk_rating(severity)
        # Date not provided, we must use the creation date of the file
        iss.dateFirstDetected = (
            first_detected_dt.strftime(self.dt_format) if isinstance(first_detected_dt, datetime) else ""
        )
        iss.basisForAdjustment = f"{self.name} import"
        return iss

    @abstractmethod
    def create_asset(self):
        """Create an asset"""

    @abstractmethod
    def create_issue(self, **kwargs: dict) -> Optional[Issue]:
        """
        Create an issue from a dictionary, and a predefined severity and first detected date

        :param dict **kwargs: The keyword arguments for this function
        :return: RegScale Issue object or None
        :rtype: Optional[Issue]
        """

        dat = kwargs.get("dat", {})
        description = kwargs.get("description", "")
        asset_identifier = kwargs.get("asset_identifier", "")
        severity = kwargs.get("severity", "low")
        first_detected_dt = kwargs.get("first_detected_dt")
        kev_due_date = kwargs.get("kev_due_date", None)
        if self.attributes.app.config["issues"][self.name.lower()]["useKev"]:
            kev_due_date = self.lookup_kev(dat["CVE"][0] if dat.get("CVE") else None)
        iss = self.gen_issue(
            title=dat.get(self.vuln_title, ""),
            description=dat.get("Description", description),
            assetIdentifier=asset_identifier,
            severity=severity,
            solution=dat.get("Solution", ""),
            first_detected_dt=first_detected_dt,
        )
        iss = self.update_due_dt(
            iss=iss,
            kev_due_date=kev_due_date,
            scanner=self.name.lower(),
            severity=severity,
        )

        return iss

    @abstractmethod
    def create_vuln(self):
        """Create a Vulnerability"""

    @staticmethod
    def common_scanner_options(message: str, prompt: str) -> Callable[[Callable], click.option]:
        """
        Common options for container scanner integrations

        :param str message: The message to display to the user
        :param str prompt: The prompt to display to the user
        :return: The decorated function
        :rtype: Callable[[Callable], click.option]
        """

        def decorator(this_func) -> Callable[[Callable], click.option]:
            this_func = click.option(
                "--folder_path",
                help=message,
                prompt=prompt,
                required=True,
                type=click.Path(exists=True, dir_okay=True, resolve_path=True),
            )(this_func)
            this_func = click.option(
                "--regscale_ssp_id",
                type=click.INT,
                help="The ID number from RegScale of the System Security Plan.",
                prompt="Enter RegScale System Security Plan ID",
                required=True,
            )(this_func)
            this_func = click.option(
                "--scan_date",
                type=click.DateTime(formats=[DT_FORMAT]),
                help="The scan date of the file.",
                required=False,
            )(this_func)
            return this_func

        return decorator

    @staticmethod
    def check_date_format(the_date: Any) -> bool:
        """
        Check if the date is in the correct format

        :param Any the_date: The date to check
        :return: True if the date is in the correct format
        :rtype: bool

        """
        res = False
        try:
            if isinstance(the_date, str):
                the_date = datetime.strptime(the_date, DT_FORMAT)
            # make sure the date is not in the future
            if the_date >= datetime.now():
                error_and_exit("The scan date cannot be in the future.")
            res = True
        except ValueError:
            error_and_exit("Incorrect data format, should be YYYY-MM-DD")
        return res

    def update_mapping(self, kwargs: dict) -> tuple[dict, Mapping]:
        """
        Update the mapping for Nexpose

        :param dict kwargs: Keyword arguments
        :return: Modified Keyword arguments and Mapping object
        :rtype: tuple[dict, Mapping]
        """
        mapping: Mapping = self.default_mapping()
        if kwargs.get("mapping"):
            mapping = kwargs["mapping"]
            # Not needed for the parent class
            del kwargs["mapping"]
        return kwargs, mapping

    def convert_xml_to_dict(self, file: TextIO) -> dict:
        """
        Convert an XML file to a Python dictionary.

        :param TextIO file: The file object representing the XML file.
        :return: A dictionary representation of the XML content.
        :rtype: dict
        """

        xml_content = file.read()
        dict_content = xmltodict.parse(xml_content)
        return dict_content

    @staticmethod
    def default_mapping() -> Mapping:
        """
        Placeholder mapping for the Super class
        """
        mapping_dict = {"mapping": {}}

        return Mapping(**mapping_dict)

    @staticmethod
    def determine_severity(s: str) -> str:
        """
        Determine the CVSS severity of the vulnerability

        :param str s: The severity
        :return: The severity
        :rtype: str
        """
        severity = "info"
        if s:
            severity = s.lower()
        # remap crits to highs
        if severity == "critical":
            severity = "high"
        return severity

    def extract_links(self, link_str: str) -> list:
        """
        Extract URLs from a string

        :param str link_str: The string to extract URLs from
        :return: The URLs
        :rtype: list
        """
        # Define a basic URL pattern
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        # Find all non-overlapping matches in the string
        urls = re.findall(url_pattern, link_str)
        return urls
