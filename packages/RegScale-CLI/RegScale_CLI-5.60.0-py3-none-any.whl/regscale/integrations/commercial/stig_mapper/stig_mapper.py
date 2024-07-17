"""
Stig Mapper module
"""

import json
import logging
from typing import List, Dict
from regscale.models.regscale_models import Asset, AssetMapping, Component


logger = logging.getLogger(__name__)


def equals(a: str, b: str) -> bool:
    """
    Compare two strings for equality.
    :param str a: The first string
    :param str b: The second string
    :return bool: True if the strings are equal, False otherwise
    :rtype: bool
    """
    return a == b


def contains(a: str, b: str) -> bool:
    """
    Check if string a contains string b.
    :param str a: The string to search
    :param str b: The string to find
    :return bool: True if a contains b, False otherwise
    :rtype: bool
    """
    return b in a


def startswith(a: str, b: str) -> bool:
    """
    Check if string a starts with string b.
    :param str a: The string to search
    :param str b: The string to find
    :return bool: True if a starts with b, False otherwise
    :rtype: bool
    """
    return a.startswith(b)


# You can add more comparators if needed
comparator_functions = {"equals": equals, "contains": contains, "startswith": startswith}


class STIGMapper:
    """
    A class to map STIGs to assets based on rules.
    """

    def __init__(self, json_file: str):
        self.rules = self.load_rules(json_file)

    @staticmethod
    def load_rules(json_file: str) -> List[Dict[str, str]]:
        """
        Load rules from a JSON file.
        :param str json_file: The path to the JSON file
        :return: A list of rules
        :rtype: List[Dict[str, str]]
        """
        with open(json_file, "r") as file:
            data = json.load(file)
            return data.get("rules", [])

    def map_stigs_to_assets(
        self,
        asset_list: List["Asset"],
        component_list: List[Component],
    ) -> List["AssetMapping"]:
        """
        Map STIGs to assets based on rules.
        :param List[Asset] asset_list: A list of assets
        :param List[Component] component_list: A list of components
        :return: A list of asset mappings
        :rtype: List[AssetMapping]
        """
        new_asset_mappings = []
        for rule in self.rules:
            stig_name = rule["stig"]
            comparator = rule["comparator"]
            value = rule["value"]
            property_name = rule["property"]
            existing_mappings = []
            component_id = None
            for component in component_list:
                if component.title == stig_name:
                    component_id = component.id
                    existing_mappings.extend(AssetMapping.find_mappings(component_id=component_id))
                    break
            if not component_id:
                continue
            matching_assets = self.find_matching_assets(
                property_name=property_name, value=value, asset_list=asset_list, comparator=comparator
            )
            for asset in matching_assets:
                asset_mapping = AssetMapping(
                    assetId=asset.id,
                    componentId=component_id,
                )
                mapping_already_exists = self.mapping_exists(asset_mapping, existing_mappings)
                mapping_in_new_mappings = asset_mapping in new_asset_mappings
                if not mapping_already_exists and not mapping_in_new_mappings:
                    logger.info(f"Mapping -> Asset ID: {asset.id}, Component ID: {component_id}")
                    new_asset_mappings.append(asset_mapping)
                else:
                    logger.info(f"Existing mapping found for Asset ID: {asset.id}, Component ID: {component_id}")
        return new_asset_mappings

    @staticmethod
    def save_all_mappings(mappings: List[AssetMapping]) -> None:
        """
        Save all asset mappings.
        :param List[AssetMapping] mappings: A list of asset mappings
        :rtype: None
        """
        for asset_mapping in mappings:
            asset_mapping.create()

    @staticmethod
    def mapping_exists(asset_mapping: AssetMapping, existing_mappings: List[AssetMapping]) -> bool:
        """
        Check if the asset mapping already exists.
        :param AssetMapping asset_mapping:
        :param List[AssetMapping] existing_mappings:
        :return: True if the mapping exists, False otherwise
        :rtype: bool
        """
        for existing_mapping in existing_mappings:
            if (
                existing_mapping.assetId == asset_mapping.assetId
                and existing_mapping.componentId == asset_mapping.componentId
            ):
                return True
        return False

    @staticmethod
    def find_matching_assets(property_name: str, value: str, asset_list: List[Asset], comparator: str) -> List["Asset"]:
        """
        Find matching assets based on the comparator method.
        :param str property_name: The property name to search
        :param str value: The value to compare
        :param List[Asset] asset_list: A list of assets
        :param str comparator: The comparator method
        :return List[Asset]: A list of matching assets
        :rtype: List[Asset]
        """
        matching_assets = []
        comparator_func = comparator_functions.get(comparator, None)

        if comparator_func:
            for asset in asset_list:
                asset_value = getattr(asset, property_name) if hasattr(asset, property_name) else None
                if asset_value and comparator_func(asset_value, value):
                    matching_assets.append(asset)
        return matching_assets
