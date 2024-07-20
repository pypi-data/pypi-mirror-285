#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nexpose RegScale integration"""
import ast
from datetime import datetime
from os import PathLike
from pathlib import Path

import click
from rich.console import Console

from regscale.core.app.application import Application
from regscale.models.app_models.mapping import Mapping
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.integration_models.nexpose import Nexpose
from regscale.validation.record import validate_regscale_object


@click.group()
def nexpose():
    """Performs actions on Nexpose files."""


@nexpose.command(name="show_mapping")
def show_mapping():
    """Show the default mapping for Prisma."""
    import json

    mapping = Nexpose.default_mapping().mapping
    console = Console()
    # convert dict to json string
    dat = json.dumps(mapping, indent=4)
    console.print(dat)


@nexpose.command(name="import_nexpose")
@ContainerScan.common_scanner_options(
    message="File path to the folder containing Nexpose .csv files to process to RegScale.",
    prompt="File path for Nexpose files:",
)
@click.option(
    "--header_map_file",
    help="The CLI will use the custom header from the provided mapping file",
    type=click.Path(exists=True),
    default=None,
    required=False,
)
## TODO: Add Show mapping file option
def import_nexpose(
    folder_path: PathLike[str], regscale_ssp_id: int, scan_date: datetime, header_map_file: Path
) -> None:
    """
    Import Nexpose scans, vulnerabilities and assets to RegScale from Nexpose files
    """
    app = Application()
    if not validate_regscale_object(regscale_ssp_id, "securityplans"):
        app.logger.warning("SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id)
        return
    if not scan_date or not ContainerScan.check_date_format(scan_date):
        scan_date = datetime.now()
    if len(list(Path(folder_path).glob("*.csv"))) == 0:
        app.logger.warning("No Nexpose(csv) files found in the specified folder.")
        return
    mapping = None
    if header_map_file:
        expected_field_names = [
            "IP Address",
            "Hostname",
            "OS",
            "Vulnerability Title",
            "Vulnerability ID",
            "CVSSv2 Score",
            "CVSSv3 Score",
            "Description",
            "Proof",
            "Solution",
            "CVEs",
        ]
        mapping = Mapping.from_file(file_path=header_map_file, expected_field_names=expected_field_names)
    for file in Path(folder_path).glob("*.csv"):
        Nexpose(
            name="Nexpose", file_path=str(file), regscale_ssp_id=regscale_ssp_id, scan_date=scan_date, mapping=mapping
        )
