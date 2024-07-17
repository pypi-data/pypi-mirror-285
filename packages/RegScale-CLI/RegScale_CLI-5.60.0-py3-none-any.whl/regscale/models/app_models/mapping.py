#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Pydantic class for custom container scan mappings """
import json
from json import JSONDecodeError
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from regscale.core.app import create_logger
from regscale.core.app.utils.app_utils import error_and_exit


class Mapping(BaseModel):
    """
    Pydantic class for custom container scan mappings
    """

    model_config = ConfigDict(populate_by_name=True, json_encoders={bytes: lambda v: v.decode()})

    mapping: Dict[str, str]
    # expected field names for validation
    expected_field_names: List[str] = []
    _logger: Logger = create_logger()

    @field_validator("expected_field_names")
    @classmethod
    def validate_mapping(cls: Type["Mapping"], expected_field_names: List[str], values: Dict[str, Any]) -> List[str]:
        """
        Validate the expected field names

        :param List[str] expected_field_names: Expected field names
        :param Dict[str, Any] values: Values
        :return: Expected field names
        """
        mapping = values.data.get("mapping")
        if mapping is not None and expected_field_names is not None:
            missing_fields = [field for field in expected_field_names if field not in mapping]
            if missing_fields:
                # Raising a validation error here forces a type error : No constructor
                error_and_exit(
                    f"The following expected fields are missing in the mapping, and are required: {missing_fields}"
                )
        return expected_field_names

    @field_validator("expected_field_names")
    @classmethod
    def validate_expected_field_names(cls: Type["Mapping"], expected_field_names: Any) -> List[str]:
        """
        Validate the expected field names and types

        :param Any expected_field_names: Expected field names
        :raises ValidationError: If expected_field_names is not a list or if any element in the list is not a string
        :rtype: List[str]
        :return: Expected field names
        """
        if not isinstance(expected_field_names, list):
            raise ValidationError("expected_field_names must be a list")
        if not all(isinstance(field_name, str) for field_name in expected_field_names):
            raise ValidationError("All elements in expected_field_names must be strings")
        return expected_field_names

    # Add a from file method to load the mapping from a JSON file
    @classmethod
    def from_file(cls, file_path: Path, expected_field_names: List[str] = []) -> "Mapping":
        """
        Load the mapping from a JSON file

        :param Path file_path: Path to the JSON file
        :param List[str] expected_field_names: Expected field names, defaults to []
        :raises ValueError: If the mapping key is missing or mapping data is empty in the JSON file
        :rtype: Mapping
        :return: Mapping
        """
        with open(file_path, "r") as file:
            try:
                dat = json.load(file)
                if not dat.get("mapping"):
                    raise ValueError("The mapping key is missing or mapping data is empty in the JSON file")
                mapping = cls(mapping=dat["mapping"], expected_field_names=expected_field_names)
            except JSONDecodeError as jex:
                cls._logger.default.debug(jex)
                error_and_exit("JSON file is badly formatted, please check the file")
            except (ValueError, SyntaxError) as exc:
                error_and_exit(f"Error parsing JSON file: {exc}")
        return mapping

    def get_value(self, dat: Optional[dict], key: str, warnings: bool = True) -> Any:
        """
        Get the value from a dictionary by mapped key

        :param Optional[dict] dat: Data dictionary, defaults to None
        :param str key: Key to get the value for
        :param bool warnings: Whether to log warnings, defaults to False
        :return: Value for the key
        :rtype: Any
        """
        # check mapping
        mapped_key = self.mapping.get(key)
        if not mapped_key and warnings:
            self._logger.warning(f"Key {key} not found in mapping")
        if dat and mapped_key:
            val = dat.get(mapped_key)
            if isinstance(val, str):
                return val.strip()
        if warnings:
            self._logger.warning(f"Value for key {key} not found in data")
        return None

    def to_header(self) -> list[str]:
        """
        Convert the mapping to a header
        :return: Mapping as a header
        :rtype: list[str]
        """
        # convert mapping to a list of strings
        return [f"{value}" for key, value in self.mapping.items()]
