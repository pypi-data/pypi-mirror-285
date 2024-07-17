""" Wiz Issue Integration class """

import json
import logging
import os
from datetime import timedelta, datetime
from typing import List, Dict, Optional, Tuple

from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import create_progress_object, check_file_path
from regscale.core.utils.date import date_str, days_from_today, datetime_obj
from regscale.integrations.integration.issue import IntegrationIssue
from regscale.models import (
    Issue,
    IssueSeverity,
    Link,
    IssueStatus,
    Data,
    DataDataType,
    Comment,
    regscale_models,
)
from regscale.utils.dict_utils import get_value
from regscale.utils.graphql_client import PaginatedGraphQLClient
from .constants import (
    CONTENT_TYPE,
    ISSUE_QUERY,
    DATASOURCE,
    ISSUES_FILE_PATH,
    SEVERITY_MAP,
)

logger = logging.getLogger(__name__)

CLOUD_PROVIDER_URL_FIELD = "entitySnapshot.cloudProviderURL"
WIZ_ASSET_NAME = "entitySnapshot.name"
SOURCE_ID = "sourceRule.id"
WIZ_ASSET_ID = "entitySnapshot.id"


class WizIssue(IntegrationIssue):
    """
    Wiz Issue class
    """

    def __init__(
        self,
        filter_by,
        regscale_id: int,
        regscale_module: str,
        wiz_url: str,
        first: int = 100,
        wiz_projects=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if wiz_projects is None:
            wiz_projects = []
        self.variables = {
            "first": first,
            "filterBy": filter_by,
        }
        self.regscale_id = regscale_id
        self.regscale_module = regscale_module
        self.wiz_projects = wiz_projects
        self.wiz_url = wiz_url
        app = Application()
        self.config = app.config
        self.asset_dict = {}
        self.issues_to_create = []
        self.issues_to_update = []
        self.data_to_create = []
        self.links_to_create = []
        self.comments_to_create = []
        self.data_to_update = []
        self.links_to_update = []
        self.comments_to_update = []
        self.additional_data = {}
        self.additional_data_updated = {}
        self.assets: List[regscale_models.Asset] = []
        self.control_impl_controlid_dict = {}
        self.pull_limit_hours = self.config.get("wizFullPullLimitHours", 8)
        self.low_days = self.config.get("issues.wiz.high", 60)
        self.medium_days = self.config.get("issues.wiz.medium", 210)
        self.high_days = self.config.get("issues.wiz.low", 394)
        self.due_date_map = {
            regscale_models.IssueSeverity.High: date_str(days_from_today(self.low_days)),
            regscale_models.IssueSeverity.Moderate: date_str(days_from_today(self.medium_days)),
            regscale_models.IssueSeverity.Low: date_str(days_from_today(self.high_days)),
        }

    def pull(self):
        """
        Pull issues from Wiz for the given project ids
        """
        wiz_issues = self.fetch_wiz_data_if_needed()
        logger.info(f"Found {len(wiz_issues)} issues from Wiz")
        self.assets = regscale_models.Asset.get_all_by_parent(
            parent_id=self.regscale_id, parent_module=self.regscale_module
        )
        self.asset_dict = {asset.wizId: asset for asset in self.assets}
        self.control_impl_controlid_dict = regscale_models.ControlImplementation.get_control_label_map_by_plan(
            plan_id=self.regscale_id
        )
        self.create_issues(
            wiz_issues=wiz_issues,
        )
        all_issues = []
        try:
            if self.issues_to_create:
                created_issues = Issue.batch_create(items=self.issues_to_create)
                all_issues.extend(created_issues)
                logger.info(f"Created {len(created_issues)} new issues.")
                if created_issues:
                    self._process_additional_data_create(issues=created_issues)
            if self.issues_to_update:
                updated_issues = Issue.batch_update(items=self.issues_to_update)
                all_issues.extend(updated_issues)
                if updated_issues:
                    self._process_additional_data_update(issues=updated_issues)
                logger.info(f"Updated {len(updated_issues)} issues.")

        except Exception as e:
            logger.error(f"Error during issue batch operation: {e}")

        logger.info(f"Total issues processed: {len(all_issues)}")

    def _process_additional_data_update(self, issues: List[Issue]) -> None:
        """
        Process additional data for updates

        :param List[Issue] issues: Issues
        :return None: None
        :rtype None: None
        """
        data_list: List[Data] = []
        links: List[Link] = []
        comments: List[Comment] = []

        logger.info(f"Processing additional data for {len(issues)} issues")
        fetching_data_progress = create_progress_object()
        fetching_data_task = fetching_data_progress.add_task("[#f68d1f]Fetching additional data...", total=len(issues))
        update_data_progress = create_progress_object()
        update_link_progress = create_progress_object()
        update_comment_progress = create_progress_object()
        with fetching_data_progress:
            for issue in issues:
                if issue.wizId:
                    self._handle_updating_additional_data(
                        issue=issue,
                        data_list=data_list,
                        links=links,
                        comments=comments,
                    )
                fetching_data_progress.advance(fetching_data_task, advance=1)

        if data_list:
            update_data_task = update_data_progress.add_task(
                "[#f68d1f]Updating additional data...", total=len(data_list)
            )
            Data.batch_update(items=data_list)
            update_data_progress.advance(update_data_task, advance=len(data_list))
        if links:
            update_link_task = update_link_progress.add_task("[#f68d1f]Updating additional links...", total=len(links))
            Link.batch_update(items=links)
            update_link_progress.advance(update_link_task, advance=len(links))
        if comments:
            update_comment_task = update_comment_progress.add_task(
                "[#f68d1f]Updating additional comments...", total=len(comments)
            )
            Comment.batch_update(items=comments)
            update_comment_progress.advance(update_comment_task, advance=len(comments))

    @staticmethod
    def _create_data(data_list: List[Data], issue_id: int) -> None:
        """
        Create data for the given issue

        :param List[Data] data_list: List of data
        :param int issue_id: Issue ID
        """
        existing_data = Data.get_all_by_parent(parent_id=issue_id, parent_module="issues")
        existing_data_dict = {d.rawData: d for d in existing_data if d.dataSource == DATASOURCE}
        for data in data_list:
            if not existing_data_dict.get(data.rawData):
                data.create()

    @staticmethod
    def _create_links(links: List[Link], issue_id: int) -> None:
        """
        Create links for the given issue
        :param List[Link] links: List of links
        :param int issue_id: Issue ID
        :rtype: None
        """
        existing_link = Link.get_all_by_parent(parent_id=issue_id, parent_module="issues")
        existing_link_dict = {link.url: link for link in existing_link}
        for link in links:
            if not existing_link_dict.get(link.url):
                link.create()

    @staticmethod
    def _create_comments(comments: List[Comment], issue_id: int) -> None:
        """
        Create comments for the given issue
        :param List[Comment] comments: List of comments
        :param int issue_id: Issue ID
        :rtype: None
        """
        existing_link = Comment.get_all_by_parent(parent_id=issue_id, parent_module="issues")
        existing_link_dict = {c.comment: c for c in existing_link}
        for comment in comments:
            if not existing_link_dict.get(comment.comment):
                comment.create()

    def _process_additional_data_create(self, issues: List[Issue]) -> None:
        """
        Process additional data
        :param List[Issue] issues: Issues
        :rtype: None
        """
        data_list = []
        links = []
        comments = []
        for issue in issues:
            if wiz_id := issue.wizId:
                self._handle_creating_additional_data(
                    data_dict=self.additional_data.get(wiz_id, {}),
                    issue=issue,
                    data_list=data_list,
                    links=links,
                    comments=comments,
                )

        if data_list:
            Data.batch_create(data_list)
        if links:
            Link.batch_create(items=links)
        if comments:
            Comment.batch_create(items=comments)

    def _handle_updating_additional_data(
        self,
        issue: Issue,
        data_list: List,
        links: List,
        comments: List,
    ) -> None:
        """
        Handle updating additional data
        :param Issue issue: Issue
        :param List data_list: Data list
        :param List links: Links
        :param List comments: Comments
        :rtype None: None
        """
        existing_comments, existing_data, existing_links = self.fetch_existing_addtional_data(issue)
        comments.extend(existing_comments)
        data_list.extend(existing_data)
        links.extend(existing_links)

    @staticmethod
    def fetch_existing_addtional_data(issue: Issue) -> Tuple[List[Comment], List[Data], List[Link]]:
        """
        Fetch existing additional data for the given issue
        :param Issue issue: Issue
        :return Tuple[List[Comment], List[Data], List[Link]]: Tuple of comments, data, and links
        :rtype Tuple[List[Comment], List[Data], List[Link]]: Tuple
        """
        existing_data = Data.get_all_by_parent(parent_id=issue.id, parent_module="issues")
        existing_links = Link.get_all_by_parent(parent_id=issue.id, parent_module="issues")
        existing_comments = Comment.get_all_by_parent(parent_id=issue.id, parent_module="issues")
        filtered_data: List[Data] = list(
            filter(
                lambda d: d.dataSource == DATASOURCE,
                existing_data,
            )
        )
        filtered_links = list(
            filter(
                lambda elink: "Cloud Provider URL" in elink.title,
                existing_links,
            )
        )
        return existing_comments, filtered_data, filtered_links

    @staticmethod
    def _handle_creating_additional_data(
        data_dict: Dict, issue: Issue, data_list: List, links: List, comments: List
    ) -> None:
        """
        Handle pulling additional data to list add appropriate id's from created issues
        :param Dict data_dict: Dict
        :param Issue issue: Issue
        :param List data_list: Data list
        :param List links: Links
        :param List comments: Comments
        :rtype: None
        """
        if data := data_dict.get("data"):
            data.parentId = issue.id
            data_list.append(data)
        if link := data_dict.get("link"):
            link.parentID = issue.id
            links.append(link)
        if comment_list := data_dict.get("comments"):
            for comment in comment_list:
                comment.parentID = issue.id
            comments.extend(comment_list)

    def fetch_wiz_data_if_needed(self) -> List[Dict]:
        """
        Fetch Wiz data if needed and save to file if not already fetched within the last 8 hours and return the data
        :return List[Dict]: The fetched data
        :rtype List[Dict]: List[Dict]
        """

        fetch_interval = timedelta(hours=self.pull_limit_hours)  # Interval to fetch new data
        current_time = datetime.now()

        # Check if the file exists and its last modified time
        if os.path.exists(ISSUES_FILE_PATH):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(ISSUES_FILE_PATH))
            if current_time - file_mod_time < fetch_interval:
                with open(ISSUES_FILE_PATH, "r") as file:
                    nodes = json.load(file)
                return nodes

        nodes = self.fetch_wiz_data(
            query=ISSUE_QUERY,
            variables=self.variables,
            api_endpoint_url=self.wiz_url,
            topic_key="issues",
        )
        check_file_path("artifacts")
        with open(ISSUES_FILE_PATH, "w") as file:
            json.dump(nodes, file)

        return nodes

    @staticmethod
    def fetch_wiz_data(query: str, variables: Dict, api_endpoint_url: str, topic_key: str) -> List[Dict]:
        """
        Fetch Wiz data for the given query and variables
        :param str query: The query to fetch data
        :param Dict variables: The variables for the query
        :param str api_endpoint_url: The Wiz API endpoint URL
        :param str topic_key: The key for the topic in the response data
        :raises ValueError: If the Wiz access token is missing
        :return: The fetched data
        :rtype: List[Dict]
        """
        logger.debug("Sending a paginated request to Wiz API")
        app = Application()
        api_endpoint_url = app.config["wizUrl"] if api_endpoint_url is None else api_endpoint_url

        if token := app.config.get("wizAccessToken"):
            client = PaginatedGraphQLClient(
                endpoint=api_endpoint_url,
                query=query,
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Authorization": "Bearer " + token,
                },
            )

            # Fetch all results using the client's pagination logic
            data = client.fetch_all(variables=variables, topic_key=topic_key)

            return data
        raise ValueError("Your Wiz access token is missing.")

    @staticmethod
    def group_issues(wiz_issues: List[Dict]) -> Dict:
        """
        Group Wiz issues by data sourceRule.id
        :param List[Dict] wiz_issues: List of Wiz issues
        :return Dict: Dict with key of data sourceRule.id containing a list of Wiz issues
        :rtype Dict: Dict
        """
        issues = {}
        for wiz_issue in wiz_issues:
            source_id = get_value(wiz_issue, SOURCE_ID)
            if not issues.get(source_id):
                issues[source_id] = [wiz_issue]
            else:
                issues[source_id].append(wiz_issue)
        return issues

    def create_issues(self, wiz_issues: List[Dict]) -> None:
        """
        Map Wiz issues to RegScale issues
        :param List[Dict] wiz_issues: List of Wiz issues
        :rtype: None
        """
        app = Application()
        config = app.config
        user_id = config.get("userId")
        create_progress = create_progress_object()
        total_items = len(wiz_issues)
        create_job = create_progress.add_task("[#f68d1f]Mapping RegScale issues...", total=total_items)
        with create_progress:
            existing_issues = Issue.get_all_by_parent(parent_id=self.regscale_id, parent_module=self.regscale_module)
            existing_issues_dict = {i.wizId: i for i in existing_issues}
            logger.info(f"Found {len(existing_issues)} existing issues")
            for wiz_issue in wiz_issues:
                asset: regscale_models.Asset = self.asset_dict.get(
                    get_value(wiz_issue, WIZ_ASSET_ID),
                )
                self.create_issue(
                    issue=wiz_issue,
                    user_id=user_id,
                    parent_id=asset.id if asset else self.regscale_id,
                    parent_module=asset.get_module_slug() if asset else self.regscale_module,
                    identifier=f"<p>{get_value(wiz_issue, WIZ_ASSET_NAME)}</p>",
                    existing_issues_dict=existing_issues_dict,
                )
                create_progress.advance(create_job, advance=1)

    @staticmethod
    def dedupe(list_with_dups: List) -> List:
        """
        Deduplicate a list
        :param List list_with_dups: List with duplicates
        :return List: Deduplicated list
        :rtype List: List
        """
        return list(set(list_with_dups))

    def create_issue(
        self,
        issue: Dict,
        user_id: str,
        parent_id: int,
        parent_module: str,
        identifier: str,
        existing_issues_dict: Dict,
    ):
        """
        Create a RegScale issue from a Wiz issue
        :param issue: Wiz issue dictionary
        :param user_id: User ID to assign the issue to
        :param parent_id the regscale model to which the issue is attached
        :param parent_module the regscale model to which the issue is attached
        :param identifier: Asset identifiers
        :param existing_issues_dict: Existing issues to update
        """
        due_date_str = self.process_issue_due_date(get_value(issue, "severity"))
        unknown_title = (
            f"unknown - {issue.get('id')} - type: {issue.get('type')} - entity_id: {issue.get(WIZ_ASSET_ID)}"
        )

        existing_issue = existing_issues_dict.get(get_value(issue, "id"))
        if existing_issue:
            self._update_issue(
                existing_issue=existing_issue,
                issue=issue,
                user_id=user_id,
                parent_id=parent_id,
                parent_module=parent_module,
                identifier=identifier,
                unknown_title=unknown_title,
                due_date_str=due_date_str,
            )
        else:
            self._create_issue(
                issue=issue,
                user_id=user_id,
                parent_id=parent_id,
                parent_module=parent_module,
                identifier=identifier,
                unknown_title=unknown_title,
                due_date_str=due_date_str,
            )

    @staticmethod
    def convert_first_seen_to_days(first_seen: str) -> int:
        """
        Converts the first seen date to days
        :param str first_seen: First seen date
        :returns: Days
        :rtype: int
        """
        first_seen_date = datetime_obj(first_seen)
        if not first_seen_date:
            return 0
        first_seen_date_naive = first_seen_date.replace(tzinfo=None)
        return (datetime.now() - first_seen_date_naive).days

    def determine_is_poam_from_days_since_last_seen_and_severity(
        self, days_since_last_seen: int, severity: str
    ) -> bool:
        """
        Determines if the issue is a POAM from the days since last seen
        :param int days_since_last_seen: Days since last seen
        :param str severity: Severity of the issue
        :returns: True if the issue is a POAM, False otherwise
        :rtype: bool
        """
        if severity.lower().__contains__("low"):
            return days_since_last_seen > self.low_days
        elif severity.lower().__contains__("moderate"):
            return days_since_last_seen > self.medium_days
        elif severity.lower().__contains__("high") or severity.lower().__contains__("critical"):
            return days_since_last_seen > self.high_days
        return False

    def set_is_poam_and_due_date_on_issue(self, issue: Issue):
        """
        Set the isPoam and dueDate on the issue
        :param Issue issue: Issue object
        """
        days_open = self.convert_first_seen_to_days(issue.dateFirstDetected)
        due_date: str = self.due_date_map.get(issue.severityLevel, date_str(days_from_today(days_open)))
        days_since_first_seen = self.convert_first_seen_to_days(issue.dateFirstDetected)
        is_poam = self.determine_is_poam_from_days_since_last_seen_and_severity(
            days_since_first_seen, issue.severityLevel
        )
        issue.isPoam = is_poam
        issue.dueDate = due_date

    def _update_issue(self, **kwargs) -> None:
        """
        Update a RegScale issue from a Wiz issue
        :param existing_issue Issue: RegScale issue object
        :param issue: Wiz issue dictionary
        :param user_id: User ID to assign the issue to
        :param parent_id the regscale model to which the issue is attached
        :param parent_module the regscale model to which the issue is attached
        :param identifier: Asset identifiers
        :param unknown_title: Unknown title
        :rtype: None
        """
        issue = kwargs.get("issue")
        asset: regscale_models.Asset = self.asset_dict.get(
            get_value(issue, WIZ_ASSET_ID),
        )
        existing_issue: Issue = kwargs.get("existing_issue")
        user_id = kwargs.get("user_id")
        identifier = kwargs.get("identifier")
        unknown_title = kwargs.get("unknown_title")

        due_date_str = self.process_issue_due_date(get_value(issue, "severity"))
        existing_issue.title = get_value(issue, "sourceRule.name") or unknown_title
        existing_issue.description = get_value(issue, "sourceRule.cloudConfigurationRuleDescription")
        existing_issue.dateLastUpdated = get_value(issue, "updatedAt")
        existing_issue.dateFirstDetected = get_value(issue, "createdAt")
        existing_issue.status = self.map_status(get_value(issue, "status"))
        existing_issue.severityLevel = self.map_severity_level(issue)
        existing_issue.recommendedActions = get_value(issue, "sourceRule.remediationInstructions")
        existing_issue.dueDate = due_date_str
        existing_issue.dateCompleted = get_value(issue, "resolvedAt")
        existing_issue.lastUpdatedById = user_id
        existing_issue.assetIdentifier = identifier
        existing_issue.identification = "Wiz"
        existing_issue.sourceReport = "Wiz"
        existing_issue.parentId = asset.id if asset else kwargs.get("parent_id")
        existing_issue.parentModule = asset.get_module_slug() if asset else kwargs.get("parent_module")
        existing_issue.wizId = get_value(issue, WIZ_ASSET_ID)
        existing_issue.securityChecks = get_value(issue, SOURCE_ID)
        existing_issue.pluginId = get_value(issue, SOURCE_ID)
        existing_issue.otherIdentifier = get_value(issue, "entitySnapshot.externalId")
        self.set_is_poam_and_due_date_on_issue(existing_issue)
        self.issues_to_update.append(existing_issue)
        existing_comments, existing_data, existing_links = self.fetch_existing_addtional_data(issue=existing_issue)
        self.data_to_update.extend(existing_data)
        self.links_to_update.extend(existing_links)
        self.comments_to_update.extend(existing_comments)

    def prepare_additional_data(self, issue: Dict, user_id: str) -> Dict:
        """
        Prepare additional data for a Wiz issue before creating or updating the RegScale issue.
        :param Dict issue: Wiz issue dictionary
        :param str user_id: User ID to assign the additional data to
        :return Dict: Additional data
        :rtype Dict: Dict
        """
        return {
            "data": self.create_data_from_wiz_issue(issue, user_id),
            "link": self.create_link_from_wiz_issue(issue, user_id),
            "comments": self.create_comments_from_wiz_issue(issue, user_id),
        }

    @staticmethod
    def create_comments_from_wiz_issue(issue: Dict, user_id: str) -> List[Comment]:
        """
        Create comments from a Wiz issue
        :param Dict issue: Wiz issue dictionary
        :param str user_id: User ID to assign the comments to
        :return List[Comment]: List of RegScale comment objects
        :rtype List[Comment]: List[Comment]
        """
        wiz_notes = get_value(issue, "notes")
        comments = [
            Comment(
                parentID=0,  # Temporarily set to 0; will be updated after issue creation.
                parentModule="issues",
                comment=f"{note.get('email')}: {note.get('text')}" if note.get("email") else note.get("text"),
                commentDate=note.get("createdAt"),
                createdById=user_id,
                lastUpdatedById=user_id,
            )
            for note in wiz_notes or []
        ]
        return comments

    @staticmethod
    def update_comments_from_wiz_issue(issue: Dict, user_id: str, existing_comments: List[Comment]) -> List[Comment]:
        """
        Update comments based on the Wiz issue.
        :param Dict issue: Wiz issue dictionary containing the issue data.
        :param str user_id: User ID to assign the comments to.
        :param List[Comment] existing_comments: List of existing Comment objects to be updated.
        :return: Updated or new RegScale comment objects.
        :rtype: List[Comment]
        """
        wiz_notes = get_value(issue, "notes")
        updated_comments = []

        # Map existing comments by some identifiable key, e.g., note ID if available
        comment_map = {comment.comment: comment for comment in existing_comments}

        for note in wiz_notes or []:
            note_key = f"{note.get('email')}: {note.get('text')}"  # Construct a unique key for each note
            if note_key in comment_map:
                # Update existing comment
                comment = comment_map[note_key]
                comment.commentDate = note.get("createdAt")
                comment.lastUpdatedById = user_id
                updated_comments.append(comment)

        # Assume we return both updated and new comments
        return updated_comments

    @staticmethod
    def create_data_from_wiz_issue(issue: Dict, user_id: str) -> Data:
        """
        Create a RegScale data object from a Wiz issue
        :param Dict issue: Wiz issue dictionary
        :param str user_id: User ID to assign the data to
        :return Data: RegScale data object
        :rtype Data: Data
        """
        data = Data(
            parentId=0,  # Temporarily set to 0; will be updated after issue creation.
            parentModule="issues",
            dataSource=DATASOURCE,
            dataType=DataDataType.JSON.value,
            rawData=json.dumps(issue),
            createdById=user_id,
            lastUpdatedById=user_id,
        )
        return data

    @staticmethod
    def create_link_from_wiz_issue(issue: Dict, user_id: str) -> Optional[Link]:
        """
        Create a RegScale link object from a Wiz issue
        :param Dict issue: Wiz issue dictionary
        :param str user_id: User ID to assign the link to
        :return: RegScale link object or None if no URL is available
        :rtype: Optional[Link]
        """
        if url := get_value(issue, CLOUD_PROVIDER_URL_FIELD):
            link = Link(
                parentID=0,  # Temporarily set to 0; will be updated after issue creation.
                parentModule="issues",
                url=url,
                title=f"Wiz Entity: {get_value(issue, WIZ_ASSET_NAME)}",
                createdById=user_id,
                lastUpdatedById=user_id,
            )
            return link
        return None

    @staticmethod
    def update_link_from_wiz_issue(issue: Dict, user_id: str, existing_links: List[Link]) -> Optional[Link]:
        """
        Update a RegScale link object based on the Wiz issue.

        :param Dict issue: Wiz issue dictionary containing the issue data.
        :param str user_id: User ID to assign the link to.
        :param List[Link] existing_links: List of existing Link objects to be updated.
        :return: Updated or new RegScale link object.
        :rtype: Optional[Link]
        """
        url = get_value(issue, CLOUD_PROVIDER_URL_FIELD)
        if not url or not isinstance(url, str):
            return None

        # Map existing links by URL
        link_map = {link.url: link for link in existing_links}

        if url in link_map:
            # Update existing link
            link = link_map[url]
            link.title = f"Wiz Entity: {get_value(issue, WIZ_ASSET_NAME)}"
            link.lastUpdatedById = user_id
            return link

        # Create new link
        return Link(
            parentID=0,  # Temporarily set to 0; will be updated after issue creation.
            parentModule="issues",
            url=url,
            title=f"Wiz Entity: {get_value(issue, WIZ_ASSET_NAME)}",
            createdById=user_id,
            lastUpdatedById=user_id,
        )

    def get_control_impl_id_from_control_id_string(self, control_id_string: str) -> int:
        """
        Get the control ID from the control ID string
        :param str control_id_string: The control ID string
        :return: The control implementation ID
        :rtype: int
        """
        return self.control_impl_controlid_dict.get(control_id_string.lower())

    def _create_issue(self, **kwargs):
        """
        Create a RegScale issue from a Wiz issue
        :param issue: Wiz issue dictionary
        :param user_id: User ID to assign the issue to
        :param parent_id the regscale model to which the issue is attached
        :param parent_module the regscale model to which the issue is attached
        :param identifier: Asset identifiers
        :param unknown_title: Unknown title
        :param due_date_str: Due date string
        """
        issue = kwargs.get("issue")
        subcategories_list_of_dict = get_value(issue, "sourceRule.securitySubCategories")
        control_id_strings_list = []

        if subcategories_list_of_dict:
            control_ids_from_wiz = [subcat.get("externalId") for subcat in subcategories_list_of_dict]
            for wiz_control_id in control_ids_from_wiz:
                control_id_strings_list.append(self.get_control_impl_id_from_control_id_string(wiz_control_id.lower()))

            for control_id in control_id_strings_list:
                new_issue = self._create_issue_from_wiz_data(**kwargs)
                new_issue.controlId = control_id

                if new_issue not in self.issues_to_create:
                    self.issues_to_create.append(new_issue)
        else:
            new_issue = self._create_issue_from_wiz_data(**kwargs)
            new_issue.controlId = self.get_control_impl_id_from_control_id_string("CM-6(5)") or None
            self.issues_to_create.append(new_issue)

    def _create_issue_from_wiz_data(self, **kwargs) -> regscale_models.Issue:
        """
        Create a RegScale issue from Wiz data
        param issue: Wiz issue dictionary
        :param user_id: User ID to assign the issue to
        :param parent_id the regscale model to which the issue is attached
        :param parent_module the regscale model to which the issue is attached
        :param identifier: Asset identifiers
        :param unknown_title: Unknown title
        :param due_date_str: Due date string
        :return: The created RegScale issue
        :rtype: regscale_models.Issue
        """
        issue = kwargs.get("issue")
        wiz_id = get_value(issue, WIZ_ASSET_ID)
        user_id = kwargs.get("user_id")
        parent_id = kwargs.get("parent_id")
        parent_module = kwargs.get("parent_module")
        identifier = kwargs.get("identifier")
        unknown_title = kwargs.get("unknown_title")
        due_date_str = kwargs.get("due_date_str")
        status = self.map_status(get_value(issue, "status"))
        asset: regscale_models.Asset = self.asset_dict.get(
            get_value(issue, WIZ_ASSET_ID),
        )
        additional_data = self.prepare_additional_data(
            issue=issue,
            user_id=user_id,
        )
        issue = Issue(
            title=get_value(issue, "sourceRule.name") or unknown_title,
            description=get_value(issue, "sourceRule.cloudConfigurationRuleDescription"),
            dateCreated=get_value(issue, "createdAt"),
            dateLastUpdated=get_value(issue, "updatedAt"),
            status=status,
            severityLevel=self.map_severity_level(issue),
            recommendedActions=get_value(issue, "sourceRule.remediationInstructions"),
            assetIdentifier=identifier,
            dueDate=due_date_str,
            issueOwnerId=user_id,
            createdById=user_id,
            dateFirstDetected=get_value(issue, "createdAt"),
            lastUpdatedById=user_id,
            parentId=asset.id if asset else parent_id,
            securityPlanId=self.regscale_id,
            parentModule=asset.get_module_slug() if asset else parent_module,
            dateCompleted=(
                get_value(issue, "resolvedAt") if get_value(issue, "resolvedAt") and status != "Open" else None
            ),
            identification="Wiz",
            sourceReport="Wiz",
            wizId=get_value(issue, WIZ_ASSET_ID),
            securityChecks=get_value(issue, SOURCE_ID),
            pluginId=get_value(issue, SOURCE_ID),
            otherIdentifier=get_value(issue, "entitySnapshot.externalId"),
        )
        self.set_is_poam_and_due_date_on_issue(issue)
        self.additional_data[wiz_id] = additional_data
        return issue

    @staticmethod
    def map_status(status: str) -> str:
        """
        Map Wiz status to RegScale status
        :param str status: Wiz status
        :return str: RegScale status
        :rtype str: str
        """
        wiz_status = status
        if wiz_status == "OPEN":
            return IssueStatus.Open.value
        if wiz_status == "RESOLVED":
            return IssueStatus.Closed.value
        if wiz_status == "IN_PROGRESS":
            return IssueStatus.Open.value
        if wiz_status == "REJECTED":
            return IssueStatus.Cancelled.value
        return IssueStatus.Open.value

    @staticmethod
    def process_issue_due_date(
        severity_level: str,
    ) -> str:
        """
        Process issue due date
        :param str severity_level: Severity level
        :return: due date str
        :rtype: str
        """
        app = Application()
        config = app.config
        fmt = "%Y-%m-%d %H:%M:%S"

        # Default days setting for unspecified severity levels
        default_days = config.get("issues", {}).get("wiz", {}).get("default", 0)
        days = config.get("issues", {}).get("wiz", {}).get(severity_level.lower(), default_days)

        try:
            days = int(days)
        except ValueError:
            # Handle non-integer 'days' gracefully
            days = default_days

        due_date = datetime.now() + timedelta(days=days)
        return due_date.strftime(fmt)

    @staticmethod
    def map_severity_level(wiz_issue: Dict) -> str:
        """
        Map Wiz severity level to RegScale severity level
        :param Dict wiz_issue: Wiz issue dictionary containing the severity level
        :return str: RegScale severity level
        :rtype str: str
        """
        severity = get_value(wiz_issue, "severity")
        if not severity:
            return IssueSeverity.NotAssigned.value
        if isinstance(severity, str):
            return SEVERITY_MAP.get(severity, "Low")
        return IssueSeverity.NotAssigned.value

    @staticmethod
    def build_link(data: Dict) -> Optional[Link]:
        """
        Build a link to the Wiz issue
        :param Dict data: The Wiz issue data
        :return Optional[Link]: The link to the Wiz issue or None if the link is not found
        :rtype Optional[Link]: Optional[Link]
        """
        url = get_value(data, CLOUD_PROVIDER_URL_FIELD)
        if not url and not isinstance(url, str):
            return None
        return Link(url=url, title=f"Wiz Entity: {get_value(data, WIZ_ASSET_NAME)}")
