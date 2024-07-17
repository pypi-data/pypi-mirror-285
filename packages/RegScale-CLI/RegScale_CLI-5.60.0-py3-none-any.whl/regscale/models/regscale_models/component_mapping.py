""" This module contains the ComponentMapping model. """

import logging
from typing import Optional

from pydantic import Field, ConfigDict

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger(__name__)


class ComponentMapping(RegScaleModel):
    _module_slug = "componentmapping"
    _parent_id_field = "componentId"
    _unique_fields = ["componentId", "securityPlanId"]

    id: int = 0
    uuid: Optional[str] = None
    securityPlanId: int
    componentId: int
    createdById: str = Field(default_factory=RegScaleModel._api_handler.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: str = Field(default_factory=RegScaleModel._api_handler.get_user_id)
    dateLastUpdated: str = Field(default_factory=get_current_datetime)
    tenantsId: int = 1
    isPublic: bool = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ComponentMapping model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(get_all_by_parent="/api/{model_slug}/getMappingsAsSecurityPlans/{intParentID}")
