#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Integrates Qualys assets and vulnerabilities into RegScale CLI """
import os
import pprint
from asyncio import sleep
from datetime import datetime, timedelta
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Optional, Tuple, Union

import click
import requests
import xmltodict
from requests import Session
from rich.progress import TaskID

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    create_progress_object,
    error_and_exit,
    get_current_datetime,
    save_data_to,
)
from regscale.core.app.utils.regscale_utils import lookup_reg_assets_by_parent
from regscale.integrations.scanner_integration import IntegrationFinding
from regscale.models.app_models.click import NotRequiredIf, save_output_to
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.integration_models.qualys import Qualys
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.issue import Issue

####################################################################################################
#
# Qualys API Documentation:
#   https://qualysguard.qg2.apps.qualys.com/qwebhelp/fo_portal/api_doc/index.htm
#
####################################################################################################


# create global variables for the entire module
logger = create_logger()

# create progress object to add tasks to for real time updates
job_progress = create_progress_object()
HEADERS = {"X-Requested-With": "RegScale CLI"}
QUALYS_API = Session()


# Create group to handle Qualys commands
@click.group()
def qualys():
    """Performs actions from the Qualys API"""


@qualys.command(name="export_scans")
@save_output_to()
@click.option(
    "--days",
    type=int,
    default=30,
    help="The number of days to go back for completed scans, default is 30.",
)
@click.option(
    "--export",
    type=click.BOOL,
    help="To disable saving the scans as a .json file, use False. Defaults to True.",
    default=True,
    prompt=False,
    required=False,
)
def export_past_scans(save_output_to: Path, days: int, export: bool = True):
    """Export scans from Qualys Host that were completed
    in the last x days, defaults to last 30 days
    and defaults to save it as a .json file"""
    export_scans(
        save_path=save_output_to,
        days=days,
        export=export,
    )


@qualys.command(name="import_scans")
@ContainerScan.common_scanner_options(
    message="File path to the folder containing Aqua .csv files to process to RegScale.",
    prompt="File path for Qualys files",
)
def import_scans(folder_path: os.PathLike[str], regscale_ssp_id: int, scan_date: datetime):
    """Import scans from Qualys"""
    files_lst = list(Path(folder_path).glob("*.csv"))
    # If no files are found in the folder, return a warning
    if len(files_lst) == 0:
        logger.warning("No Qualys files found in the folder path provided.")
        return
    if not scan_date or not ContainerScan.check_date_format(scan_date):
        scan_date = datetime.now()
    # loop through all files in folder_path
    for file in files_lst:
        Qualys(
            name="Qualys",
            file_path=file,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            scan_date=scan_date,
        )


@qualys.command(name="save_results")
@save_output_to()
@click.option(
    "--scan_id",
    type=click.STRING,
    help="Qualys scan reference ID to get results, defaults to all.",
    default="all",
)
def save_results(save_output_to: Path, scan_id: str):
    """Get scan results from Qualys using a scan ID or all scans and save them to a .json file."""
    save_scan_results_by_id(save_path=save_output_to, scan_id=scan_id)


@qualys.command(name="sync_qualys")
@click.option(
    "--regscale_ssp_id",
    type=click.INT,
    required=True,
    prompt="Enter RegScale System Security Plan ID",
    help="The ID number from RegScale of the System Security Plan",
)
@click.option(
    "--create_issue",
    type=click.BOOL,
    required=False,
    help="Create Issue in RegScale from vulnerabilities in Qualys.",
    default=False,
)
@click.option(
    "--asset_group_id",
    type=click.INT,
    help="Filter assets from Qualys with an asset group ID.",
    default=None,
    cls=NotRequiredIf,
    not_required_if=["asset_group_name"],
)
@click.option(
    "--asset_group_name",
    type=click.STRING,
    help="Filter assets from Qualys with an asset group name.",
    default=None,
    cls=NotRequiredIf,
    not_required_if=["asset_group_id"],
)
def sync_qualys(
    regscale_ssp_id: int,
    create_issue: bool = False,
    asset_group_id: int = None,
    asset_group_name: str = None,
):
    """
    Query Qualys and sync assets & their associated
    vulnerabilities to a Security Plan in RegScale.
    """
    sync_qualys_to_regscale(
        regscale_ssp_id=regscale_ssp_id,
        create_issue=create_issue,
        asset_group_id=asset_group_id,
        asset_group_name=asset_group_name,
    )


@qualys.command(name="get_asset_groups")
@save_output_to()
def get_asset_groups(save_output_to: Path):
    """
    Get all asset groups from Qualys via API and save them to a .json file.
    """
    # see if user has enterprise license
    check_license()

    date = get_current_datetime("%Y%m%d")
    check_file_path(save_output_to)
    asset_groups = get_asset_groups_from_qualys()
    save_data_to(
        file=Path(f"{save_output_to}/qualys_asset_groups_{date}.json"),
        data=asset_groups,
    )


