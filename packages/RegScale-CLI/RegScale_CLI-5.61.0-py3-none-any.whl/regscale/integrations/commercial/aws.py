#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" RegScale AWS Audit Manager Integration """

import datetime
import os

import click

from regscale.core.app.logz import create_logger
from regscale.integrations.commercial.amazon.common import sync_aws_findings
from regscale.models.integration_models.container_scan import ContainerScan

logger = create_logger()


# Create group to handle AWS integration
@click.group()
def aws():
    """AWS Integrations"""


@aws.group(help="Sync AWS Inspector Scans to RegScale.")
def inspector():
    """Sync AWS Inspector scans."""


@aws.command(name="sync_findings")
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
    help="Create Issue in RegScale from vulnerabilities in AWS Security Hub.",
    default=False,
)
@click.option(
    "--aws_access_key_id",
    "--key_id",
    type=click.STRING,
    required=False,
    help="AWS Access Key ID",
    default=os.environ.get("AWS_ACCESS_KEY_ID"),
)
@click.option(
    "--aws_secret_access_key",
    "--key",
    type=click.STRING,
    required=False,
    help="AWS Secret Access Key",
    default=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)
# noqa: E402
def sync_findings(
    regscale_ssp_id: int,
    create_issue: bool = False,
    aws_access_key_id: str = os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY"),
) -> None:
    """Sync AWS Security Hub Findings."""
    sync_aws_findings(regscale_ssp_id, create_issue, aws_access_key_id, aws_secret_access_key)


@inspector.command(name="import_scans")
@ContainerScan.common_scanner_options(
    message="File path to the folder containing AWS Inspector files to process to RegScale.",
    prompt="File path for AWS Inspector files (CSV or JSON)",
)
def import_scans(folder_path: os.PathLike[str], regscale_ssp_id: int, scan_date: datetime.date) -> None:
    from pathlib import Path

    from regscale.models.integration_models.amazon_models.inspector_scan import InspectorScan
    from regscale.regscale import Application

    app = Application()
    csv_files = list(Path(folder_path).glob("*.csv"))
    json_files = list(Path(folder_path).glob("*.json"))
    matched_files = csv_files + json_files
    if not matched_files:
        raise FileNotFoundError("No AWS Inspector files found in the specified folder.")
    logger.debug("AWS Files: " + str(matched_files))
    if not scan_date:
        scan_date = datetime.datetime.now()
    for file in matched_files:
        InspectorScan(
            name="AWS Inspector",
            app=app,
            file_path=file,
            scan_date=scan_date,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            ignore_validation=False,
            file_type=file.suffix,
        )
