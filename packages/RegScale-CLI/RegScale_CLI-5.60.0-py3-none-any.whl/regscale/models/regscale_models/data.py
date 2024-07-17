""" Data model class """

from enum import Enum
from typing import List, Optional, cast

from pydantic import Field, ConfigDict
from requests import Response

from regscale.core.app.utils.app_utils import (
    get_current_datetime,
    create_progress_object,
)
from .regscale_model import RegScaleModel, T


class DataListItem(RegScaleModel):
    """
    Data list item model class
    """

    id: int
    dateCreated: str
    dataType: str
    dataSource: str


class DataDataType(str, Enum):
    """
    Data data type enum
    """

    JSON = "JSON"
    XML = "XML"
    YAML = "YAML"

    def __str__(self):
        return self.value


class Data(RegScaleModel):
    """
    Data model class
    """

    _module_slug = "data"
    _unique_fields = ["parentId", "parentModule", "dataSource", "dataType"]

    id: Optional[int] = 0
    createdById: Optional[str] = Field(default_factory=RegScaleModel._api_handler.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel._api_handler.get_user_id)
    isPublic: bool = True
    dataSource: str
    dataType: Optional[str] = None
    rawData: Optional[str] = None
    parentId: int
    parentModule: str
    tenantsId: int = 1
    dateLastUpdated: str = Field(default_factory=get_current_datetime)

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Data model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            batch_create="/api/{model_slug}/batchCreate",
            batch_update="/api/{model_slug}/batchUpdate",
        )

    @classmethod
    def get_all_by_parent(cls, parent_id: int, parent_module: str) -> List[T]:
        """
        Get a list of objects by parent.

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A list of objects
        :rtype: List[T]
        """
        results = cls._handle_get_all_list_response(
            cls._api_handler.get(
                endpoint=cls.get_endpoint("get_all_by_parent").format(
                    intParentID=parent_id,
                    strModule=parent_module,
                )
            )
        )
        return [cls.get_object(r.id) for r in results]

    @classmethod
    def _handle_get_all_list_response(cls, response: Response, suppress_error: bool = False) -> List[T]:
        """
        Handle a list response.
        :param Response response: The response
        :param bool suppress_error: Whether to suppress the error, defaults to False
        :return: A list of objects or an empty List
        :rtype: List[T]
        """
        if not response or response.status_code in [204, 404]:
            return []
        if response.ok:
            json_response = response.json()
            if isinstance(json_response, dict) and "items" in json_response:
                json_response = json_response.get("items", [])
            return cast(List[DataListItem], [DataListItem(**o) for o in json_response])
        else:
            cls.log_response_error(response, suppress_error=False)
            return []