def export_scans(
    save_path: Path,
    days: int = 30,
    export: bool = True,
) -> None:
    """
    Function to export scans from Qualys that were completed in the last x days, defaults to 30

    :param Path save_path: Path to save the scans to as a .json file
    :param int days: # of days of completed scans to export, defaults to 30 days
    :param bool export: Whether to save the scan data as a .json, defaults to True
    :rtype: None
    """
    # see if user has enterprise license
    check_license()
    date = get_current_datetime("%Y%m%d")
    results = get_detailed_scans(days)
    if export:
        check_file_path(save_path)
        save_data_to(
            file=Path(f"{save_path.name}/qualys_scans_{date}.json"),
            data=results,
        )
    else:
        pprint.pprint(results, indent=4)


def save_scan_results_by_id(save_path: Path, scan_id: str) -> None:
    """
    Function to save the queries from Qualys using an ID a .json file

    :param Path save_path: Path to save the scan results to as a .json file
    :param str scan_id: Qualys scan ID to get the results for
    :rtype: None
    """
    # see if user has enterprise license
    check_license()

    check_file_path(save_path)
    with job_progress:
        if scan_id.lower() == "all":
            # get all the scan results from Qualys
            scans = get_scans_summary("all")

            # add task to job progress to let user know # of scans to fetch
            task1 = job_progress.add_task(
                f"[#f8b737]Getting scan results for {len(scans['SCAN'])} scan(s)...",
                total=len(scans["SCAN"]),
            )
            # get the scan results from Qualys
            scan_data = get_scan_results(scans, task1)
        else:
            task1 = job_progress.add_task(f"[#f8b737]Getting scan results for {scan_id}...", total=1)
            # get the scan result for the provided scan id
            scan_data = get_scan_results(scan_id, task1)
    # save the scan_data as the provided file_path
    save_data_to(file=save_path, data=scan_data)


def sync_qualys_to_regscale(
    regscale_ssp_id: int,
    create_issue: bool = False,
    asset_group_id: int = None,
    asset_group_name: str = None,
) -> None:
    """
    Sync Qualys assets and vulnerabilities to a security plan in RegScale

    :param int regscale_ssp_id: ID # of the SSP in RegScale
    :param bool create_issue: Flag whether to create an issue in RegScale from Qualys vulnerabilities, defaults to False
    :param int asset_group_id: Optional filter for assets in Qualys with an asset group ID, defaults to None
    :param str asset_group_name: Optional filter for assets in Qualys with an asset group name, defaults to None
    :rtype: None
    """
    # see if user has enterprise license
    check_license()

    # check if the user provided an asset group id or name
    if asset_group_id:
        # get the assets from Qualys using the group name
        sync_qualys_assets_and_vulns(
            ssp_id=regscale_ssp_id,
            create_issue=create_issue,
            asset_group_filter=asset_group_name,
        )
    elif asset_group_name:
        # get the assets from Qualys using the group name
        sync_qualys_assets_and_vulns(
            ssp_id=regscale_ssp_id,
            create_issue=create_issue,
            asset_group_filter=asset_group_id,
        )
    else:
        sync_qualys_assets_and_vulns(ssp_id=regscale_ssp_id, create_issue=create_issue)


def get_scan_results(scans: Any, task: TaskID) -> dict:
    """
    Function to retrieve scan results from Qualys using provided scan list and returns a dictionary

    :param Any scans: list of scans to retrieve from Qualys
    :param TaskID task: task to update in the progress object
    :return: dictionary of detailed Qualys scans
    :rtype: dict
    """
    app = check_license()
    config = app.config

    # set the auth for the QUALYS_API session
    QUALYS_API.auth = (config["qualysUserName"], config["qualysPassword"])

    scan_data = {}
    # check number of scans requested
    if isinstance(scans, str):
        # only one scan was requested, set up variable for the for loop
        scans = {"SCAN": [{"REF": scans}]}
    for scan in scans["SCAN"]:
        # set up data and parameters for the scans query
        try:
            # try and get the scan id ref #
            scan_id = scan["REF"]
            # set the parameters for the Qualys API call
            params = {
                "action": "fetch",
                "scan_ref": scan_id,
                "mode": "extended",
                "output_format": "json_extended",
            }
            # get the scan data via API
            res = QUALYS_API.get(
                url=f"{config['qualysUrl']}/api/2.0/fo/scan/",
                headers=HEADERS,
                params=params,
            )
            # convert response to json
            if res.status_code == 200:
                try:
                    res_data = res.json()
                    scan_data[scan_id] = res_data
                except JSONDecodeError:
                    error_and_exit("Unable to convert response to JSON.")
            else:
                error_and_exit(f"Received unexpected response from Qualys API: {res.status_code}: {res.text}")
        except KeyError:
            # unable to get the scan id ref #
            continue
        job_progress.update(task, advance=1)
    return scan_data


