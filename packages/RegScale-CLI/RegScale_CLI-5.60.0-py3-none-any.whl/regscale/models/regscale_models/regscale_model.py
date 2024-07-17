#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Base Regscale Model """
import copy
import json
import logging
import warnings
from abc import ABC
from typing import Any, ClassVar, Dict, List, Optional, TypeVar, Union, cast, get_type_hints

from pydantic import BaseModel, ConfigDict, Field
from requests import Response

from regscale.core.app.utils.api_handler import APIHandler, APIInsertionError, APIResponseError, APIUpdateError
from regscale.core.app.utils.app_utils import create_progress_object
from regscale.models.regscale_models.search import Search

T = TypeVar("T", bound="RegScaleModel")

logger = logging.getLogger("rich")


class RegScaleModel(BaseModel, ABC):
    """Mixin class for RegScale Models to add functionality to interact with RegScale API"""

    _module_slug = "model_slug"
    _module_string = ""
    _module_slug_id_url = "/api/{model_slug}/{id}"
    _module_slug_url = "/api/{model_slug}"
    _module_id = 0
    _api_handler: ClassVar[APIHandler] = APIHandler()
    _parent_id_field: str = "parentId"
    _unique_fields: list[str] = []
    _get_objects_for_list: bool = False
    _exclude_graphql_fields: list[str] = ["extra_data", "tenantsId"]
    _original_data: Optional[dict] = None

    id: int = 0
    extra_data: dict = Field(default={}, exclude=True)
    createdById: Optional[str] = None
    lastUpdatedById: Optional[str] = None

    class Config:
        use_enum_values = True
        populate_by_name = True

    def __init__(self: T, *args, **data) -> T:
        try:
            super().__init__(*args, **data)
            # Capture initial state after initialization
            self._original_data = self.dict(exclude_unset=True)
        except Exception as e:
            logger.error(f"Error creating {self.__class__.__name__}: {e} {data}", exc_info=True)

    def has_changed(self) -> bool:
        """
        Check if current data differs from the original data.

        :return: True if the data has changed, False otherwise
        :rtype: bool
        """
        if getattr(self, "id", 0) in [0, None]:
            return True
        return any(self.show_changes())

    def show_changes(self) -> Dict[str, Any]:
        """
        Display the changes between the original data and the current data.

        :return: A dictionary of changes
        :rtype: Dict[str, Any]
        """
        if getattr(self, "id", 0) == 0:
            return self._original_data
        if not self._original_data:
            return {}
        current_data = self.dict(exclude_unset=True)
        changes = {
            key: {"from": self._original_data.get(key), "to": current_data.get(key)}
            for key in current_data
            if current_data.get(key) != self._original_data.get(key)  # and key != "id"
        }
        return changes

    def diff(self, other: Any) -> Dict:
        """
        Find the differences between two objects

        :param Any other: The other object to compare
        :return: A dictionary of differences
        :rtype: Dict
        """
        differences = {}
        for attr in vars(self):
            if getattr(self, attr) != getattr(other, attr):
                differences[attr] = (getattr(self, attr), getattr(other, attr))
        return differences

    def dict(self, exclude_unset: bool = False, **kwargs: Optional[dict]) -> dict[str, Any]:
        """
        Override the default dict method to exclude hidden fields

        :param bool exclude_unset: Whether to exclude unset fields, defaults to False
        :param Optional[dict] **kwargs: Additional keyword arguments
        :return: Dictionary representation of the object
        :rtype: dict[str, Any]
        """
        hidden_fields = set(
            attribute_name
            for attribute_name, model_field in self.model_fields.items()
            if model_field.from_field("hidden") == "hidden"
        )
        unset_fields = set(
            attribute_name
            for attribute_name, model_field in self.model_fields.items()
            if getattr(self, attribute_name, None) is None
        )
        excluded_fields = hidden_fields.union(unset_fields)
        kwargs.setdefault("exclude", excluded_fields)
        return super().model_dump(**kwargs)

    @classmethod
    def get_module_id(cls) -> int:
        """
        Get the module ID for the model.

        :return: Module ID #
        :rtype: int
        """
        return cls._module_id.default

    @classmethod
    def get_module_slug(cls) -> str:
        """
        Get the module slug for the model.

        :return: Module slug
        :rtype: str
        """
        return cls._module_slug.default

    @classmethod
    def get_module_string(cls) -> str:
        """
        Get the module name for the model.

        :return: Module name
        :rtype: str
        """
        return cls._module_string.default or cls.get_module_slug()

    @classmethod
    def get_unique_fields(cls) -> list[str]:
        """
        Get the unique fields for the model.

        :return: Unique fields
        :rtype: list[str]
        """
        return cls._unique_fields.default

    @classmethod
    def _get_endpoints(cls) -> ConfigDict:
        """
        Get the endpoints for the API.

        :return: A dictionary of endpoints
        :rtype: ConfigDict
        """
        endpoints = ConfigDict(  # type: ignore
            get=cls._module_slug_id_url.default,
            insert="/api/{model_slug}/",
            update=cls._module_slug_id_url.default,
            delete=cls._module_slug_id_url.default,
            list="/api/{model_slug}/getList",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",
        )
        endpoints.update(cls._get_additional_endpoints())
        return endpoints

    def __repr__(self) -> str:
        """
        Override the default repr method to return a string representation of the object.

        :return: String representation of the object
        :rtype: str
        """
        return f"<{self.__str__()}>"

    def __str__(self) -> str:
        """
        Override the default str method to return a string representation of the object.

        :return: String representation of the object
        :rtype: str
        """
        fields = (
            "\n  "
            + "\n  ".join(
                f"{name}={value!r},"
                for name, value in self.dict().items()
                # if value is not None
            )
            + "\n"
        )
        return f"{self.__class__.__name__}({fields})"

    def find_by_unique(self, parent_id_field: Optional[str] = None) -> Optional[T]:
        """
        Find a unique instance of the object.

        :param Optional[str] parent_id_field: The parent ID field, defaults to None
        :raises NotImplementedError: If the method is not implemented
        :return: The instance or None if not found
        :rtype: Optional[T]
        """
        if not self.get_unique_fields():
            raise NotImplementedError(f"_unique_fields not defined for {self.__class__.__name__}")

        parent_id = None
        if parent_id_field:
            parent_id = getattr(self, parent_id_field, None)

        if not parent_id:
            parent_id = getattr(self, self._parent_id_field, None)

        if not parent_id:
            if parent_id == 0:
                raise ValueError(f"Parent ID is 0 for {self.__class__.__name__}")
            raise NotImplementedError(
                f"parentControlId or an alternative parent ID field not defined for {self.__class__.__name__}"
            )

        parent_module = getattr(self, "parentModule", getattr(self, "parent_module", ""))
        for instance in self.get_all_by_parent(parent_id=parent_id, parent_module=parent_module):
            if all(getattr(instance, field) == getattr(self, field) for field in self.get_unique_fields()):
                return instance
        return None

    def get_or_create(self: T) -> T:
        """
        Get or create an instance.

        :return: The instance
        :rtype: T
        """
        instance = self.find_by_unique()
        if instance:
            return instance
        else:
            return self.create()

    def create_or_update(self: T, cache_dict: Optional[Dict[str, int]] = None) -> T:
        """
        Create or update an instance. Use a map to cache and retrieve instances based on unique fields.

        :param Optional[Dict[str, T]] cache_dict: A dictionary to cache instances by a unique key, defaults to None
        :return: The instance of the class
        :rtype: T
        """
        # Generate a unique key based on the unique fields of the model
        unique_key = tuple(
            getattr(self, field) for field in self.get_unique_fields() if getattr(self, field, None) is not None
        )
        unique_key_str = "_".join(map(str, unique_key))  # Convert tuple to a string key

        if cache_dict is not None and unique_key_str in cache_dict:
            # If the instance is in the map, return it directly
            self.id = cache_dict[unique_key_str]
            return self.save()

        # If not found in the map, find the instance by unique fields
        instance = self.find_by_unique()

        if instance:
            # Update the instance
            self.id = instance.id
            if hasattr(self, "dateCreated"):
                self.dateCreated = instance.dateCreated
            updated_instance = self.save()
            if cache_dict is not None:
                cache_dict[unique_key_str] = updated_instance.id
            return updated_instance
        else:
            # Create a new instance
            created_instance = self.create()
            if cache_dict is not None:
                cache_dict[unique_key_str] = created_instance.id
            return created_instance

    @classmethod
    def _handle_list_response(
        cls, response: Response, suppress_error: bool = False, override_values: Optional[Dict] = None
    ) -> List[T]:
        """
        Handles the response for a list of items from an API call.

        This method processes the response object to extract a list of items. If the response is successful and contains
        a list of items (either directly or within a 'items' key for JSON responses), it returns a list of class instances
        created from the items. If the response is unsuccessful or does not contain any items, it logs an error and returns an empty list.

        :param Response response: The response
        :param bool suppress_error: Whether to suppress the error, defaults to False
        :param Optional[Dict] override_values: Override values, defaults to None
        :return: A list of class instances created from the response items
        :rtype: List[T]
        """
        logger.debug(f"Handling list response with status_code {response.status_code if response else ''}")

        if cls._is_response_invalid(response):
            logger.debug("No response or status code 204, 404, or 400")
            return []

        if response.ok and response.status_code != 400:
            items = cls._extract_items(response)
            cls._apply_override_values(items, override_values)
            return cls._create_objects_from_items(items)

        cls._log_response_error(response, suppress_error)
        return []

    @staticmethod
    def _is_response_invalid(response: Response) -> bool:
        """
        Check if the response is invalid.
        :param Response response: The response
        :return: True if the response is invalid, False otherwise
        :rtype: bool
        """
        # regscale is sending ok with 400 status code for some reason
        return not response or response.status_code in [204, 404]

    @staticmethod
    def _extract_items(response: Response) -> List[Dict]:
        """
        Extract items from the response.
        :param Response response: The response
        :return: A list of items
        :rtype: List[Dict]
        """
        json_response = response.json()
        if isinstance(json_response, dict) and "items" in json_response:
            return json_response.get("items", [])
        return json_response

    @staticmethod
    def _apply_override_values(items: List[Dict], override_values: Optional[Dict]) -> None:
        """
        Apply override values to the items.
        :param List[Dict] items: List of items
        :param Optional[Dict] override_values: Override values, defaults to None
        :rtype: None
        """
        if override_values:
            for item in items:
                for key, value in override_values.items():
                    item[key] = value

    @classmethod
    def _create_objects_from_items(cls, items: List[Dict]) -> List[T]:
        """
        Create objects from items using threading to improve performance.
        :param List[Dict] items: List of items
        :return: List of class instances created from the items
        :rtype: List[T]
        """
        from concurrent.futures import ThreadPoolExecutor

        def fetch_object(item):
            return cls.get_object(object_id=item["id"])

        if cls._get_objects_for_list.default:
            with ThreadPoolExecutor(max_workers=1) as executor:
                objects = list(executor.map(fetch_object, items))
            return cast(List[T], objects)
        return cast(List[T], [cls(**item) for item in items])

    @classmethod
    def _log_response_error(cls, response: Response, suppress_error: bool) -> None:
        """
        Log an error message for the response.
        :param Response response: The response
        :param bool suppress_error: Whether to suppress the error
        """
        if not suppress_error:
            logger.error(f"Error in response: {response.status_code}, {response.text}")

    @classmethod
    def _handle_response(cls, response: Response) -> Optional[T]:
        """
        Handles the response for a single item from an API call.

        This method processes the response object to extract a single item. If the response is successful and contains
        an item, it returns an instance of the class created from the item. If the response is unsuccessful or does not
        contain an item, it logs an error and returns None.

        :param Response response: The response object from the API call.
        :return: An instance of the class created from the response item, or None if unsuccessful.
        :rtype: Optional[T]
        """
        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            return cast(T, cls(**response.json()))
        else:
            logger.error(f"Failed to get {cls.get_module_slug()} for {cls.__name__}")
            return None

    @classmethod
    def _handle_meta_response(cls, response: Response) -> Optional[Dict[str, Union[int, List[T]]]]:
        """
        Handles the meta response for an api call using RegScale's query helper API.

        This method processes the response object to extract a page of items. The item dicts are converted to instances
        of T

        :param Response response: The response object from the API call.
        :return: A dict of total items and a list of the class created from each response item, or None if unsuccessful.
        :rtype: Optional[Dict[str, Union[int, List[T]]]]
        """
        data = {}
        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            data["totalItems"] = response.json()["totalItems"] if "totalItems" in response.json() else 0
            items = (
                [cast(T, cls(**item)) for item in response.json()["items"] if item]
                if "items" in response.json()
                else []
            )
            data["items"] = items
            return data
        else:
            logger.error(f"Failed to get {cls.get_module_slug()} for {cls.__name__}")
            return None

    @classmethod
    def _handle_graph_response(cls, response: Dict[Any, Any], child: Optional[Any] = None) -> List[T]:
        """
        Handle graph response

        :param Dict[Any, Any] response: Response from API
        :param Optional[Any] child: Child object, defaults to None
        :return: List of RegScale model objects
        :rtype: List[T]
        """
        items = []
        for k, v in response.items():
            if hasattr(v, "items"):
                for o in v["items"]:
                    if child:
                        items.append(cast(T, cls(**o[child])))
                    else:
                        items.append(cast(T, cls(**o)))
        return items

    @classmethod
    def get_field_names(cls) -> List[str]:
        """
        Get the field names for the Asset model.

        :return: List of field names
        :rtype: List[str]
        """
        return [x for x in get_type_hints(cls).keys() if not x.startswith("_")]

    @classmethod
    def build_graphql_fields(cls) -> str:
        """
        Dynamically builds a GraphQL query for a given Pydantic model class.

        :return: A string representing the GraphQL query.
        :rtype: str
        """
        return "\n".join(x for x in cls.get_field_names() if x not in cls._exclude_graphql_fields.default)

    @classmethod
    def get_by_parent(cls, parent_id: int, parent_module: str) -> List[T]:
        """
        Get a list of objects by parent.

        DEPRECATED: This method will be removed in future versions. Use 'get_all_by_parent' instead.

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A list of objects
        :rtype: List[T]
        """
        warnings.warn(
            "The method 'get_by_parent' is deprecated and will be removed in future versions. "
            "Use 'get_all_by_parent' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return cls.get_all_by_parent(parent_id, parent_module)

    @classmethod
    def get_all_by_parent(
        cls,
        parent_id: int,
        parent_module: Optional[str] = None,
        search: Optional[Search] = None,
    ) -> List[T]:
        """
        Get a list of objects by parent.

        :param int parent_id: The ID of the parent
        :param Optional[str] parent_module: The module of the parent
        :param Optional[Search] search: The search object, defaults to None
        :return: A list of objects
        :rtype: List[T]
        """
        if "get_all_by_search" in cls._get_endpoints() and parent_id and parent_module and not search:
            logger.debug("Using get_all_by_search")
            # Use get_all_by_search if available for the module
            search = Search(parentID=parent_id, module=parent_module)
        if search:
            return cls._handle_looping_response(search)

        try:
            endpoint = cls.get_endpoint("get_all_by_parent").format(intParentID=parent_id, strModule=parent_module)
        except ValueError as e:
            logger.error(f"Failed to get endpoint: {e}")
            return []

        return cls._handle_list_response(cls._api_handler.get(endpoint=endpoint))

    @classmethod
    def _handle_looping_response(cls, search: Search, page: int = 1, page_size: int = 500) -> List[T]:
        """
        Handles the response for a list of items from an API call.

        :param Search search: The search object
        :param int page: The starting page, defaults to 1
        :param int page_size: The number of items per page, defaults to 500
        :return: A list of objects
        :rtype: List[T]
        """
        items = []
        this_search = copy.deepcopy(search)
        this_search.page = page
        this_search.pageSize = page_size

        while True:
            data: dict = cls._handle_meta_response(
                cls._api_handler.post(
                    endpoint=cls.get_endpoint("get_all_by_search"),
                    data=this_search.model_dump(),
                )
            )
            try:
                if not data.get("items"):
                    break
            except AttributeError:
                break

            items.extend(data["items"])
            this_search.page += 1

        return items

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the API.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict()

    @classmethod
    def get_endpoint(cls, endpoint_type: str) -> str:
        """
        Get the endpoint for a specific type.

        :param str endpoint_type: The type of endpoint
        :raises ValueError: If the endpoint type is not found
        :return: The endpoint
        :rtype: str
        """
        endpoint = cls._get_endpoints().get(endpoint_type, "na")
        if not endpoint or endpoint == "na":
            logger.error(f"{cls.__name__} does not have endpoint {endpoint_type}")
            raise ValueError(f"Endpoint {endpoint_type} not found")
        endpoint = str(endpoint).replace("{model_slug}", cls.get_module_slug())
        return endpoint

    def create(self: T) -> T:
        """
        Insert a RegScale object.

        :raises APIInsertionError: If the insert fails
        :return: The created object
        :rtype: T
        """
        endpoint = self.get_endpoint("insert")
        response = self._api_handler.post(endpoint=endpoint, data=self.dict())
        if response and response.ok:
            return self.__class__(**response.json())
        else:
            logger.error(
                f"Failed to update {self.__class__.__name__}\n Endpoint: {endpoint}\n Payload: {json.dumps(self.dict(), indent=2)}"
            )
            if response and not response.ok:
                logger.error(f"Response Error: Code #{response.status_code}: {response.reason}\n{response.text}")
            if response is None:
                error_msg = "Response was None"
                logger.error(error_msg)
                raise APIInsertionError(error_msg)
            error_msg = f"Response Code: {response.status_code}:{response.reason} - {response.text}"
            logger.error(error_msg)
            raise APIInsertionError(error_msg)

    @classmethod
    def batch_create(cls, items: List[T]) -> List[T]:
        """
        Use bulk_create method to create assets.

        :param List[T] items: List of Asset Objects
        :return: List of cls items from RegScale
        :rtype: List[T]
        """
        create_progress = create_progress_object()
        batch_size = 100
        results = []
        total_items = len(items)
        create_job = create_progress.add_task(
            f"[#f68d1f]Creating {total_items} RegScale {cls.__name__}s...",
            total=total_items,
        )
        with create_progress:
            for i in range(0, total_items, batch_size):
                batch = items[i : i + batch_size]
                results.extend(
                    cls._handle_list_response(
                        cls._api_handler.post(
                            endpoint=cls.get_endpoint("batch_create"),
                            data=[item.dict() for item in batch],
                        )
                    )
                )
                progress_increment = min(batch_size, total_items - i)
                create_progress.advance(create_job, progress_increment)
        return results

    @classmethod
    def batch_update(cls, items: List[T]) -> List[T]:
        """
        Use bulk_create method to create assets.

        :param List[T] items: List of cls Objects
        :return: List of cls items from RegScale
        :rtype: List[T]
        """
        update_progress = create_progress_object()
        batch_size = 100
        results = []
        total_items = len(items)
        update_job = update_progress.add_task(
            f"[#f68d1f]Updating {total_items} RegScale {cls.__name__}s...",
            total=total_items,
        )
        with update_progress:
            for i in range(0, total_items, batch_size):
                batch = items[i : i + batch_size]
                results.extend(
                    cls._handle_list_response(
                        cls._api_handler.put(
                            endpoint=cls.get_endpoint("batch_update"),
                            data=[item.dict() for item in batch],
                        )
                    )
                )
                progress_increment = min(batch_size, total_items - i)
                update_progress.advance(update_job, progress_increment)
        return results

    def save(self: T) -> T:
        """
        Save changes of the model instance.

        :raises APIUpdateError: If the update fails
        :return: The updated object
        :rtype: T
        """
        if self.has_changed():
            logger.debug(f"Updating {self.__class__.__name__} {getattr(self, 'id', '')}")
            endpoint = self.get_endpoint("update").format(id=self.id, data=self.dict())
            response = self._api_handler.put(endpoint=endpoint, data=self.dict())
            if hasattr(response, "ok") and response.ok:
                return self.__class__(**response.json())
            else:
                logger.error(
                    f"Failed to update {self.__class__.__name__}\n Endpoint: {endpoint}\n Payload: {json.dumps(self.dict(), indent=2)}"
                )
                if response is not None:
                    raise APIUpdateError(f"Response Code: {response.status_code} - {response.text}")
                else:
                    raise APIUpdateError("Response was None")
        else:
            logger.debug(f"No changes detected for {self.__class__.__name__} {getattr(self, 'id', '')}")
            return self

    @classmethod
    def get_object(cls, object_id: Union[str, int]) -> Optional[T]:
        """
        Get a RegScale object by ID.

        :param Union[str, int] object_id: The ID of the object
        :return: The object or None if not found
        :rtype: Optional[T]
        """
        response = cls._api_handler.get(endpoint=cls.get_endpoint("get").format(id=object_id))
        if response and response.ok:
            if response.json() and isinstance(response.json(), list):
                return cast(T, cls(**response.json()[0]))
            else:
                return cast(T, cls(**response.json()))
        else:
            logger.debug(f"Failing response: {response.status_code}: {response.reason} {response.text}")
            logger.warning(f"{cls.__name__}: No matching record found for ID: {cls.__name__} {object_id}")
            return None

    @classmethod
    def get_list(cls) -> List[T]:
        """
        Get a list of objects.

        :return: A list of objects
        :rtype: List[T]
        """
        response = cls._api_handler.get(endpoint=cls.get_endpoint("list"))
        if response.ok:
            return cast(List[T], [cls.get_object(object_id=sp["id"]) for sp in response.json()])
        else:
            logger.error(f"Failed to get list of {cls.__name__} {response}")
            return []

    def delete(self) -> bool:
        """
        Delete an object in RegScale.

        :return: True if successful, False otherwise
        :rtype: bool
        """
        response = self._api_handler.delete(endpoint=self.get_endpoint("delete").format(id=self.id))
        if response.ok:
            return True
        else:
            logger.error(f"Failed to delete {self.__class__.__name__} {self.dict()}")
            return False

    @classmethod
    def from_dict(cls, obj: Dict[str, Any], copy_object: bool = False) -> T:  # type: ignore
        """
        Create RegScale Model from dictionary

        :param Dict[str, Any] obj: dictionary
        :param bool copy_object: Whether to copy the object without an id, defaults to False
        :return: Instance of RegScale Model
        :rtype: T
        """
        copy_obj = copy.copy(obj)
        if "id" in copy_obj and copy_object:
            del copy_obj["id"]
        return cast(T, cls(**copy_obj))

    @classmethod
    def parse_response(cls, response: Response, suppress_error: bool = False) -> Optional[T]:
        """
        Parse a response.

        :param Response response: The response
        :param bool suppress_error: Whether to suppress the error, defaults to False
        :return: An object or None
        :rtype: Optional[T]
        """
        if response and response.ok:
            logger.info(json.dumps(response.json(), indent=4))
            return cast(T, cls(**response.json()))
        else:
            cls.log_response_error(response=response, suppress_error=suppress_error)
            return None

    @classmethod
    def log_response_error(cls, response: Response, suppress_error: bool = False) -> None:
        """
        Log an error message.

        :param Response response: The response
        :param bool suppress_error: Whether to suppress the error, defaults to False
        :raises APIResponseError: If the response is None
        :rtype: None
        """
        message = ""
        if response is not None:
            message = f"{cls.__name__}: - StatusCode: {response.status_code} Reason: {response.reason}"
            if response.text:
                message += f" - {response.text}"
            if suppress_error:
                logger.error(message)
            else:
                raise APIResponseError(message)
        else:
            if suppress_error:
                logger.error(f"{cls.__name__}: Response was None")
            else:
                raise APIResponseError(f"{cls.__name__}: Response was None")
