#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Veracode RegScale integration"""
from datetime import datetime
from os import PathLike
from pathlib import Path

import click

from regscale.core.app.application import Application
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.integration_models.veracode import Veracode
from regscale.validation.record import validate_regscale_object


@click.group()
def veracode():
    """Performs actions on Veracode export files."""


@veracode.command(name="import_veracode")
@ContainerScan.common_scanner_options(
    message="File path to the folder containing Veracode .xlsx files to process to RegScale.",
    prompt="File path for Veracode files:",
)
def import_veracode(folder_path: PathLike[str], regscale_ssp_id: int, scan_date: datetime):
    """
    Import scans, vulnerabilities and assets to RegScale from Veracode export files

    """
    app = Application()
    if not validate_regscale_object(regscale_ssp_id, "securityplans"):
        app.logger.warning("SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id)
        return
    if not scan_date or not ContainerScan.check_date_format(scan_date):
        scan_date = datetime.now()
    xml_file_list = list(Path(folder_path).glob("*.xml"))  # Support Veracode file format
    csv_file_list = list(Path(folder_path).glob("*.xlsx"))  # Support Coalfire Excel format
    file_list = xml_file_list + csv_file_list
    if len(file_list) == 0:
        app.logger.warning("No Veracode files found in the specified folder.")
        return
    for file in file_list:
        Veracode(
            name="Veracode",
            app=app,
            file_path=file,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            scan_date=scan_date,
        )