def get_detailed_scans(days: int) -> list:
    """
    function to get the list of all scans from Qualys using QUALYS_API

    :param int days: # of days before today to filter scans
    :return: list of results from Qualys API
    :rtype: list
    """
    app = check_license()
    config = app.config

    # set the auth for the QUALYS_API session
    QUALYS_API.auth = (config["qualysUserName"], config["qualysPassword"])

    today = datetime.now()
    scan_date = today - timedelta(days=days)

    # set up data and parameters for the scans query
    params = {
        "action": "list",
        "scan_date_since": scan_date.strftime("%Y-%m-%d"),
        "output_format": "json",
    }
    params2 = {
        "action": "list",
        "scan_datetime_since": scan_date.strftime("%Y-%m-%dT%H:%I:%S%ZZ"),
    }
    res = QUALYS_API.get(
        url=f"{config['qualysUrl']}/api/2.0/fo/scan/summary/",
        headers=HEADERS,
        params=params,
    )
    response = QUALYS_API.get(
        url=f"{config['qualysUrl']}/api/2.0/fo/scan/vm/summary/",
        headers=HEADERS,
        params=params2,
    )
    # convert response to json
    res_data = res.json()
    try:
        response_data = xmltodict.parse(response.text)["SCAN_SUMMARY_OUTPUT"]["RESPONSE"]["SCAN_SUMMARY_LIST"][
            "SCAN_SUMMARY"
        ]
        if len(res_data) < 1:
            res_data = response_data
        else:
            res_data.extend(response_data)
    except JSONDecodeError:
        logger.error("ERROR: Unable to convert to JSON.")
    return res_data


def get_scans_summary(scan_choice: str) -> dict:
    """
    Get all scans from Qualys Host

    :param str scan_choice: The type of scan to retrieve from Qualys API
    :return: Detailed summary of scans from Qualys API as a dictionary
    :rtype: dict
    """
    app = check_license()
    config = app.config
    urls = []

    # set the auth for the QUALYS_API session
    QUALYS_API.auth = (config["qualysUserName"], config["qualysPassword"])

    # set up variables for function
    scan_data = {}
    responses = []
    scan_url = f"{config['qualysUrl']}/api/2.0/fo/scan/"

    # set up parameters for the scans query
    params = {"action": "list"}
    # check what scan list was requested and set urls list accordingly
    if scan_choice.lower() == "all":
        urls = [scan_url, scan_url + "compliance", scan_url + "scap"]
    elif scan_choice.lower() == "vm":
        urls = [scan_url]
    elif scan_choice.lower() in ["compliance", "scap"]:
        urls = [scan_url + scan_choice.lower()]
    # get the list of vm scans
    for url in urls:
        # get the scan data
        response = QUALYS_API.get(url=url, headers=HEADERS, params=params)
        # store response into a list
        responses.append(response)
    # check the responses received for data
    for response in responses:
        # see if response was successful
        if response.status_code == 200:
            # parse the data
            data = xmltodict.parse(response.text)["SCAN_LIST_OUTPUT"]["RESPONSE"]
            # see if the scan has any data
            try:
                # add the data to the scan_data dictionary
                scan_data.update(data["SCAN_LIST"])
            except KeyError:
                # no data found, continue the for loop
                continue
    return scan_data


