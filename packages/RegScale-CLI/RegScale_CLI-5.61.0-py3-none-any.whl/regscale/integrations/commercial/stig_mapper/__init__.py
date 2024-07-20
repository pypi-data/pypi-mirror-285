""" STIG Mapper commands. """

import click
import logging
from regscale.integrations.commercial.stig_mapper.stig_mapper import STIGMapper
from regscale.models import regscale_id, regscale_module, Component, Asset

logger = logging.getLogger(__name__)


@click.group()
def stig_mapper(name="stig_mapper"):
    """Map data from STIGs to RegScale."""


@stig_mapper.command(name="run")
@click.option(
    "--json-file", help="Path to the JSON file with mapping rules", required=True, type=click.Path(exists=True)
)
@regscale_id()
@regscale_module()
def run(json_file: str, regscale_id: int, regscale_module: str):
    """
    Map STIGs from a .json file to assets in RegScale.
    """
    stig_mapper = STIGMapper(json_file)
    components = Component.get_all_by_parent(parent_id=regscale_id, parent_module=regscale_module)
    assets = Asset.get_all_by_parent(parent_id=regscale_id, parent_module=regscale_module)
    asset_mappings = stig_mapper.map_stigs_to_assets(asset_list=assets, component_list=components)
    stig_mapper.save_all_mappings(mappings=asset_mappings)
    logger.info(f"Created {len(asset_mappings)} new asset mappings")
