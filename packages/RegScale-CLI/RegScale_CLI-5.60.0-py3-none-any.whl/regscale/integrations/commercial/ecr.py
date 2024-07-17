#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ECR RegScale integration"""
from pathlib import Path

import click

from regscale.core.app.application import Application
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.integration_models.ecr_models.ecr import ECR
from regscale.validation.record import validate_regscale_object


@click.group()
def ecr():
    """Performs actions on ECR Scanner artifacts."""


@ecr.command(name="import_ecr")
@ContainerScan.common_scanner_options(
    message="File path to the folder containing ECR files to process to RegScale.",
    prompt="File path for ECR files",
)
def import_ecr(folder_path: click.Path, regscale_ssp_id: click.INT, scan_date: click.STRING):
    """
    Import ECR scans, vulnerabilities and assets to RegScale from ECR JSON files

    """
    app = Application()
    if not validate_regscale_object(regscale_ssp_id, "securityplans"):
        app.logger.warning("SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id)
        return
    json_files = list(Path(folder_path).glob("*.json"))
    csv_files = list(Path(folder_path).glob("*.csv"))
    ecr_files = json_files + csv_files
    if not ecr_files:
        app.logger.warning("No ECR files found in %s", folder_path)
    for file in ecr_files:
        ECR(
            app=app,
            name="ECR",
            file_path=file,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            scan_date=scan_date,
            file_type=file.suffix,
        )
