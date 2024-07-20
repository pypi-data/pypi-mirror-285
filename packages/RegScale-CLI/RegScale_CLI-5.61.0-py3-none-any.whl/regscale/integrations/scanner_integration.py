#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Scanner Integration Class """

import concurrent.futures
import dataclasses
import enum
import logging
import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from multiprocessing import Manager
from typing import Any, Generic, Iterator, List, Optional, Tuple, TypeVar, Union

from rich.progress import Progress, TaskID

from regscale.core.app.utils.api_handler import APIHandler
from regscale.core.app.utils.app_utils import create_progress_object, get_current_datetime
from regscale.core.app.utils.catalog_utils.common import objective_to_control_dot
from regscale.core.utils.date import date_str, days_from_today
from regscale.models import OpenIssueDict, regscale_models

logger = logging.getLogger(__name__)

K = TypeVar("K")  # Key type
V = TypeVar("V")  # Value type

THREAD_MAX_WORKERS = 2


class ManagedDefaultDict(Generic[K, V]):
    def __init__(self, default_factory, manager=None):
        if manager is None:
            manager = Manager()
        self.store = manager.dict()
        self.default_factory = default_factory

    def __getitem__(self, key: Any) -> Any:
        """
        Get the item from the store

        :param Any key: Key to get the item from the store
        :return: Value from the store
        :rtype: Any
        """
        if key not in self.store:
            self.store[key] = self.default_factory()
        return self.store[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set the item in the store

        :param Any key: Key to set the item in the store
        :param Any value: Value to set in the store
        :rtype: None
        """
        self.store[key] = value

    def __contains__(self, key: Any) -> bool:
        """
        Check if the key is in the store

        :param Any key: Key to check in the store
        :return: Whether the key is in the store
        :rtype: bool
        """
        return key in self.store

    def __len__(self) -> int:
        """
        Get the length of the store

        :return: Number of items in the store
        :rtype: int
        """
        return len(self.store)

    def get(self, key: Any, default: Optional[Any] = None) -> Optional[Any]:
        """
        Get the value from the store

        :param Any key: Key to get the value from the store
        :param Optional[Any] default: Default value to return if the key is not in the store, defaults to None
        :return: The value from the store, or the default value
        :rtype: Optional[Any]
        """
        if key not in self.store:
            return default
        return self.store[key]

    def items(self) -> Any:
        """
        Get the items from the store

        :return: Items from the store
        :rtype: Any
        """
        return self.store.items()

    def keys(self) -> Any:
        """
        Get the keys from the store

        :return: Keys from the store
        :rtype: Any
        """
        return self.store.keys()

    def values(self) -> Any:
        """
        Get the values from the store

        :return: Values in the store
        :rtype: Any
        """
        return self.store.values()

    def update(self, *args: Tuple, **kwargs: dict) -> None:
        """
        Update the store

        :param Tuple *args: Args to pass when updating the store
        :param dict **kwargs: Keyword arguments to pass when updating the store
        :rtype: None
        """
        self.store.update(*args, **kwargs)


@dataclasses.dataclass
class IntegrationAsset:
    """
    Dataclass for integration assets.

    Represents an asset to be integrated, including its metadata and associated components.
    If a component does not exist, it will be created based on the names provided in ``component_names``.

    :param str name: The name of the asset.
    :param str identifier: A unique identifier for the asset.
    :param str asset_type: The type of the asset.
    :param str asset_category: The category of the asset.
    :param str component_type: The type of the component, defaults to ``ComponentType.Hardware``.
    :param Optional[int] parent_id: The ID of the parent asset, defaults to None.
    :param Optional[str] parent_module: The module of the parent asset, defaults to None.
    :param str status: The status of the asset, defaults to "Active (On Network)".
    :param str date_last_updated: The last update date of the asset, defaults to the current datetime.
    :param Optional[str] asset_owner_id: The ID of the asset owner, defaults to None.
    :param Optional[str] mac_address: The MAC address of the asset, defaults to None.
    :param Optional[str] fqdn: The Fully Qualified Domain Name of the asset, defaults to None.
    :param Optional[str] ip_address: The IP address of the asset, defaults to None.
    :param List[str] component_names: A list of strings that represent the names of the components associated with the
    asset, components will be created if they do not exist.
    """

    name: str
    identifier: str
    asset_type: str
    asset_category: str
    component_type: str = regscale_models.ComponentType.Hardware
    parent_id: Optional[int] = None
    parent_module: Optional[str] = None
    status: str = "Active (On Network)"
    date_last_updated: str = dataclasses.field(default_factory=get_current_datetime)
    asset_owner_id: Optional[str] = None
    mac_address: Optional[str] = None
    fqdn: Optional[str] = None
    ip_address: Optional[str] = None
    component_names: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class IntegrationFinding:
    """
    Dataclass for integration findings.

    :param list[str] control_labels: A list of control labels associated with the finding.
    :param str title: The title of the finding.
    :param str category: The category of the finding.
    :param regscale_models.IssueSeverity severity: The severity of the finding, based on regscale_models.IssueSeverity.
    :param str description: A description of the finding.
    :param regscale_models.ControlTestResultStatus status: The status of the finding, based on
    regscale_models.ControlTestResultStatus.
    :param str pri[ority: The priority of the finding, defaults to "Medium".
    :param str issue_type: The type of issue, defaults to "Risk".
    :param str issue_title: The title of the issue, defaults to an empty string.
    :param str date_created: The creation date of the finding, defaults to the current datetime.
    :param str due_date: The due date of the finding, defaults to 60 days from the current datetime.
    :param str date_last_updated: The last update date of the finding, defaults to the current datetime.
    :param str external_id: An external identifier for the finding, defaults to an empty string.
    :param str gaps: A description of any gaps identified, defaults to an empty string.
    :param str observations: Observations related to the finding, defaults to an empty string.
    :param str evidence: Evidence supporting the finding, defaults to an empty string.
    :param str identified_risk: The risk identified by the finding, defaults to an empty string.
    :param str impact: The impact of the finding, defaults to an empty string.
    :param str recommendation_for_mitigation: Recommendations for mitigating the finding, defaults to an empty string.
    :param str asset_identifier: The identifier of the asset associated with the finding, defaults to an empty string.
    :param Optional[str] cci_ref: The Common Configuration Enumeration reference for the finding, defaults to None.
    :param str rule_id: The rule ID of the finding, defaults to an empty string.
    :param str rule_version: The version of the rule associated with the finding, defaults to an empty string.
    :param str results: The results of the finding, defaults to an empty string.
    :param Optional[str] comments: Additional comments related to the finding, defaults to None.
    :param str baseline: The baseline of the finding, defaults to an empty string.
    :param str poam_comments: Comments related to the Plan of Action and Milestones (POAM) for the finding, defaults to
    an empty string.
    """

    control_labels: List[str]
    title: str
    category: str
    severity: regscale_models.IssueSeverity
    description: str
    status: Union[regscale_models.ControlTestResultStatus, regscale_models.ChecklistStatus]
    priority: str = "Medium"

    # Vulns
    first_seen: str = dataclasses.field(default_factory=get_current_datetime)
    last_seen: str = dataclasses.field(default_factory=get_current_datetime)
    cve: Optional[str] = None
    cvss_v3_score: Optional[float] = None
    cvss_v2_score: Optional[float] = None
    ip_address: Optional[str] = None
    plugin_id: Optional[str] = None
    plugin_name: Optional[str] = None
    dns: Optional[str] = None
    severity_int: int = 0

    # Issues
    issue_title: str = ""
    issue_type: str = "Risk"
    date_created: str = dataclasses.field(default_factory=get_current_datetime)
    date_last_updated: str = dataclasses.field(default_factory=get_current_datetime)
    due_date: str = date_str(days_from_today(60))
    external_id: str = ""
    gaps: str = ""
    observations: str = ""
    evidence: str = ""
    identified_risk: str = ""
    impact: str = ""
    recommendation_for_mitigation: str = ""
    asset_identifier: str = ""
    cci_ref: Optional[str] = None
    rule_id: str = ""
    rule_version: str = ""
    results: str = ""
    comments: Optional[str] = None
    baseline: str = ""
    poam_comments: Optional[str] = None

    def __eq__(self, other: Any) -> bool:
        """
        Check if the finding is equal to another finding

        :param Any other: The other finding to compare
        :return: Whether the findings are equal
        :rtype: bool
        """
        if not isinstance(other, IntegrationFinding):
            return NotImplemented
        return (self.title, self.category, self.external_id) == (other.title, other.category, other.external_id)

    def __hash__(self) -> hash:
        """
        Get the hash of the finding

        :return: Hash of the finding
        :rtype: hash
        """
        return hash((self.title, self.category, self.external_id))


class ScannerIntegrationType(str, enum.Enum):
    """
    Enumeration for scanner integration types.
    """

    CHECKLIST = "checklist"
    CONTROL_TEST = "control_test"


class ScannerIntegration(ABC):
    """
    Abstract class for scanner integrations.

    :param int plan_id: The ID of the security plan
    """

    # Basic configuration options
    options_map_assets_to_components: bool = False
    type = ScannerIntegrationType.CONTROL_TEST
    title = "Scanner Integration"
    asset_identifier_field = ""

    # Progress trackers
    asset_progress: Progress
    finding_progress: Progress

    # Processing counts
    num_assets_to_process: Optional[int] = None
    num_findings_to_process: Optional[int] = None

    # Error handling
    errors: List[str] = []

    # Mapping dictionaries
    finding_status_map: dict[Any, regscale_models.ChecklistStatus] = {}
    finding_severity_map: dict[Any, regscale_models.IssueSeverity] = {}
    asset_map: dict[str, regscale_models.Asset] = {}
    # cci_to_control_map: dict[str, set[int]] = {}
    control_implementation_id_map: dict[str, int] = {}
    control_map: dict[int, str] = {}
    control_id_to_implementation_map: dict[int, int] = {}

    # Existing issues map
    existing_issue_ids_by_implementation_map: dict[int, List[OpenIssueDict]] = defaultdict(list)

    concurrency_lock = threading.Lock()

    def __init__(self, plan_id: int):
        manager = Manager()
        self.plan_id = plan_id

        self.components: list[Any] = manager.list()
        self.asset_map_by_identifier: dict[str, regscale_models.Asset] = manager.dict()
        self.asset_map_by_identifier.update(self.get_asset_map())

        self.existing_issues_map: dict[int, List[regscale_models.Issue]] = manager.dict()
        self.checklist_asset_map: ManagedDefaultDict[int, List[regscale_models.Checklist]] = ManagedDefaultDict(
            list, manager
        )
        self.components_by_title: dict[str, regscale_models.Component] = manager.dict()
        self.control_tests_map: ManagedDefaultDict[int, regscale_models.ControlTest] = ManagedDefaultDict(list, manager)

        self.implementation_objective_map: dict[str, int] = manager.dict()
        self.implementation_option_map: dict[str, int] = manager.dict()
        self.control_implementation_map: dict[int, regscale_models.ControlImplementation] = manager.dict()

        self.control_implementation_id_map = regscale_models.ControlImplementation.get_control_label_map_by_plan(
            plan_id=plan_id
        )
        self.control_map = {v: k for k, v in self.control_implementation_id_map.items()}
        self.existing_issue_ids_by_implementation_map = regscale_models.Issue.get_open_issues_ids_by_implementation_id(
            plan_id=plan_id
        )
        self.control_id_to_implementation_map = regscale_models.ControlImplementation.get_control_id_map_by_plan(
            plan_id=plan_id
        )
        self.cci_to_control_map: dict[str, set[int]] = manager.dict()
        self.cci_to_control_map_lock = threading.Lock()

        self.assessment_map: dict[int, regscale_models.Assessment] = {}
        self.assessor_id = self.get_assessor_id()
        self.asset_progress = create_progress_object()
        self.finding_progress = create_progress_object()

    @staticmethod
    def get_assessor_id() -> str:
        """
        Gets the ID of the assessor

        :return: The ID of the assessor
        :rtype: str
        """

        api_handler = APIHandler()
        return api_handler.get_user_id()

    def get_cci_to_control_map(self) -> dict[str, set[int]]:
        """
        Gets the CCI to control map

        :return: The CCI to control map
        :rtype: dict[str, set[int]]
        """
        with self.cci_to_control_map_lock:
            if any(self.cci_to_control_map):
                return self.cci_to_control_map
            logger.debug("Getting CCI to control map...")
            self.cci_to_control_map = regscale_models.map_ccis_to_control_ids(parent_id=self.plan_id)
            return self.cci_to_control_map

    def get_control_to_cci_map(self) -> dict[int, set[str]]:
        """
        Gets the security control id to CCI map

        :return: The security control id to CCI map
        :rtype: dict[int, set[str]]
        """
        control_id_to_cci_map = defaultdict(set)
        for cci, control_ids in self.get_cci_to_control_map().items():
            for control_id in control_ids:
                control_id_to_cci_map[control_id].add(cci)
        return control_id_to_cci_map

    def get_control_implementation_id_for_cci(self, cci: Optional[str]) -> Optional[int]:
        """
        Gets the control implementation ID for a CCI

        :param Optional[str] cci: The CCI
        :return: The control ID
        :rtype: Optional[int]
        """
        cci_to_control_map = self.get_cci_to_control_map()
        if cci not in cci_to_control_map:
            cci = "CCI-000366"
        for control_id in cci_to_control_map.get(cci, set()):
            return self.control_id_to_implementation_map.get(control_id)
        return None

    def get_asset_map(self) -> dict[str, regscale_models.Asset]:
        """
        Retrieves a mapping of asset identifiers to their corresponding Asset objects. This method supports two modes
        of operation based on the `options_map_assets_to_components` flag. If the flag is set, it fetches the asset
        map using a specified key field from the assets associated with the given plan ID. Otherwise, it constructs
        the map by fetching all assets under the specified plan and using the asset identifier field as the key.

        :return: A dictionary mapping asset identifiers to Asset objects.
        :rtype: dict[str, regscale_models.Asset]
        """
        if self.options_map_assets_to_components:
            # Fetches the asset map directly using a specified key field.
            return regscale_models.Asset.get_map(plan_id=self.plan_id, key_field=self.asset_identifier_field)
        else:
            # Constructs the asset map by fetching all assets under the plan and using the asset identifier field as
            # the key.
            return {  # type: ignore
                getattr(x, self.asset_identifier_field): x
                for x in regscale_models.Asset.get_all_by_parent(
                    parent_id=self.plan_id, parent_module=regscale_models.SecurityPlan.get_module_string()
                )
            }

    @abstractmethod
    def fetch_findings(self, *args: Tuple, **kwargs: dict) -> List[IntegrationFinding]:
        """
        Fetches findings from the integration

        :param Tuple *args: Tuple of arguments
        :param dict **kwargs: Dictionary of keyword arguments
        :return: A list of findings
        :rtype: List[IntegrationFinding]
        """
        pass

    @abstractmethod
    def fetch_assets(self, *args: Tuple, **kwargs: dict) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from the integration

        :param Tuple *args: Tuple of arguments
        :param dict **kwargs: Dictionary of keyword arguments
        :return: An iterator of assets
        :rtype: Iterator[IntegrationAsset]
        """
        pass

    def get_finding_status(self, status: Optional[str]) -> regscale_models.ChecklistStatus:
        """
        Gets the RegScale checklist status based on the integration finding status

        :param Optional[str] status: The status of the finding
        :return: The RegScale checklist status
        :rtype: regscale_models.ChecklistStatus
        """
        return self.finding_status_map.get(status, regscale_models.ChecklistStatus.NOT_REVIEWED)

    def get_finding_severity(self, severity: Optional[str]) -> regscale_models.IssueSeverity:
        """
        Gets the RegScale issue severity based on the integration finding severity

        :param Optional[str] severity: The severity of the finding
        :return: The RegScale issue severity
        :rtype: regscale_models.IssueSeverity
        """
        return self.finding_severity_map.get(severity, regscale_models.IssueSeverity.NotAssigned)

    def get_or_create_assessment(self, control_implementation_id: int) -> regscale_models.Assessment:
        """
        Gets or creates a RegScale assessment

        :param int control_implementation_id: The ID of the control implementation
        :return: The assessment
        :rtype: regscale_models.Assessment
        """
        logger.info(f"Getting or creating assessment for control implementation {control_implementation_id}")
        assessment: Optional[regscale_models.Assessment] = self.assessment_map.get(control_implementation_id)
        if assessment:
            logger.debug(
                f"Found cached assessment {assessment.id} for control implementation {control_implementation_id}"
            )
        else:
            logger.debug(f"Assessment not found for control implementation {control_implementation_id}")
            assessment = regscale_models.Assessment(
                plannedStart=get_current_datetime(),
                plannedFinish=get_current_datetime(),
                status=regscale_models.AssessmentStatus.COMPLETE.value,
                assessmentResult=regscale_models.AssessmentResultsStatus.FAIL.value,
                actualFinish=get_current_datetime(),
                leadAssessorId=self.assessor_id,
                parentId=control_implementation_id,
                parentModule=regscale_models.ControlImplementation.get_module_string(),
                title=f"{self.title} Assessment",
                assessmentType=regscale_models.AssessmentType.QA_SURVEILLANCE.value,
            ).create()
        self.assessment_map[control_implementation_id] = assessment
        return assessment

    def get_components(self) -> List[regscale_models.Component]:
        """
        Get all components from the integration

        :return: A list of components
        :rtype: List[regscale_models.Component]
        """
        if any(self.components):
            return self.components
        self.components = regscale_models.Component.get_all_by_parent(
            parent_id=self.plan_id,
            parent_module=regscale_models.SecurityPlan.get_module_string(),
        )
        return self.components

    def get_component_by_title(self) -> dict:
        """
        Get all components from the integration

        :return: A dictionary of components
        :rtype: dict
        """
        return {component.title: component for component in self.get_components()}

    # Asset Methods
    def set_asset_defaults(self, asset: IntegrationAsset) -> IntegrationAsset:
        """
        Set default values for the asset (Thread Safe)

        :param IntegrationAsset asset: The integration asset
        :return: The asset with which defaults should be set
        :rtype: IntegrationAsset
        """
        if not asset.asset_owner_id:
            asset.asset_owner_id = self.get_assessor_id()
        if not asset.status:
            asset.status = "Active (On Network)"
        return asset

    def process_asset(
        self,
        asset: IntegrationAsset,
        loading_assets: TaskID,
        progress_lock: threading.Lock,
    ) -> None:
        """
        Safely processes a single asset in a concurrent environment. This method ensures thread safety
        by utilizing a threading lock. It assigns default values to the asset if necessary, maps the asset
        to components if specified, and updates the progress of asset loading.
        (Thread Safe)

        :param IntegrationAsset asset: The integration asset to be processed.
        :param TaskID loading_assets: The identifier for the task tracking the progress of asset loading.
        :param threading.Lock progress_lock: A lock to ensure thread-safe updates to the progress tracking.
        :rtype: None
        """

        # Assign default values to the asset if they are not already set.
        asset = self.set_asset_defaults(asset)

        # If mapping assets to components is enabled and the asset has associated component names,
        # attempt to update or create each asset under its respective component.
        if self.options_map_assets_to_components and any(asset.component_names):
            for component_name in asset.component_names:
                self.update_or_create_asset(asset, component_name)
        else:
            # If no component mapping is required, add the asset directly to the security plan without a component.
            self.update_or_create_asset(asset, None)

        with progress_lock:
            # Ensure the total number of assets to process is reflected in the task's total before advancing the
            # progress.
            if self.num_assets_to_process and self.asset_progress.tasks[loading_assets].total != float(
                self.num_assets_to_process
            ):
                self.asset_progress.update(loading_assets, total=self.num_assets_to_process)
            # Increment the progress for the asset loading task by one.
            self.asset_progress.advance(loading_assets, 1)

    def update_or_create_asset(
        self,
        asset: IntegrationAsset,
        component_name: Optional[str] = None,
    ) -> None:
        """
        This method either updates an existing asset or creates a new one within a thread-safe manner. It handles
        the asset's association with a component, creating the component if it does not exist.
        (Thread Safe)

        :param IntegrationAsset asset: The asset to be updated or created.
        :param Optional[str] component_name: The name of the component to associate the asset with. If None, the asset
                                             is added directly to the security plan without a component association.
        """
        component = None
        if component_name:
            logger.debug(f"Searching for component: {component_name}...")
            if not (component := self.components_by_title.get(component_name)):
                logger.debug(f"No existing component found with name {component_name}, proceeding to create it...")
                component = regscale_models.Component(
                    title=component_name,
                    componentType=asset.component_type,
                    securityPlansId=self.plan_id,
                    description=component_name,
                    componentOwnerId=self.get_assessor_id(),
                ).create()
                self.components.append(component)
            if component.securityPlansId:
                regscale_models.ComponentMapping(
                    componentId=component.id,
                    securityPlanId=component.securityPlansId,
                ).get_or_create()
            self.components_by_title[component_name] = component

        # Check if the asset already exists and update it if necessary, otherwise create a new asset.
        if existing_or_new_asset := self.find_existing_asset(asset):
            self.update_asset_if_needed(asset, existing_or_new_asset)
        else:
            existing_or_new_asset = self.create_new_asset(asset, component=component)

        # If the asset is associated with a component, create a mapping between them.
        if component:
            regscale_models.AssetMapping(
                assetId=existing_or_new_asset.id,
                componentId=component.id,
            ).get_or_create()

    def find_existing_asset(self, asset: IntegrationAsset) -> Optional[regscale_models.Asset]:
        """
        Searches for and retrieves an existing asset within the system that corresponds to the provided integration
        asset.
        This operation is performed in a thread-safe manner to ensure data integrity during concurrent access.
        (Thread Safe)

        :param IntegrationAsset asset: The integration asset for which an existing match is sought.
        :return: An instance of the matching existing asset if found; otherwise, None.
        :rtype: Optional[regscale_models.Asset]
        """
        return self.asset_map_by_identifier.get(asset.identifier)

    @staticmethod
    def update_asset_if_needed(asset: IntegrationAsset, existing_asset: regscale_models.Asset) -> None:
        """
        Updates an existing asset if any of its fields differ from the integration asset (Thread Safe)

        :param IntegrationAsset asset: The integration asset
        :param regscale_models.Asset existing_asset: The existing asset
        :rtype: None
        """
        is_updated = False
        if asset.asset_owner_id and existing_asset.assetOwnerId != asset.asset_owner_id:
            existing_asset.assetOwnerId = asset.asset_owner_id
            is_updated = True
        if asset.parent_id and existing_asset.parentId != asset.parent_id:
            existing_asset.parentId = asset.parent_id
            is_updated = True
        if asset.parent_module and existing_asset.parentModule != asset.parent_module:
            existing_asset.parentModule = asset.parent_module
            is_updated = True
        if existing_asset.assetType != asset.asset_type:
            existing_asset.assetType = asset.asset_type
            is_updated = True
        if existing_asset.status != asset.status:
            existing_asset.status = asset.status
            is_updated = True
        if existing_asset.assetCategory != asset.asset_category:
            existing_asset.assetCategory = asset.asset_category
            is_updated = True

        if is_updated:
            existing_asset.dateLastUpdated = asset.date_last_updated
            existing_asset.save()
            logger.debug(f"Updated asset {asset.identifier}")
        else:
            logger.debug(f"Asset {asset.identifier} is already up to date")

    def create_new_asset(
        self, asset: IntegrationAsset, component: Optional[regscale_models.Component]
    ) -> regscale_models.Asset:
        """
        This method is responsible for creating a new asset in the system based on the provided integration asset
        details. If a component is specified, the new asset will be associated with this component. Otherwise,
        it will be directly associated with the security plan. This process is executed in a thread-safe manner to
        ensure data integrity. (Thread Safe)

        :param IntegrationAsset asset: The integration asset from which the new asset will be created.
        :param Optional[regscale_models.Component] component: The component to which the new asset should be linked,
        or None if it should be linked directly to the security plan.
        :return: The newly created asset instance.
        :rtype: regscale_models.Asset
        """
        new_asset = regscale_models.Asset(
            name=asset.name,
            assetOwnerId=asset.asset_owner_id or "Unknown",
            parentId=component.id if component else self.plan_id,
            parentModule=(
                regscale_models.Component.get_module_string()
                if component
                else regscale_models.SecurityPlan.get_module_string()
            ),
            assetType=asset.asset_type,
            dateLastUpdated=asset.date_last_updated,
            status=asset.status,
            assetCategory=asset.asset_category,
        )
        if self.asset_identifier_field:
            setattr(new_asset, self.asset_identifier_field, asset.identifier)
        new_asset = new_asset.create()
        self.asset_map_by_identifier[asset.identifier] = new_asset
        logger.debug(f"Created new asset with identifier {asset.identifier}")

        # Create an AssetMapping if the new asset is associated with a component
        if component:
            regscale_models.AssetMapping(
                assetId=new_asset.id,
                componentId=component.id,
            ).get_or_create()

        return new_asset

    def update_regscale_assets(self, assets: Iterator[IntegrationAsset]) -> None:
        """
        Updates RegScale assets based on the integration assets

        :param Iterator[IntegrationAsset] assets: The integration assets
        :rtype: None
        """

        self.asset_map_by_identifier = regscale_models.Asset.get_map(
            plan_id=self.plan_id, key_field=self.asset_identifier_field
        )

        logger.info("Updating RegScale assets...")
        loading_assets = self.asset_progress.add_task(
            f"[#f8b737]Creating and updating assets from {self.title}.",
        )
        progress_lock = threading.Lock()

        # Initialize maps
        if self.options_map_assets_to_components:
            # Look up Component by title
            self.components_by_title = self.get_component_by_title()
        self.asset_map_by_identifier = self.get_asset_map()

        with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_MAX_WORKERS) as executor:
            future_to_asset = {
                executor.submit(
                    self.process_asset,
                    asset,
                    loading_assets,
                    progress_lock,
                ): asset
                for asset in assets
            }
            for future in concurrent.futures.as_completed(future_to_asset):
                asset = future_to_asset[future]
                try:
                    future.result()
                except Exception as exc:
                    self.log_error(f"An error occurred when processing asset {asset.name}: {exc}")

    # Finding Methods
    def create_issue_from_finding(
        self,
        title: str,
        parent_id: int,
        parent_module: str,
        finding: IntegrationFinding,
    ) -> regscale_models.Issue:
        """
        Creates a RegScale issue from a finding

        :param str title: The title of the issue
        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :param IntegrationFinding finding: The finding data
        :return: The created RegScale issue
        :rtype: regscale_models.Issue
        """
        issue_status = (
            regscale_models.IssueStatus.Closed
            if finding.status == regscale_models.ControlTestResultStatus.PASS
            else regscale_models.IssueStatus.Open
        )

        return regscale_models.Issue(
            parentId=parent_id,
            parentModule=parent_module,
            title=title[:450],  # Truncate to 450 characters
            dateCreated=finding.date_created,
            status=issue_status,
            severityLevel=finding.severity,
            issueOwnerId=self.assessor_id,
            securityPlanId=self.plan_id,
            identification="Vulnerability Assessment",
            dateFirstDetected=finding.date_created,
            dueDate=finding.due_date,
            description=finding.description,
            sourceReport="STIG",
            recommendedActions=finding.recommendation_for_mitigation,
            assetIdentifier=finding.asset_identifier,
            securityChecks=finding.external_id,
            remediationDescription=finding.recommendation_for_mitigation,
            otherIdentifier=finding.external_id,
            poamComments=finding.poam_comments,
            controlId=self.get_control_implementation_id_for_cci(finding.cci_ref),
            isPoam=(self.type is ScannerIntegrationType.CHECKLIST),
            dateCompleted=finding.date_last_updated if issue_status == regscale_models.IssueStatus.Closed else None,
        ).create()

    def update_issues_from_finding(
        self, issue: regscale_models.Issue, finding: IntegrationFinding
    ) -> regscale_models.Issue:
        """
        Updates RegScale issues based on the integration findings

        :param regscale_models.Issue issue: The issue to update
        :param IntegrationFinding finding: The integration findings
        :return: The updated issue
        :rtype: regscale_models.Issue
        """
        issue_status = (
            regscale_models.IssueStatus.Closed
            if finding.status == regscale_models.ControlTestResultStatus.PASS
            else regscale_models.IssueStatus.Open
        )
        # if issue.status != issue_status:
        issue.status = issue_status
        issue.severityLevel = finding.severity
        issue.description = finding.description
        issue.recommendedActions = finding.recommendation_for_mitigation
        issue.assetIdentifier = finding.asset_identifier
        issue.securityChecks = finding.external_id
        issue.remediationDescription = finding.recommendation_for_mitigation
        issue.identification = "Vulnerability Assessment"
        issue.isPoam = self.type is ScannerIntegrationType.CHECKLIST
        issue.controlId = self.get_control_implementation_id_for_cci(finding.cci_ref)
        if issue.has_changed():
            issue.dateLastUpdated = finding.date_last_updated
            return issue.save()
        return issue

    def handle_passing_finding(
        self,
        existing_issues: List[regscale_models.Issue],
        finding: IntegrationFinding,
        parent_id: int,
        parent_module: str,
    ) -> None:
        """
        Handles findings that have passed by closing any open issues associated with the finding.

        :param List[regscale_models.Issue] existing_issues: The list of existing issues to check against
        :param IntegrationFinding finding: The finding data that has passed
        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :rtype: None
        """
        logger.debug(f"Handling passing finding {finding.external_id} for {parent_id}")

        open_issue_ids = [x["id"] for x in self.existing_issue_ids_by_implementation_map[parent_id]]

        for issue in existing_issues:
            if issue.id in open_issue_ids:
                open_issue_ids.remove(issue.id)

            if issue.otherIdentifier == finding.external_id and issue.status != regscale_models.IssueStatus.Closed:
                self.close_issue(
                    issue, parent_module, parent_id, open_issue_ids, date_completed=finding.date_last_updated
                )

    def close_issue(
        self,
        issue: regscale_models.Issue,
        parent_module: str,
        parent_id: int,
        open_issue_ids: List[int],
        date_completed: Optional[str] = None,
    ):
        """
        Closes the given issue and updates control implementation status if needed.

        :param regscale_models.Issue issue: The issue to be closed
        :param str parent_module: The module of the parent
        :param int parent_id: The ID of the parent
        :param List[int] open_issue_ids: List of open issue IDs
        :param Optional[str] date_completed: The date the issue was completed
        """
        if parent_module == regscale_models.ControlImplementation.get_module_string():
            logger.info(f"Closing issue {issue.id} for control {self.control_map[parent_id]}")
        else:
            logger.info(f"Closing issue {issue.id} for asset {parent_id}")

        issue.status = regscale_models.IssueStatus.Closed
        issue.dateCompleted = date_completed or get_current_datetime()
        issue.save()

        if not issue.controlId:
            logger.warning(f"Control ID not found for issue {issue.id}")
        else:
            self.update_control_implementation_status(
                issue, parent_id, open_issue_ids, regscale_models.ImplementationStatus.FULLY_IMPLEMENTED
            )

    def update_control_implementation_status(
        self,
        issue: regscale_models.Issue,
        parent_id: int,
        open_issue_ids: List[int],
        status: regscale_models.ImplementationStatus,
    ) -> None:
        """
        Updates the control implementation status based on the open issues.

        :param regscale_models.Issue issue: The issue being closed
        :param int parent_id: The ID of the parent
        :param List[int] open_issue_ids: List of open issue IDs
        :param regscale_models.ImplementationStatus status: The status to set (default: FULLY_IMPLEMENTED)
        :rtype: None
        """
        # If there are still open issues, do not allow the status to be set to FULLY_IMPLEMENTED
        if any(open_issue_ids) and status == regscale_models.ImplementationStatus.FULLY_IMPLEMENTED:
            logger.debug(f"Asset {parent_id} still has open issues")
            return
        logger.debug(f"Asset {parent_id} has no open issues")
        if not issue.controlId:
            logger.warning(f"Control ID not found for issue {issue.id}")
            return
        control_implementation = self.control_implementation_map.get(
            issue.controlId
        ) or regscale_models.ControlImplementation.get_object(object_id=issue.controlId)
        if not control_implementation:
            logger.warning(f"Control implementation {issue.controlId} not found")
            return
        control_implementation.status = status
        self.control_implementation_map[issue.controlId] = control_implementation.save()

    def handle_failing_finding(
        self,
        issue_title: str,
        existing_issues: List[regscale_models.Issue],
        finding: IntegrationFinding,
        parent_id: int,
        parent_module: str,
    ) -> None:
        """
        Handles findings that have failed by updating an existing open issue or creating a new one and updating the control implementation status.

        :param str issue_title: The title of the issue
        :param List[regscale_models.Issue] existing_issues: The list of existing issues to check against
        :param IntegrationFinding finding: The finding data that has failed
        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :rtype: None
        """
        # logger.info(f"Handling failing finding {finding.external_id} for {parent_id}")

        # Determine the parent type based on the parent module
        parent_type = (
            "control" if parent_module == regscale_models.ControlImplementation.get_module_string() else "asset"
        )
        # Attempt to find an existing open issue that matches the finding's external ID.
        if found_issue := next(
            (
                issue
                for issue in existing_issues
                if issue.otherIdentifier == finding.external_id and issue.status != regscale_models.IssueStatus.Closed
            ),
            None,
        ):
            # If an existing open issue is found, update it with the new finding data.
            logger.debug(f"Updating issue {found_issue.id} for {parent_type} {parent_id}")
            self.update_issues_from_finding(issue=found_issue, finding=finding)
        else:
            # If no existing open issue is found, create a new one.
            logger.info(f"Creating issue for {parent_type} {parent_id}")
            found_issue = self.create_issue_from_finding(
                title=issue_title,
                parent_id=parent_id,
                parent_module=parent_module,
                finding=finding,
            )
        # Update the control implementation status based on open issues
        self.update_control_implementation_status(
            found_issue,
            parent_id,
            [issue.id for issue in existing_issues],
            regscale_models.ImplementationStatus.NOT_IMPLEMENTED,
        )

    def handle_failing_checklist(
        self,
        finding: IntegrationFinding,
        plan_id: int,
        asset: regscale_models.Asset,
    ) -> None:
        if finding.cci_ref:
            failing_objectives = regscale_models.ControlObjective.fetch_control_objectives_by_other_id(
                parent_id=plan_id, other_id_contains=finding.cci_ref
            )
            failing_objectives += regscale_models.ControlObjective.fetch_control_objectives_by_name(
                parent_id=plan_id, name_contains=finding.cci_ref
            )
            for failing_objective in failing_objectives:
                if failing_objective.name.lower().startswith("cci-"):
                    implementation_id = self.get_control_implementation_id_for_cci(failing_objective.name)
                else:
                    control_label = objective_to_control_dot(failing_objective.name)
                    if control_label not in self.control_implementation_id_map:
                        logger.warning(f"Control {control_label} not found for {control_label}")
                        continue
                    implementation_id = self.control_implementation_id_map[control_label]

                with self.concurrency_lock:
                    failing_option = regscale_models.ImplementationOption(
                        name="Failed STIG",
                        description="Failed STIG Security Checks",
                        acceptability=regscale_models.ImplementationStatus.NOT_IMPLEMENTED,
                        objectiveId=failing_objective.id,
                        securityControlId=failing_objective.securityControlId,
                        responsibility="Customer",
                    ).create_or_update(cache_dict=self.implementation_option_map)
                    regscale_models.ImplementationObjective(
                        securityControlId=failing_objective.securityControlId,
                        implementationId=implementation_id,
                        objectiveId=failing_objective.id,
                        optionId=failing_option.id,
                        status=regscale_models.ImplementationStatus.NOT_IMPLEMENTED,
                        statement=failing_objective.description,
                        responsibility="Customer",
                    ).create_or_update(cache_dict=self.implementation_objective_map)

    def process_checklist(self, finding: IntegrationFinding) -> None:
        """
        Processes a single checklist item based on the provided finding.

        This method checks if the asset related to the finding exists, updates or creates a checklist item,
        and handles the finding based on its status (pass/fail).

        :param IntegrationFinding finding: The finding to process
        :rtype: None
        """
        logger.info(f"Processing checklist {finding.external_id}")
        asset = self.asset_map_by_identifier.get(finding.asset_identifier)
        if not asset:
            self.log_error(f"Asset not found for identifier {finding.asset_identifier}, skipping finding")
            return

        asset_module_string = regscale_models.Asset.get_module_string()

        # Clear the cache if it grows too large to prevent memory issues
        if len(self.checklist_asset_map) > 300:
            self.checklist_asset_map.clear()

        # Check if the asset's checklists are already in the cache
        if not (checklists := self.checklist_asset_map.get(asset.id)):
            # If not, fetch and cache the checklists
            self.checklist_asset_map[asset.id] = regscale_models.Checklist.get_all_by_parent(
                parent_id=asset.id, parent_module=asset_module_string
            )
            # Now, checklists will always fetch from the cache, avoiding unnecessary database calls
            checklists = self.checklist_asset_map[asset.id]

        if not finding.cci_ref:
            finding.cci_ref = "CCI-000366"

        found_checklist = next(
            (
                checklist
                for checklist in checklists
                if checklist.vulnerabilityId == finding.external_id
                and checklist.tool == regscale_models.ChecklistTool.STIGs
                and checklist.cci == finding.cci_ref
            ),
            None,
        )

        if not found_checklist:
            logger.debug(f"Creating checklist for {finding.external_id}")
            regscale_models.Checklist(
                status=finding.status,
                assetId=asset.id,
                tool=regscale_models.ChecklistTool.STIGs,
                baseline=finding.baseline,
                vulnerabilityId=finding.external_id,
                results="??",  # TODO: Determine what to put here
                check=finding.title,
                cci=finding.cci_ref,
                ruleId=finding.rule_id,
                version=finding.rule_version,
                comments=finding.comments,
                datePerformed=finding.date_created,
            ).create()
        else:
            logger.debug(f"Updating checklist for {finding.external_id}")
            found_checklist.status = finding.status
            found_checklist.results = finding.results
            found_checklist.comments = finding.comments
            found_checklist.save()

        # with self.existing_issues_map_lock:
        if asset.id not in self.existing_issues_map:
            # If not, fetch and cache the issues
            with self.concurrency_lock:
                logger.debug(f"Fetching issues for asset {asset.id}")
                self.existing_issues_map[asset.id] = regscale_models.Issue.get_all_by_parent(
                    parent_id=asset.id, parent_module=asset_module_string
                )

        # Now, existing_issues will always fetch from the cache, avoiding unnecessary database calls
        existing_issues = self.existing_issues_map[asset.id]

        # Optionally clear the cache if it grows too large
        # if len(self.existing_issues_map) > 300:
        #     logger.info("Clearing existing issues cache")
        #     self.existing_issues_map.clear()

        if finding.status == regscale_models.ChecklistStatus.PASS:
            self.handle_passing_finding(existing_issues, finding, asset.id, asset_module_string)
        else:
            logger.debug(f"Handling failing checklist for {finding.external_id}")
            self.handle_failing_checklist(finding=finding, plan_id=self.plan_id, asset=asset)
            self.handle_failing_finding(
                issue_title=finding.issue_title or finding.title,
                existing_issues=existing_issues,
                finding=finding,
                parent_id=asset.id,
                parent_module=asset_module_string,
            )

    def update_regscale_checklists(self, findings: List[IntegrationFinding]) -> None:
        """
        Process checklists from IntegrationFindings in a threaded manner.

        :param List[IntegrationFinding] findings: The findings to process
        :rtype: None
        """
        logger.info("Updating RegScale checklists...")
        loading_findings = self.finding_progress.add_task(
            f"[#f8b737]Creating and updating checklists from {self.title}.",
        )
        progress_lock = threading.Lock()

        # Set concurrency to 3 to avoid overloading the API
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_MAX_WORKERS) as executor:
            future_to_finding = {executor.submit(self.process_checklist, finding): finding for finding in findings}
            for future in concurrent.futures.as_completed(future_to_finding):
                finding = future_to_finding[future]
                try:
                    # Accessing the result of the future will raise any exceptions that occurred
                    future.result()
                    with progress_lock:
                        # Wait until self.num_findings_to_process is set to set task total.
                        if self.num_findings_to_process and self.finding_progress.tasks[
                            loading_findings
                        ].total != float(self.num_findings_to_process):
                            self.finding_progress.update(
                                loading_findings,
                                total=self.num_findings_to_process,
                                description=f"[#f8b737]Creating and updating "
                                f"{self.num_findings_to_process} checklists from {self.title}.",
                            )
                        self.finding_progress.advance(loading_findings, 1)
                except Exception as exc:
                    self.log_error(
                        f"An error occurred when processing asset {finding.asset_identifier} "
                        f"for finding {finding.external_id}: {exc}",
                        exc_info=True,
                    )

    def update_regscale_findings(self, findings: List[IntegrationFinding]) -> None:
        """
        Updates RegScale findings based on the integration findings

        :param List[IntegrationFinding] findings: The integration findings
        :rtype: None
        """
        for finding in findings:
            if finding:
                for control_label in finding.control_labels:
                    if not (control_implementation_id := self.control_implementation_id_map.get(control_label)):
                        logger.error(f"Control Implementation for {control_label} not found in RegScale")
                        continue
                    assessment = self.get_or_create_assessment(control_implementation_id)
                    control_test = regscale_models.ControlTest(
                        uuid=finding.external_id,
                        parentControlId=control_implementation_id,
                        testCriteria=finding.cci_ref or finding.description,
                    ).get_or_create()
                    regscale_models.ControlTestResult(
                        parentTestId=control_test.id,
                        parentAssessmentId=assessment.id,
                        uuid=finding.external_id,
                        result=finding.status,  # type: ignore
                        dateAssessed=finding.date_created,
                        assessedById=self.assessor_id,
                        gaps=finding.gaps,
                        observations=finding.observations,
                        evidence=finding.evidence,
                        identifiedRisk=finding.identified_risk,
                        impact=finding.impact,
                        recommendationForMitigation=finding.recommendation_for_mitigation,
                    ).create()
                    logger.debug(
                        f"Created or Updated assessment {assessment.id} for control "
                        f"{self.control_map[control_implementation_id]}"
                    )
                    existing_issues: list[regscale_models.Issue] = regscale_models.Issue.get_all_by_parent(
                        parent_id=control_implementation_id,
                        parent_module=regscale_models.ControlImplementation.get_module_string(),
                    )
                    if finding.status == regscale_models.ControlTestResultStatus.PASS:
                        return self.handle_passing_finding(
                            existing_issues=existing_issues,
                            finding=finding,
                            parent_id=control_implementation_id,
                            parent_module=regscale_models.ControlImplementation.get_module_string(),
                        )

                    return self.handle_failing_finding(
                        issue_title=f"Finding {finding.external_id} failed",
                        existing_issues=existing_issues,
                        finding=finding,
                        parent_id=control_implementation_id,
                        parent_module=regscale_models.ControlImplementation.get_module_string(),
                    )

    @classmethod
    def cci_assessment(cls, plan_id: int) -> None:
        """
        Creates or updates CCI assessments in RegScale

        :param int plan_id: The ID of the security plan
        :rtype: None
        """
        instance = cls(plan_id)
        for control_id, ccis in instance.get_control_to_cci_map().items():
            if not (implementation_id := instance.control_id_to_implementation_map.get(control_id)):
                logger.error(f"Control Implementation for {control_id} not found in RegScale")
                continue
            assessment = instance.get_or_create_assessment(implementation_id)
            assessment_result = regscale_models.AssessmentResultsStatus.PASS
            open_issues = instance.existing_issue_ids_by_implementation_map.get(implementation_id, [])
            ccis.add("CCI-000366")
            for cci in sorted(ccis):
                logger.debug(f"Creating assessment for CCI {cci} for implementation {implementation_id}")
                result = regscale_models.ControlTestResultStatus.PASS
                for issue in open_issues:
                    if cci.lower() in issue["otherIdentifier"].lower():
                        result = regscale_models.ControlTestResultStatus.FAIL
                        assessment_result = regscale_models.AssessmentResultsStatus.FAIL
                        break

                control_test_key = f"{implementation_id}-{cci}"
                control_test = instance.control_tests_map.get(
                    control_test_key,
                    regscale_models.ControlTest(
                        parentControlId=implementation_id,
                        testCriteria=cci,
                    ).get_or_create(),
                )
                regscale_models.ControlTestResult(
                    parentTestId=control_test.id,
                    parentAssessmentId=assessment.id,
                    result=result,
                    dateAssessed=get_current_datetime(),
                    assessedById=instance.assessor_id,
                ).create()
            assessment.assessmentResult = assessment_result
            assessment.save()

    @classmethod
    def sync_findings(cls, plan_id: int, **kwargs: dict) -> None:
        """
        Syncs findings from the integration to RegScale

        :param int plan_id: The ID of the security plan
        :param dict **kwargs: Additional keyword arguments
        :rtype: None
        """
        logger.info(f"Syncing {cls.title} findings...")
        instance = cls(plan_id)
        instance.finding_progress = create_progress_object()
        with instance.finding_progress:
            if cls.type == ScannerIntegrationType.CHECKLIST:
                instance.update_regscale_checklists(findings=instance.fetch_findings(**kwargs))
            else:
                instance.update_regscale_findings(findings=instance.fetch_findings(**kwargs))
            if instance.errors:
                logger.error("Summary of errors encountered:")
                for error in instance.errors:
                    logger.error(error)
            else:
                logger.info("All findings have been processed successfully.")

        APIHandler().log_api_summary()

    @classmethod
    def sync_assets(cls, plan_id: int, **kwargs: dict) -> None:
        """
        Syncs assets from the integration to RegScale

        :param int plan_id: The ID of the security plan
        :param dict **kwargs: Additional keyword arguments
        :rtype: None
        """
        logger.info(f"Syncing {cls.title} assets...")
        instance = cls(plan_id)
        instance.asset_progress = create_progress_object()
        with instance.asset_progress:
            instance.update_regscale_assets(assets=instance.fetch_assets(**kwargs))

        if instance.errors:
            logger.error("Summary of errors encountered:")
            for error in instance.errors:
                logger.error(error)
        else:
            logger.info("All assets have been processed successfully.")

    def log_error(self, error: str, exc_info: bool = True) -> None:
        """
        Logs an error along with the stack trace.

        :param str error: The error message
        :param bool exc_info: If True, includes the stack trace of the current exception in the log.
        :rtype: None
        """
        self.errors.append(error)
        logger.error(error, exc_info=exc_info)
