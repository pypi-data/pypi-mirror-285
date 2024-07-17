"""
Wiz Integration class
"""

import datetime
import json
import logging
from os import environ
from typing import List, Optional

from regscale.core.app.utils.app_utils import check_license
from regscale.integrations import Integration
from regscale.integrations.commercial.wiz.inventory import WizInventory
from regscale.integrations.commercial.wiz.issue import WizIssue
from regscale.integrations.commercial.wiz.wiz_auth import wiz_authenticate
from regscale.integrations.commercial.wiz.vulnerabilities import VulnerabilitiesIntegration

logger = logging.getLogger(__name__)


class WizIntegration(Integration):
    """
    Wiz Integration class
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_inventory_pull = (
            self.config.get("wizLastInventoryPull")
            if self.config.get("wizLastInventoryPull") != "<wizLastInventoryPull>"
            else None
        )
        self.filter_by_override = (
            self.config.get("wizIssueFilterBy") if self.config.get("wizIssueFilterBy") != "<wizIssueFilterBy>" else None
        )
        self.wiz_url = self.config.get("wizUrl")
        self.is_authenticated = False

    def authenticate(
        self,
        client_id: str = environ.get("WizClientId"),
        client_secret: str = environ.get("WizClientId"),
    ) -> bool:
        """
        Authenticate to Wiz using the client id and client secret

        :param str client_id: Wiz client id, defaults to WizClientId environment variable
        :param str client_secret: Wiz client secret, defaults to WizClientSecret environment variable
        :return: True if authenticated, False otherwise
        :rtype: bool
        """
        if not self.is_authenticated:
            self.is_authenticated = wiz_authenticate(client_id, client_secret)
        return self.is_authenticated

    def inventory(
        self,
        wiz_project_ids: List[str],
        regscale_id: int,
        regscale_module: str,
        filter_by_override: str,
        client_id: str,
        client_secret: str,
        full_inventory: bool,
    ) -> None:
        """
        Pull inventory from Wiz for the given project ids

        :param List[str] wiz_project_ids: Wiz project ids to pull inventory for
        :param int regscale_id: RegScale system security plan id
        :param str regscale_module: RegScale module to create assets in
        :param str filter_by_override: Filter by override to use for pulling inventory
        :param str client_id: Wiz client id
        :param str client_secret: Wiz client secret
        :param bool full_inventory: Pull full inventory from Wiz
        :rtype: None
        """
        check_license()
        self.authenticate(client_id, client_secret)
        wiz_projects = wiz_project_ids
        if filter_by_override:
            filter_by = json.loads(filter_by_override)
        else:
            filter_by = {
                "projectId": wiz_projects,
            }
            if self.last_inventory_pull and not full_inventory:
                filter_by["updatedAt"] = {"after": self.last_inventory_pull}

        inventory = WizInventory(
            filter_by=filter_by,
            regscale_id=regscale_id,
            regscale_module=regscale_module,
            wiz_projects=wiz_projects,
            wiz_url=self.wiz_url,
            full_inventory=full_inventory,
        )
        inventory.pull()
        self.last_inventory_pull = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.config["wizLastInventoryPull"] = self.last_inventory_pull
        self.save_config(self.config)

    def issues(
        self,
        wiz_project_id: str,
        regscale_id: int,
        regscale_module: str,
        client_id: str,
        client_secret: str,
        filter_by_override: Optional[str] = None,
    ) -> None:
        """
        Pull issues from Wiz for the given project id and create issues in RegScale

        :param str wiz_project_id: Wiz project id to pull issues for
        :param int regscale_id: RegScale record id
        :param str regscale_module: RegScale module to create issues in
        :param str client_id: Wiz client id
        :param str client_secret: Wiz client secret
        :param Optional[str] filter_by_override: Filter by override to use for pulling issues, defaults to None
        :rtype: None
        """
        check_license()
        self.authenticate(client_id, client_secret)

        if self.filter_by_override:
            filter_by = json.loads(filter_by_override)
        else:
            filter_by = {
                "project": wiz_project_id,
            }

        wiz_issue_integration = WizIssue(
            filter_by=filter_by,
            regscale_id=regscale_id,
            regscale_module=regscale_module,
            wiz_projects=wiz_project_id,
            wiz_url=self.wiz_url,
        )
        wiz_issue_integration.pull()

    def sbom(
        self,
        wiz_project_id: str,
        regscale_id: int,
        regscale_module: str,
        filter_by_override: str,
        client_id: str,
        client_secret: str,
    ):
        """
        Pull SBOM from Wiz for the given project id and create SBOM in RegScale

        :param str wiz_project_id: Wiz project id to pull SBOM for
        :param int regscale_id: RegScale record id
        :param str regscale_module: RegScale module to create SBOM in
        :param str filter_by_override: Filter by override to use for pulling SBOM
        :param str client_id: Wiz client id
        :param str client_secret: Wiz client secret
        """
        # SBOM coming coon
        pass

    def fetch_vulnerabilities(
        self,
        wiz_project_id: str,
        regscale_id: int,
        regscale_module: str,
        client_id: str,
        client_secret: str,
        filter_by_override: str = None,
    ) -> None:
        """
        Fetch vulnerabilities from Wiz
        :param str wiz_project_id: Wiz Project ID
        :param int regscale_id: RegScale ID
        :param str regscale_module: RegScale Module
        :param str client_id: Wiz Client ID
        :param str client_secret: Wiz Client Secret
        :param str filter_by_override: Filter By Override
        """
        check_license()
        self.authenticate(client_id, client_secret)
        logger.info("Pulling Vulnerabilities")
        vulnerability_client = VulnerabilitiesIntegration(
            wiz_project_id=wiz_project_id,
            filter_by_override=filter_by_override,
            parent_id=regscale_id,
            parent_module=regscale_module,
            scan_tool="Wiz",
        )
        vulnerability_client.run()