def get_scan_details(days: int) -> list:
    """
    Retrieve completed scans from last x days from Qualys Host

    :param int days: # of days before today to filter scans
    :return: Detailed summary of scans from Qualys API as a dictionary
    :rtype: list
    """
    app = check_license()
    config = app.config

    # set the auth for the QUALYS_API session
    QUALYS_API.auth = (config["qualysUserName"], config["qualysPassword"])
    # get since date for API call
    since_date = datetime.now() - timedelta(days=days)
    # set up data and parameters for the scans query
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Requested-With": "RegScale CLI",
    }
    params = {
        "action": "list",
        "scan_date_since": since_date.strftime("%Y-%m-%d"),
        "output_format": "json",
    }
    params2 = {
        "action": "list",
        "scan_datetime_since": since_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    res = QUALYS_API.get(
        url=f"{config['qualysUrl']}/api/2.0/fo/scan/summary/",
        headers=headers,
        params=params,
    )
    response = QUALYS_API.get(
        url=f"{config['qualysUrl']}/api/2.0/fo/scan/vm/summary/",
        headers=headers,
        params=params2,
    )
    # convert response to json
    res_data = res.json()
    try:
        response_data = xmltodict.parse(response.text)["SCAN_SUMMARY_OUTPUT"]["RESPONSE"]["SCAN_SUMMARY_LIST"][
            "SCAN_SUMMARY"
        ]
        if len(res_data) < 1:
            res_data = response_data
        else:
            res_data.update(response_data)
    except JSONDecodeError as ex:
        error_and_exit(f"Unable to convert to JSON.\n{ex}")
    except KeyError:
        error_and_exit(f"No data found.\n{response.text}")
    return res_data


def sync_qualys_assets_and_vulns(
    ssp_id: int,
    create_issue: bool,
    asset_group_filter: Optional[Union[int, str]] = None,
) -> None:
    """
    Function to query Qualys and sync assets & associated vulnerabilities to RegScale

    :param int ssp_id: RegScale System Security Plan ID
    :param bool create_issue: Flag to create an issue in RegScale for each vulnerability from Qualys
    :param Optional[Union[int, str]] asset_group_filter: Filter the Qualys assets by an asset group ID or name, if any
    :rtype: None
    """
    app = check_license()
    config = app.config
    regscale_api = Api()
    qualys_assets_and_issues = []

    # set the auth for the QUALYS_API session
    QUALYS_API.auth = (config["qualysUserName"], config["qualysPassword"])

    # Get the assets from RegScale with the provided SSP ID
    logger.info("Getting assets from RegScale for SSP #%s...", ssp_id)
    reg_assets = lookup_reg_assets_by_parent(api=regscale_api, parent_id=ssp_id, module="securityplans")
    logger.info(
        "Located %s asset(s) associated with SSP #%s in RegScale.",
        len(reg_assets),
        ssp_id,
    )
    logger.debug(reg_assets)

    if qualys_assets := get_qualys_assets_and_scan_results(asset_group_filter):
        logger.info("Received %s assets from Qualys.", len(qualys_assets))
        logger.debug(qualys_assets)
        # Get vulnerabilities from Qualys for the Qualys assets
        logger.info("Getting vulnerabilities for %s asset(s) from Qualys...", len(qualys_assets))
        qualys_assets_and_issues, total_vuln_count = get_issue_data_for_assets(qualys_assets)
        logger.info("Received %s vulnerabilities from Qualys.", total_vuln_count)
        logger.debug(qualys_assets_and_issues)
    else:
        error_and_exit("No assets found in Qualys.")
    sync_assets(
        qualys_assets=qualys_assets,
        reg_assets=reg_assets,
        qualys_assets_and_issues=qualys_assets_and_issues,
        ssp_id=ssp_id,
        config=config,
        regscale_api=regscale_api,
    )
    if create_issue:
        sync_issues(
            ssp_id=ssp_id,
            qualys_assets_and_issues=qualys_assets_and_issues,
            config=config,
            regscale_api=regscale_api,
        )


def sync_assets(
    qualys_assets: list[dict],
    reg_assets: list[Asset],
    qualys_assets_and_issues: list[dict],
    ssp_id: int,
    config: dict,
    regscale_api: Api,
) -> None:
    """
    Function to sync Qualys assets to RegScale

    :param list[dict] qualys_assets: List of Qualys assets
    :param list[Asset] reg_assets: List of RegScale assets
    :param list[dict] qualys_assets_and_issues: List of Qualys assets and their issues
    :param int ssp_id: RegScale System Security Plan ID
    :param dict config: Configuration dictionary
    :param Api regscale_api: RegScale API object
    :rtype: None
    """
    update_assets = []
    for qualys_asset in qualys_assets:  # you can list as many input dicts as you want here
        lookup_assets = lookup_asset(reg_assets, qualys_asset["ASSET_ID"])
        # Update parent id to SSP on insert
        if len(lookup_assets) > 0:
            for asset in set(lookup_assets):
                asset.parentId = ssp_id
                asset.parentModule = "securityplans"
                asset.otherTrackingNumber = qualys_asset["ID"]
                asset.ipAddress = qualys_asset["IP"]
                asset.qualysId = qualys_asset["ASSET_ID"]
                try:
                    assert asset.id
                    # avoid duplication
                    if asset.qualysId not in [v["qualysId"] for v in update_assets]:
                        update_assets.append(asset.dict())
                except AssertionError as aex:
                    logger.error("Asset does not have an id, unable to update!\n%s", aex)
    update_and_insert_assets(
        qualys_assets_and_issues=qualys_assets_and_issues,
        reg_assets=reg_assets,
        ssp_id=ssp_id,
        config=config,
        regscale_api=regscale_api,
        update_assets=update_assets,
    )


def update_and_insert_assets(
    qualys_assets_and_issues: list[dict],
    reg_assets: list[Asset],
    ssp_id: int,
    config: dict,
    regscale_api: Api,
    update_assets: list[dict],
) -> None:
    """
    Function to update and insert Qualys assets into RegScale

    :param list[dict] qualys_assets_and_issues: List of Qualys assets and their issues
    :param list[Asset] reg_assets: List of RegScale assets
    :param int ssp_id: RegScale System Security Plan ID
    :param dict config: RegScale CLI Configuration dictionary
    :param Api regscale_api: RegScale API object
    :param list[dict] update_assets: List of assets to update
    :rtype: None
    """
    insert_assets = []
    if assets_to_be_inserted := [
        qualys_asset
        for qualys_asset in qualys_assets_and_issues
        if qualys_asset["ASSET_ID"]
        not in [asset["ASSET_ID"] for asset in inner_join(reg_assets, qualys_assets_and_issues)]
    ]:
        for qualys_asset in assets_to_be_inserted:
            # Do Insert
            r_asset = Asset(
                name=f'Qualys Asset #{qualys_asset["ASSET_ID"]} IP: {qualys_asset["IP"]}',
                otherTrackingNumber=qualys_asset["ID"],
                parentId=ssp_id,
                parentModule="securityplans",
                ipAddress=qualys_asset["IP"],
                assetOwnerId=config["userId"],
                assetType="Other",
                assetCategory="Hardware",
                status="Off-Network",
                qualysId=qualys_asset["ASSET_ID"],
            )
            # avoid duplication
            if r_asset.qualysId not in set(v["qualysId"] for v in insert_assets):
                insert_assets.append(r_asset.dict())
        try:
            regscale_api.update_server(
                method="post",
                url=f"{config['domain']}/api/assets",
                json_list=insert_assets,
                message=f"Creating {len(insert_assets)} asset(s) from Qualys to RegScale.",
            )

            logger.info("RegScale Assets successfully created: %i", len(insert_assets))
        except requests.exceptions.RequestException as rex:
            logger.error("Unable to create Qualys Assets in RegScale\n%s", rex)
    if len(update_assets) > 0:
        try:
            regscale_api.update_server(
                method="put",
                url=f"{config['domain']}/api/assets",
                json_list=update_assets,
                message=f"Updating {len(update_assets)} assets from Qualys to RegScale.",
            )
            logger.info("RegScale Assets successfully updated: %i", len(update_assets))
        except requests.RequestException as rex:
            logger.error("Unable to Update Qualys Assets to RegScale\n%s", rex)


def sync_issues(ssp_id: int, qualys_assets_and_issues: list[dict], config: dict, regscale_api: Api) -> None:
    """
    Function to sync Qualys issues to RegScale

    :param int ssp_id: RegScale System Security Plan ID
    :param list[dict] qualys_assets_and_issues: List of Qualys assets and their issues
    :param dict config: RegScale CLI Configuration dictionary
    :param Api regscale_api: RegScale API object
    :rtype: None
    """
    update_issues = []
    insert_issues = []
    vuln_count = 0
    ssp_assets = Asset.get_all_by_parent(parent_id=ssp_id, parent_module="securityplans")
    for asset in qualys_assets_and_issues:
        # Create issues in RegScale from Qualys vulnerabilities
        regscale_issue_updates, regscale_new_issues = create_regscale_issue_from_vuln(
            regscale_ssp_id=ssp_id, qualys_asset=asset, regscale_assets=ssp_assets, vulns=asset["ISSUES"]
        )
        update_issues.extend(regscale_issue_updates)
        insert_issues.extend(regscale_new_issues)
        vuln_count += len(asset.get("ISSUES", []))
    if len(insert_issues) > 0:
        deduped_vulns = combine_duplicate_qualys_vulns(insert_issues)
        logger.info(
            "Creating %i new issue(s) in RegScale, condensed from %i Qualys vulnerabilities.",
            len(deduped_vulns),
            vuln_count,
        )
        regscale_api.update_server(
            url=f"{config['domain']}/api/issues",
            message=f"Creating {len(deduped_vulns)} issue(s) in RegScale...",
            json_list=[vuln.dict() for vuln in deduped_vulns],
        )
        logger.info("RegScale Issue(s) successfully created: %i", len(deduped_vulns))
    if len(update_issues) > 0:
        deduped_vulns = combine_duplicate_qualys_vulns(update_issues)
        logger.info(
            "Updating %i existing issue(s) in RegScale, condensed from %i Qualys vulnerabilities.",
            len(deduped_vulns),
            vuln_count,
        )
        regscale_api.update_server(
            url=f"{config['domain']}/api/issues",
            message=f"Updating {len(deduped_vulns)} issues..",
            json_list=[issue.dict() for issue in deduped_vulns],
            method="put",
        )
        logger.info("RegScale Issue(s) successfully updated: %i", len(deduped_vulns))


def combine_duplicate_qualys_vulns(qualys_vulns: list[Issue]) -> list:
    """
    Function to combine duplicate Qualys vulnerabilities

    :param list[Issue] qualys_vulns: List of Qualys vulnerabilities as RegScale issues
    :return: List of Qualys vulnerabilities with duplicates combined
    :rtype: list
    """
    with job_progress:
        logger.info("Combining duplicate Qualys vulnerabilities found across multiple assets...")
        deduping_task = job_progress.add_task(
            f"Combining {len(qualys_vulns)} Qualys vulnerabilities...",
            total=len(qualys_vulns),
        )
        combined_vulns: dict[str, Issue] = {}
        for vuln in qualys_vulns:
            if vuln.qualysId in combined_vulns:
                if current_identifier := combined_vulns[vuln.qualysId].assetIdentifier:
                    combined_vulns[vuln.qualysId].assetIdentifier = update_asset_identifier(
                        vuln.assetIdentifier, current_identifier
                    )
                else:
                    combined_vulns[vuln.qualysId].assetIdentifier = vuln.assetIdentifier
            else:
                combined_vulns[vuln.qualysId] = vuln
            job_progress.update(deduping_task, advance=1)
    return list(combined_vulns.values())


def get_qualys_assets_and_scan_results(asset_group_filter: Optional[Union[int, str]] = None) -> list:
    """
    function to gather all assets from Qualys API host along with their scan results

    :param Optional[Union[int, str]] asset_group_filter: Qualys asset group ID or name to filter by, if provided
    :return: list of dictionaries containing asset data
    :rtype: list
    """
    app = check_license()
    config = app.config

    # set the auth for the QUALYS_API session
    QUALYS_API.auth = (config["qualysUserName"], config["qualysPassword"])
    # set url
    url = f'{config["qualysUrl"]}api/2.0/fo/asset/host/vm/detection?action=list&show_asset_id=1'

    # check if an asset group filter was provided and append it to the url
    if asset_group_filter:
        if isinstance(asset_group_filter, str):
            # Get the asset group ID from Qualys
            url += f"&ag_titles={asset_group_filter}"
            logger.info("Getting assets from Qualys by group name: %s...", asset_group_filter)
        else:
            url += f"&ag_ids={asset_group_filter}"
            logger.info(
                "Getting assets from from Qualys by group ID: #%s...",
                asset_group_filter,
            )
    else:
        # Get all assets from Qualys
        logger.info("Getting all assets from Qualys...")

    # get the data via Qualys API host
    response = QUALYS_API.get(url=url, headers=HEADERS)

    try:
        # parse the xml data from response.text and convert it to a dictionary
        # and try to extract the data from the parsed XML dictionary
        asset_data = xmltodict.parse(response.text)["HOST_LIST_VM_DETECTION_OUTPUT"]["RESPONSE"]["HOST_LIST"]["HOST"]
    except KeyError:
        # if there is a KeyError set the dictionary to nothing
        asset_data = []
    # return the asset_data variable
    return asset_data


def get_issue_data_for_assets(asset_list: list) -> Tuple[list[dict], int]:
    """
    Function to get issue data from Qualys via API for assets in Qualys

    :param list asset_list: Assets and their scan results from Qualys
    :return:  Updated asset list of Qualys assets and their associated vulnerabilities, total number of vulnerabilities
    :rtype: Tuple[list[dict], int]
    """
    app = check_license()
    config = app.config

    # set the auth for the QUALYS_API session
    QUALYS_API.auth = (config["qualysUserName"], config["qualysPassword"])

    with job_progress:
        issues = {}
        for asset in asset_list:
            # check if the asset has any vulnerabilities
            if vulns := asset.get("DETECTION_LIST", {}).get("DETECTION", {}):
                asset_vulns = {}
                analyzing_vulns = job_progress.add_task(
                    f"Analyzing {len(vulns)} vulnerabilities for asset #{asset['ASSET_ID']} from Qualys..."
                )
                # iterate through the vulnerabilities & verify they have a confirmed status
                for vuln in vulns:
                    if vuln["TYPE"] == "Confirmed":
                        issues[vuln["QID"]] = vuln
                        asset_vulns[vuln["QID"]] = vuln
                    job_progress.update(analyzing_vulns, advance=1)
                job_progress.update(analyzing_vulns, completed=len(vulns))
                # add the issues to the asset's dictionary
                asset["ISSUES"] = asset_vulns
                job_progress.remove_task(analyzing_vulns)
    asset_list = fetch_vulns_from_qualys(issue_ids=list(issues.keys()), asset_list=asset_list, config=config)
    return asset_list, len(issues)


def fetch_vulns_from_qualys(issue_ids: list[str], asset_list: list[dict], config: dict, retries: int = 0) -> list[dict]:
    """
    Function to fetch vulnerability data from Qualys for a list of issues and assets

    :param list[str] issue_ids: List of Qualys issue IDs to fetch data for
    :param list[dict] asset_list: List of Qualys assets to update with vulnerability data
    :param dict config: CLI Configuration dictionary
    :param int retries: Number of retries for fetching data, defaults to 0
    :return: Updated asset list with vulnerability data
    :rtype: list[dict]
    """
    logger.info(
        f"Getting vulnerability data for {len(issue_ids)} issue(s) from Qualys for {len(asset_list)} asset(s)..."
    )
    response = QUALYS_API.get(
        url=f"{config['qualysUrl']}api/2.0/fo/knowledge_base/vuln?action=list&details=All&ids={','.join(issue_ids)}",
        headers=HEADERS,
    )
    if response.ok:
        issue_data = xmltodict.parse(response.text)["KNOWLEDGE_BASE_VULN_LIST_OUTPUT"]["RESPONSE"]["VULN_LIST"]["VULN"]
        # change the key for the fetched issues to be the qualys ID
        qualys_issue_data = {issue["QID"]: issue for issue in issue_data}
        logger.info("Received vulnerability data for %s issues from Qualys.", len(qualys_issue_data))
    elif response.status_code == 409:
        response_data = xmltodict.parse(response.text)["SIMPLE_RETURN"]["RESPONSE"]
        logger.warning(
            "Received timeout error from Qualys API: %s. Waiting %s seconds...",
            response_data["TEXT"],
            response_data["ITEM_LIST"]["ITEM"]["VALUE"],
        )
        sleep(int(response_data["ITEM_LIST"]["ITEM"]["VALUE"]))
        if retries < 3:
            fetch_vulns_from_qualys(issue_ids, asset_list, config, retries + 1)
        else:
            error_and_exit("Unable to fetch vulnerability data from Qualys after 3 attempts. Please try again later.")
    else:
        error_and_exit(
            f"Received unexpected response from Qualys API: {response.status_code}: {response.text}: {response.reason}"
        )
    return map_issue_data_to_assets(asset_list, qualys_issue_data)


def map_issue_data_to_assets(assets: list[dict], qualys_issue_data: dict) -> list[dict]:
    """
    Function to map Qualys issue data to Qualys assets

    :param list[dict] assets: List of Qualys assets to map issue data to
    :param dict qualys_issue_data: List of Qualys issues to map to assets
    :return: Updated asset list with Qualys issue data
    :rtype: list[dict]
    """
    for asset in assets:
        if issues := asset.get("ISSUES"):
            mapping_vulns = job_progress.add_task(
                f"Mapping {len(issues)} vulnerabilities to Asset #{asset['ASSET_ID']} from Qualys...",
                total=len(issues),
            )
            for issue in issues:
                if issue in qualys_issue_data:
                    issues[issue]["ISSUE_DATA"] = qualys_issue_data[issue]
                job_progress.update(mapping_vulns, advance=1)
            job_progress.remove_task(mapping_vulns)
    return assets


def lookup_asset(asset_list: list, asset_id: str = None) -> list[Asset]:
    """
    Function to look up an asset in the asset list and returns an Asset object

    :param list asset_list: List of assets from RegScale
    :param str asset_id: Qualys asset ID to search for, defaults to None
    :return: list of Asset objects
    :rtype: list[Asset]
    """
    if asset_id:
        results = [Asset(**asset) for asset in asset_list if asset.get("qualysId") == asset_id]
    else:
        results = [Asset(**asset) for asset in asset_list]
    # Return unique list
    return list(set(results)) or []


def map_qualys_severity_to_regscale(severity: int) -> tuple[str, str]:
    """
    Map Qualys vulnerability severity to RegScale Issue severity

    :param int severity: Qualys vulnerability severity
    :return: RegScale Issue severity and key for init.yaml
    :rtype: tuple[str, str]
    """
    if severity <= 2:
        return "III - Low - Other Weakness", "low"
    if severity == 3:
        return "II - Moderate - Reportable Condition", "moderate"
    if severity > 3:
        return "I - High - Significant Deficiency", "high"
    return "IV - Not Assigned", "low"


def create_regscale_issue_from_vuln(
    regscale_ssp_id: int, qualys_asset: dict, regscale_assets: list[Asset], vulns: dict
) -> Tuple[list[Issue], list[Issue]]:
    """
    Sync Qualys vulnerabilities to RegScale issues.

    :param int regscale_ssp_id: RegScale SSP ID
    :param dict qualys_asset: Qualys asset as a dictionary
    :param list[Asset] regscale_assets: list of RegScale assets
    :param dict vulns: dictionary of Qualys vulnerabilities associated with the provided asset
    :return: list of RegScale issues to update, and a list of issues to be created
    :rtype: Tuple[list[Issue], list[Issue]]
    """
    app = check_license()
    config = app.config

    # set the auth for the QUALYS_API session
    QUALYS_API.auth = (config["qualysUserName"], config["qualysPassword"])
    default_status = config["issues"]["qualys"]["status"]
    regscale_issues = []
    regscale_existing_issues = Issue.get_all_by_parent(parent_id=regscale_ssp_id, parent_module="securityplans")
    for vuln in vulns.values():
        asset_identifier = None
        severity, key = map_qualys_severity_to_regscale(int(vuln["SEVERITY"]))

        default_due_delta = config["issues"]["qualys"][key]
        logger.debug("Processing vulnerability# %s", vuln["QID"])
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        due_date = datetime.strptime(vuln["LAST_FOUND_DATETIME"], fmt) + timedelta(days=default_due_delta)
        regscale_asset = [asset for asset in regscale_assets if asset.qualysId == qualys_asset["ASSET_ID"]]
        if "DNS" not in qualys_asset.keys() or "IP" not in qualys_asset.keys():
            if regscale_asset:
                asset_identifier = f"RegScale Asset #{regscale_asset[0].id}: {regscale_asset[0].name}"
        else:
            if regscale_asset:
                asset_identifier = f'RegScale Asset #{regscale_asset[0].id}: {regscale_asset[0].name} Qualys DNS: {qualys_asset["DNS"]} - IP: {qualys_asset["IP"]}'
            else:
                asset_identifier = f'DNS: {qualys_asset["DNS"]} - IP: {qualys_asset["IP"]}'
        issue = Issue(
            title=vuln["ISSUE_DATA"]["TITLE"],
            description=vuln["ISSUE_DATA"]["CONSEQUENCE"] + "</br>" + vuln["ISSUE_DATA"]["DIAGNOSIS"],
            issueOwnerId=config["userId"],
            status=default_status,
            severityLevel=severity,
            qualysId=vuln["QID"],
            dueDate=due_date.strftime(fmt),
            identification="Vulnerability Assessment",
            parentId=regscale_ssp_id,
            parentModule="securityplans",
            recommendedActions=vuln["ISSUE_DATA"]["SOLUTION"],
            assetIdentifier=asset_identifier,
        )
        regscale_issues.append(issue)
    regscale_new_issues, regscale_update_issues = determine_issue_update_or_create(
        regscale_issues, regscale_existing_issues
    )
    return regscale_update_issues, regscale_new_issues


def update_asset_identifier(new_identifier: Optional[str], current_identifier: Optional[str]) -> str:
    """
    Function to update the asset identifier for a RegScale issue

    :param Optional[str] new_identifier: New asset identifier to add
    :param Optional[str] current_identifier: Current asset identifier
    :return: Updated asset identifier
    :rtype: str
    """
    if not current_identifier and new_identifier:
        return new_identifier
    if current_identifier and new_identifier:
        if new_identifier not in current_identifier:
            return f"{current_identifier}<br>{new_identifier}"
        if new_identifier in current_identifier:
            return current_identifier
        if new_identifier == current_identifier:
            return current_identifier


def determine_issue_update_or_create(
    qualys_issues: list[Issue], regscale_issues: list[Issue]
) -> Tuple[list[Issue], list[Issue]]:
    """
    Function to determine if Qualys issues needs to be updated or created in RegScale

    :param list[Issue] qualys_issues: List of Qualys issues
    :param list[Issue] regscale_issues: List of existing RegScale issues
    :return: List of new issues and list of issues to update
    :rtype: Tuple[list[Issue], list[Issue]]
    """
    new_issues = []
    update_issues = []
    for issue in qualys_issues:
        if issue.qualysId in [iss.qualysId for iss in regscale_issues]:
            update_issue = [iss for iss in regscale_issues if iss.qualysId == issue.qualysId][0]
            # Check if we need to concatenate the asset identifier
            update_issue.assetIdentifier = update_asset_identifier(issue.assetIdentifier, update_issue.assetIdentifier)
            update_issues.append(update_issue)
        else:
            new_issues.append(issue)
    return new_issues, update_issues


def inner_join(reg_list: list, qualys_list: list) -> list:
    """
    Function to compare assets from Qualys and assets from RegScale

    :param list reg_list: list of assets from RegScale
    :param list qualys_list: list of assets from Qualys
    :return: list of assets that are in both RegScale and Qualys
    :rtype: list
    """
    set1 = set(lst.get("qualysId") for lst in reg_list)
    data = []
    try:
        data = [list_qualys for list_qualys in qualys_list if list_qualys.get("ASSET_ID") in set1]
    except KeyError as ex:
        logger.error(ex)
    return data


def get_asset_groups_from_qualys() -> list:
    """
    Get all asset groups from Qualys via API

    :return: list of assets from Qualys
    :rtype: list
    """
    app = check_license()
    config = app.config
    asset_groups = []

    # set the auth for the QUALYS_API session
    QUALYS_API.auth = (config["qualysUserName"], config["qualysPassword"])
    response = QUALYS_API.get(url=f"{config['qualysUrl']}api/2.0/fo/asset/group?action=list", headers=HEADERS)
    if response.ok:
        logger.debug(response.text)
        try:
            asset_groups = xmltodict.parse(response.text)["ASSET_GROUP_LIST_OUTPUT"]["RESPONSE"]["ASSET_GROUP_LIST"][
                "ASSET_GROUP"
            ]
        except KeyError:
            logger.debug(response.text)
            error_and_exit(
                f"Unable to retrieve asset groups from Qualys.\nReceived: #{response.status_code}: {response.text}"
            )
    return asset_groups


if __name__ == "__main__":
    from regscale.core.app.internal.login import login

    login(
        str_user=os.environ["REGSCALE_USER"],
        str_password=os.environ["REGSCALE_PASSWORD"],
        host=os.environ["REGSCALE_DOMAIN"],
    )
    sync_qualys_to_regscale(
        regscale_ssp_id=131,
        create_issue=True,
    )
