#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Class for a Wiz.io integration """

# standard python imports
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime


class AssetCategory(Enum):
    """Map Wiz assetTypes with RegScale assetCategories"""

    SERVICE_USAGE_TECHNOLOGY = "software"
    GATEWAY = "software"
    SECRET = "software"
    BUCKET = "software"
    WEB_SERVICE = "software"
    DB_SERVER = "hardware"
    LOAD_BALANCER = "software"
    CLOUD_ORGANIZATION = "software"
    SUBNET = "software"
    VIRTUAL_MACHINE = "hardware"
    TECHNOLOGY = "software"
    SECRET_CONTAINER = "software"
    FILE_SYSTEM_SERVICE = "software"
    KUBERNETES_CLUSTER = "software"
    ROUTE_TABLE = "software"
    COMPUTE_INSTANCE_GROUP = "software"
    HOSTED_TECHNOLOGY = "software"
    USER_ACCOUNT = "software"
    DNS_ZONE = "software"
    VOLUME = "software"
    SERVICE_ACCOUNT = "software"
    RESOURCE_GROUP = "software"
    ACCESS_ROLE = "software"
    SUBSCRIPTION = "software"
    SERVICE_CONFIGURATION = "software"
    VIRTUAL_NETWORK = "software"
    VIRTUAL_MACHINE_IMAGE = "software"
    FIREWALL = "hardware"
    DATABASE = "software"
    GOVERNANCE_POLICY_GROUP = "software"
    STORAGE_ACCOUNT = "software"
    CONFIG_MAP = "software"
    NETWORK_ADDRESS = "software"
    NETWORK_INTERFACE = "software"
    DAEMON_SET = "software"
    PRIVATE_ENDPOINT = "software"
    ENDPOINT = "software"
    DEPLOYMENT = "software"
    POD = "software"
    KUBERNETES_STORAGE_CLASS = "software"
    ACCESS_ROLE_BINDING = "software"
    KUBERNETES_INGRESS = "software"
    CONTAINER = "software"
    CONTAINER_IMAGE = "software"
    CONTAINER_REGISTRY = "software"
    GOVERNANCE_POLICY = "software"
    REPLICA_SET = "software"
    KUBERNETES_SERVICE = "software"
    KUBERNETES_PERSISTENT_VOLUME_CLAIM = "software"
    KUBERNETES_PERSISTENT_VOLUME = "software"
    KUBERNETES_NETWORK_POLICY = "software"
    KUBERNETES_NODE = "software"


class ComplianceCheckStatus(Enum):
    PASS = "Pass"
    FAIL = "Fail"


class ComplianceReport(BaseModel):
    resource_name: str = Field(..., alias="Resource Name")
    cloud_provider_id: str = Field(..., alias="Cloud Provider ID")
    object_type: str = Field(..., alias="Object Type")
    native_type: str = Field(..., alias="Native Type")
    tags: Optional[str] = Field(None, alias="Tags")
    subscription: str = Field(..., alias="Subscription")
    projects: Optional[str] = Field(None, alias="Projects")
    cloud_provider: str = Field(..., alias="Cloud Provider")
    policy_id: str = Field(..., alias="Policy ID")
    policy_short_name: str = Field(..., alias="Policy Short Name")
    policy_description: Optional[str] = Field(None, alias="Policy Description")
    policy_category: Optional[str] = Field(None, alias="Policy Category")
    control_id: Optional[str] = Field(None, alias="Control ID")
    compliance_check: Optional[str] = Field(None, alias="Compliance Check Name (Wiz Subcategory)")
    control_description: Optional[str] = Field(None, alias="Control Description")
    severity: Optional[str] = Field(None, alias="Severity")
    result: str = Field(..., alias="Result")
    framework: Optional[str] = Field(None, alias="Framework")
    remediation_steps: Optional[str] = Field(None, alias="Remediation Steps")
    assessed_at: Optional[datetime] = Field(None, alias="Assessed At")
    created_at: Optional[datetime] = Field(None, alias="Created At")
    updated_at: Optional[datetime] = Field(None, alias="Updated At")
    subscription_name: Optional[str] = Field(None, alias="Subscription Name")
    subscription_provider_id: Optional[str] = Field(None, alias="Subscription Provider ID")
    resource_id: str = Field(..., alias="Resource ID")
    resource_region: Optional[str] = Field(None, alias="Resource Region")
    resource_cloud_platform: Optional[str] = Field(None, alias="Resource Cloud Platform")


# # Attempt to create an instance of the model again
# example_row = data.iloc[0].to_dict()
# example_compliance_report = ComplianceReport(**example_row)
#
# # Display the instance
# example_compliance_report.dict()
