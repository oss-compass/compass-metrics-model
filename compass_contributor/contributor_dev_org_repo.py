import json
import yaml
import re
import logging
from datetime import datetime, timedelta
import urllib3
from compass_common.datetime import (datetime_utcnow, str_to_datetime, datetime_to_utc, get_date_list, check_times_has_overlap)
from compass_common.uuid_utils import get_uuid
from compass_common.opensearch_utils import get_all_index_data, get_generator, get_client, get_helpers as helpers
from compass_common.datetime import get_latest_date, get_oldest_date
from compass_common.list_utils import split_list
from compass_metrics.contributor_metrics import contributor_eco_type_list
from compass_metrics.git_metrics import created_since
from compass_metrics.db_dsl import get_base_index_mapping
from compass_contributor.contributor_org import ContributorOrgService
from compass_contributor.organization import OrganizationService
from compass_contributor.bot import BotService
from collections import deque
import pkg_resources

logger = logging.getLogger(__name__)
urllib3.disable_warnings()
page_size = 1000
MAX_BULK_UPDATE_SIZE = 500




exclude_field_list = ["unknown", "-- undefined --"]

def exclude_special_str(str):
    """ For strings of author names, exclude special characters. """
    regEx = "[`~!#$%^&*()+=|{}':;',\\[\\]<>/?~！#￥%……&*（）——+|{}【】‘；：”“’\"\"。 ，、？]"
    return re.sub(regEx, "",str)

def get_organizations_info():
    """ Get profile data to determine which organization a contributor belongs to. """
    organizations_dict = {}
    organizations_json_data = pkg_resources.resource_string('compass_contributor', 'conf_utils/organizations.json')
    organizations_config = json.loads(organizations_json_data.decode('utf-8'))
    for org_name in organizations_config["organizations"].keys():
        for domain in organizations_config["organizations"][org_name]:
            organizations_dict[domain["domain"]] = org_name
    return organizations_dict

def get_bots_info(source):
    """ Get the profile data to determine if a contributor is a bot. """
    common = []
    community_dict = {}
    repo_dict = {}
    
    bots_json_data = pkg_resources.resource_string('compass_contributor', 'conf_utils/bots.json')
    bots_config = json.loads(bots_json_data.decode('utf-8'))
    source_data = bots_config[source]
    if source_data.get("contributor") and len(source_data.get("contributor")) > 0:
        common = source_data.get("contributor")
    for community, community_values in source_data["community"].items():
        if community_values.get("contributor") and len(community_values.get("contributor")) > 0:
            community_dict[community] = community_values.get("contributor")
        if community_values.get("repo"):
            for repo, repo_values in community_values["repo"].items():
                if repo_values.get("contributor") and len(repo_values.get("contributor")) > 0:
                    repo_dict[repo] = repo_values.get("contributor")
    bots_dict = {
        "common": common,
        "community": community_dict,
        "repo": repo_dict
    }
    return bots_dict

def get_all_repo(json_file, origin):
    all_repo = []
    all_repo_json = json.load(open(json_file))
    for project in all_repo_json:
        origin_software_artifact = origin + "-software-artifact"
        origin_governance = origin + "-governance"
        for key in all_repo_json[project].keys():
            if key == origin_software_artifact or key == origin_governance or key == origin:
                for repo in all_repo_json[project].get(key):
                    all_repo.append(repo)
    return all_repo

def get_email_prefix_domain(email):
    """ Get mailbox prefixes and suffixes """
    email_prefix = None
    domain = None
    try:
        email_prefix = email.split("@")[0]
        domain = email.split("@")[1]
    except (IndexError, AttributeError):
        return email_prefix, domain
    return email_prefix, domain


class ContributorDevOrgRepo:
    def __init__(self, json_file, issue_index, pr_index, issue_comments_index, pr_comments_index, git_index, 
                contributors_index, contributors_enriched_index, from_date, end_date, repo_index, event_index=None, 
                company=None, stargazer_index=None, fork_index=None, level=None, community=None, contributors_org_index=None,
                organizations_index=None, bots_index=None):
        """ Build a contributor profile of the repository, including issues, pr, commit, organization, etc.
        :param json_file: the path of json file containing repository message.
        :param identities_config_file: the path of json file containing contributor identity message.
        :param organizations_index: organizations index.
        :param bots_index: bots index
        :param issue_index: Issue index
        :param pr_index: pr index
        :param issue_comments_index: issue comment index
        :param pr_comments_index: pr comment index
        :param git_index: git index
        :param contributors_index: contributor index
        :param contributors_enriched_index: contributors_enriched_index
        :param from_date: the beginning of time for contributor profile
        :param end_date: the end of time for contributor profile
        :param repo_index: repo index
        :param event_index: issue and pr event index
        :param company: the company this warehouse belongs to
        :param stargazer_index: stargazer index
        :param fork_index: fork index
        :param contributors_org_index: contributors org index
        :param level: choose from repo, community.
        :param community: used to mark the repo belongs to which community.
        """
        self.issue_index = issue_index
        self.pr_index = pr_index
        self.issue_comments_index = issue_comments_index
        self.pr_comments_index = pr_comments_index
        self.git_index = git_index
        self.repo_index = repo_index
        self.contributors_index = contributors_index
        self.contributors_enriched_index = contributors_enriched_index
        self.from_date = from_date
        self.end_date = end_date
        self.organizations_index = organizations_index
        self.bots_index = bots_index
        self.company = None if company or company == 'None' else company
        self.event_index = event_index
        self.stargazer_index = stargazer_index
        self.fork_index = fork_index
        self.contributors_org_index = contributors_org_index
        self.level = level
        self.community = community
        self.client = None
        self.source = 'gitee' if 'gitee' in issue_index else 'github'
        self.all_repo = get_all_repo(json_file, self.source)

        self.platform_item_id_dict = {}
        self.platform_item_identity_dict = {}
        self.git_item_id_dict = {}
        self.git_item_identity_dict = {}
        self.date_field_list = []

    def run(self, elastic_url):
        """Run tasks"""
        self.elastic_url = elastic_url
        self.client = get_client(elastic_url)
        exist = self.client.indices.exists(index=self.contributors_index)
        if not exist:
            self.client.indices.create(index=self.contributors_index, body=get_base_index_mapping())
        self.organizations_dict = OrganizationService(self.elastic_url, self.organizations_index).get_dict_domain_exist() \
            if self.organizations_index else get_organizations_info()
        self.bots_dict = BotService(self.elastic_url, self.bots_index).get_dict_by_source(self.source) \
            if self.bots_index else get_bots_info(self.source)
        for repo in self.all_repo:
            self.processing_data(repo)
            self.client.indices.flush(index=self.contributors_index) #Ensure that data has been saved to ES
            self.contributor_enrich(repo)

    def processing_data(self, repo):
        """ Start processing data, generate contributor profiles """
        logger.info(repo + " start")
        start_time = datetime.now()
        self.platform_item_id_dict = {}
        self.platform_item_identity_dict = {}
        self.git_item_id_dict = {}
        self.git_item_identity_dict = {}
        self.date_field_list = []
        self.admin_date_field_list = []
        platform_index_type_dict = {
            # observe 
            "fork": {"index": self.fork_index, "date_field": "fork_date_list"},
            "star": {"index": self.stargazer_index, "date_field": "star_date_list"},
            # issue
            "issue_creation": {"index": self.issue_index, "date_field": "issue_creation_date_list"},
            "issue_comments": {"index": self.issue_comments_index, "date_field": "issue_comments_date_list"},
            # issue admin
            "issue_LabeledEvent": {"index": self.event_index, "date_field": "issue_labeled_date_list"},
            "issue_UnlabeledEvent": {"index": self.event_index, "date_field": "issue_unlabeled_date_list"},
            "issue_ClosedEvent": {"index": self.event_index, "date_field": "issue_closed_date_list"},
            "issue_ReopenedEvent": {"index": self.event_index, "date_field": "issue_reopened_date_list"},
            "issue_AssignedEvent": {"index": self.event_index, "date_field": "issue_assigned_date_list"},
            "issue_UnassignedEvent": {"index": self.event_index, "date_field": "issue_unassigned_date_list"},
            "issue_MilestonedEvent": {"index": self.event_index, "date_field": "issue_milestoned_date_list"},
            "issue_DemilestonedEvent": {"index": self.event_index, "date_field": "issue_demilestoned_date_list"},
            "issue_MarkedAsDuplicateEvent": {"index": self.event_index, "date_field": "issue_marked_as_duplicate_date_list"},
            "issue_TransferredEvent": {"index": self.event_index, "date_field": "issue_transferred_date_list"},
            "issue_RenamedTitleEvent": {"index": self.event_index, "date_field": "issue_renamed_title_date_list"},
            "issue_ChangeDescriptionEvent": {"index": self.event_index, "date_field": "issue_change_description_date_list"},
            "issue_SettingPriorityEvent": {"index": self.event_index, "date_field": "issue_setting_priority_date_list"},
            "issue_ChangePriorityEvent": {"index": self.event_index, "date_field": "issue_change_priority_date_list"},
            "issue_LinkPullRequestEvent": {"index": self.event_index, "date_field": "issue_link_pull_request_date_list"},
            "issue_UnlinkPullRequestEvent": {"index": self.event_index, "date_field": "issue_unlink_pull_request_date_list"},
            "issue_AssignCollaboratorEvent": {"index": self.event_index, "date_field": "issue_assign_collaborator_date_list"},
            "issue_UnassignCollaboratorEvent": {"index": self.event_index, "date_field": "issue_unassign_collaborator_date_list"},
            "issue_ChangeIssueStateEvent": {"index": self.event_index, "date_field": "issue_change_issue_state_date_list"},
            "issue_ChangeIssueTypeEvent": {"index": self.event_index, "date_field": "issue_change_issue_type_date_list"},
            "issue_SettingBranchEvent": {"index": self.event_index, "date_field": "issue_setting_branch_date_list"},
            "issue_ChangeBranchEvent": {"index": self.event_index, "date_field": "issue_change_branch_date_list"},
            # code
            "pr_creation": {"index": self.pr_index, "date_field": "pr_creation_date_list"},
            "pr_comments": {"index": self.pr_comments_index, "date_field": "pr_comments_date_list"},
            # code admin
            "pr_LabeledEvent": {"index": self.event_index, "date_field": "pr_labeled_date_list"},
            "pr_UnlabeledEvent": {"index": self.event_index, "date_field": "pr_unlabeled_date_list"},
            "pr_ClosedEvent": {"index": self.event_index, "date_field": "pr_closed_date_list"},
            "pr_AssignedEvent": {"index": self.event_index, "date_field": "pr_assigned_date_list"},
            "pr_UnassignedEvent": {"index": self.event_index, "date_field": "pr_unassigned_date_list"},
            "pr_ReopenedEvent": {"index": self.event_index, "date_field": "pr_reopened_date_list"},
            "pr_MilestonedEvent": {"index": self.event_index, "date_field": "pr_milestoned_date_list"},
            "pr_DemilestonedEvent": {"index": self.event_index, "date_field": "pr_demilestoned_date_list"},
            "pr_MarkedAsDuplicateEvent": {"index": self.event_index, "date_field": "pr_marked_as_duplicate_date_list"},
            "pr_TransferredEvent": {"index": self.event_index, "date_field": "pr_transferred_date_list"},
            "pr_RenamedTitleEvent": {"index": self.event_index, "date_field": "pr_renamed_title_date_list"},
            "pr_ChangeDescriptionEvent": {"index": self.event_index, "date_field": "pr_change_description_date_list"},
            "pr_SettingPriorityEvent": {"index": self.event_index, "date_field": "pr_setting_priority_date_list"},
            "pr_ChangePriorityEvent": {"index": self.event_index, "date_field": "pr_change_priority_date_list"},
            "pr_MergedEvent": {"index": self.event_index, "date_field": "pr_merged_date_list"},
            "pr_PullRequestReview": {"index": self.event_index, "date_field": "pr_review_date_list"},
            "pr_SetTesterEvent": {"index": self.event_index, "date_field": "pr_set_tester_date_list"},
            "pr_UnsetTesterEvent": {"index": self.event_index, "date_field": "pr_unset_tester_date_list"},
            "pr_CheckPassEvent": {"index": self.event_index, "date_field": "pr_check_pass_date_list"},
            "pr_TestPassEvent": {"index": self.event_index, "date_field": "pr_test_pass_date_list"},
            "pr_ResetAssignResultEvent": {"index": self.event_index, "date_field": "pr_reset_assign_result_date_list"},
            "pr_ResetTestResultEvent": {"index": self.event_index, "date_field": "pr_reset_test_result_date_list"},
            "pr_LinkIssueEvent": {"index": self.event_index, "date_field": "pr_link_issue_date_list"},
            "pr_UnlinkIssueEvent": {"index": self.event_index, "date_field": "pr_unlink_issue_date_list"},
        }
        if self.git_index is not None:
            git_date_field_list = ["code_author_date_list", "code_committer_date_list", "code_review_date_list"]
            self.date_field_list.extend(git_date_field_list)
            self.date_field_list.append("code_direct_commit_date_list")
            self.admin_date_field_list.append("code_direct_commit_date_list")
            self.processing_commit_data(self.git_index, repo, self.from_date, self.end_date)
        for index_key, index_values in platform_index_type_dict.items():
            if index_values["index"]:
                if index_values["index"] == self.event_index:
                    self.admin_date_field_list.append(index_values["date_field"])
                self.date_field_list.append(index_values["date_field"])
                self.processing_platform_data(index_values["index"], repo, self.from_date, self.end_date, index_values["date_field"], type=index_key)
        
        if len(self.platform_item_id_dict) == 0 and len(self.git_item_id_dict) == 0:
            logger.info(repo + " finish count:" + str(0) + " " + str(datetime.now() - start_time))
            return

        all_items_dict = self.get_merge_platform_git_contributor_data(repo, self.git_item_id_dict, self.platform_item_id_dict)
        contributor_org_dict = {}
        if self.contributors_org_index:
            contributor_org_service = ContributorOrgService(self.elastic_url, self.contributors_org_index, self.source)
            contributor_org_dict = contributor_org_service.get_dict_by_contributor_name(
                contributor_name_list=self.get_contributor_name_list(all_items_dict),
                level=self.level,
                label=self.community if self.level == 'community' else repo
            )
        self.delete_contributor(repo, self.contributors_index)
        logger.info(repo + "  save data...")
        all_bulk_data = []
        community =repo.split("/")[-2]
        platform_type = repo.split("/")[-3].split(".")[0]
        for item in all_items_dict.values():
            id_git_author_name_list = list(item.get("id_git_author_name_list", []))
            id_git_author_email_list = list(item.get("id_git_author_email_list", []))
            id_platform_login_author_name_list = list(item.get("id_platform_login_author_name_list", []))
            id_platform_login_name_list = list(item.get("id_platform_login_name_list", []))
            id_platform_author_name_list = list(item.get("id_platform_author_name_list", []))
            id_platform_author_email_list = list(item.get("id_platform_author_email_list", []))
            id_git_author_name_list.sort()
            id_git_author_email_list.sort()
            id_platform_login_author_name_list.sort()
            id_platform_login_name_list.sort()
            id_platform_author_name_list.sort()
            id_platform_author_email_list.sort()

            contribution_date_field_dict = {}
            for date_field in self.date_field_list:
                contribution_date_list = list(item.get(date_field, []))
                contribution_date_list.sort()
                contribution_first_date = contribution_date_list[0] if len(contribution_date_list) > 0 else None
                contribution_date_field_dict[date_field] = contribution_date_list
                contribution_date_field_dict["first_" + date_field.replace("_list", "")] = contribution_first_date

            org_change_date_list, email_org_list, is_bot = self.get_org_change_date_list_and_bot(repo, item, contributor_org_dict)
            admin_date_list = []
            min_admin_date, max_admin_date = self.get_admin_date(contribution_date_field_dict)
            if min_admin_date:
                admin_date_list.append({
                    "first_date": min_admin_date,
                    "last_date": max_admin_date
                })

            contributor_uuid = get_uuid(repo, id_platform_login_name_list[0] if id_platform_login_name_list else id_git_author_name_list[0])
            contributor_data = {
                "_index": self.contributors_index,
                "_id": contributor_uuid,
                "_source": {
                    "uuid": contributor_uuid,
                    "id_git_author_name_list": id_git_author_name_list,
                    "id_git_author_email_list": id_git_author_email_list,
                    "id_platform_login_author_name_list": id_platform_login_author_name_list,
                    "id_platform_login_name_list": id_platform_login_name_list,
                    "id_platform_author_name_list": id_platform_author_name_list,
                    "id_platform_author_email_list": id_platform_author_email_list,
                    "id_identity_list": list(item.get("id_identity_list", [])),
                    **contribution_date_field_dict,
                    "last_contributor_date": item["last_contributor_date"],
                    "org_change_date_list": org_change_date_list,
                    "email_org_change_date_list": email_org_list,
                    "admin_date_list": admin_date_list,
                    "platform_type": platform_type,
                    "domain": org_change_date_list[len(org_change_date_list)-1]["domain"] if len(org_change_date_list) > 0 else None,
                    "org_name": org_change_date_list[len(org_change_date_list)-1]["org_name"] if len(org_change_date_list) > 0 else None,
                    "community": community,
                    "repo_name": repo,
                    "is_bot": is_bot,
                    "update_at_date": datetime_utcnow().isoformat()
                }
            }
            all_bulk_data.append(contributor_data)
            if len(all_bulk_data) > MAX_BULK_UPDATE_SIZE:
                helpers().bulk(client=self.client, actions=all_bulk_data, request_timeout=100)
                all_bulk_data = []
        helpers().bulk(client=self.client, actions=all_bulk_data, request_timeout=100)
        logger.info(repo + " finish count:" + str(len(all_items_dict)) + " " + str(datetime.now() - start_time))

    def processing_platform_data(self, index, repo, from_date, to_date, date_field, type="issue"):
        """ Start processing data, generate gitee or github contributor profiles """
        logger.info(f"{repo} {index}  {type} processing...")
        start_time = datetime.now()
        results = []
        if type == "issue_creation":
            results = self.get_issue_enrich_data(index, repo, from_date, to_date, page_size)
        elif type == "pr_creation":
            results = self.get_pr_enrich_data(index, repo, from_date, to_date, page_size)
        elif type == "issue_comments":
            results = self.get_issue_comment_enrich_data(index, repo, from_date, to_date, page_size)
        elif type == "pr_comments":
            results = self.get_pr_comment_enrich_data(index, repo, from_date, to_date, page_size)
        elif type in ["fork", "star"]:
            results = self.get_observe_enrich_data(index, repo, from_date, to_date, page_size)
        elif re.match(r"^issue_.*Event$", type):
            results = self.get_issue_event_enrich_data(index, repo, from_date, to_date, page_size, type.replace("issue_", ""))
        elif re.match(r"^pr_.*Event$", type) or type in "pr_PullRequestReview":
            results = self.get_pr_event_enrich_data(index, repo, from_date, to_date, page_size, type.replace("pr_", ""))

        count = 0
        for result in results:
            source = result["_source"]
            grimoire_creation_date = datetime_to_utc(
                str_to_datetime(source["grimoire_creation_date"]).replace(tzinfo=None) + timedelta(microseconds=int(source["uuid"], 16) % 100000)).isoformat()
            user_login = source.get("user_login")
            if user_login is None:
                continue
            id_identity_list = [
                user_login,
                source.get("auhtor_name") or source.get("actor_name"),
                source.get("user_email")
            ]
            id_identity_list = set(
                [exclude_special_str(x.lower()) for x in id_identity_list if x and x.lower() not in exclude_field_list and exclude_special_str(x) ])
            org_change_date_list = []
            org_name = None
            domain = None
            if source.get("user_email") is not None :
                domain = get_email_prefix_domain(source.get("user_email"))[1]
                if domain is not None:
                    org_name = self.get_org_name_by_email(source.get("user_email"))
            if org_name is None:      
                org_name = source.get('user_org', source.get('user_company', None))
                if org_name is not None:
                    org_name = org_name.strip()
                    org_name = self.organizations_dict[org_name.lower()] if self.organizations_dict.get(org_name.lower()) else org_name
            if any([org_name, domain]):
                org_date = {
                    "domain": domain,
                    "org_name": org_name,
                    "first_date": grimoire_creation_date,
                    "last_date": grimoire_creation_date
                }
                org_change_date_list.append(org_date)
            item = {
                "uuid": get_uuid(repo, "platform", user_login, source.get("user_email"), grimoire_creation_date),
                "id_platform_login_name_list": set([user_login] if user_login else []),
                "id_platform_author_name_list": set([source.get("author_name")] if source.get("author_name") else []),
                "id_platform_author_email_list": set([source.get("user_email")] if source.get("user_email") else []),
                "id_identity_list": id_identity_list,
                date_field: {grimoire_creation_date},
                "last_contributor_date": grimoire_creation_date,
                "org_change_date_list": org_change_date_list
            }

            old_item_dict = {}
            for identity in id_identity_list:
                if identity in self.platform_item_identity_dict.keys() and self.platform_item_identity_dict[identity] in self.platform_item_id_dict.keys():
                    old_item = self.platform_item_id_dict.pop(self.platform_item_identity_dict[identity])
                    old_item_dict[old_item["uuid"]] = old_item
            if len(old_item_dict) > 0:
                item = self.get_merge_old_new_contributor_data(old_item_dict, {item["uuid"]: item})[0][item["uuid"]]

            self.platform_item_id_dict[item["uuid"]] = item
            for identity in item["id_identity_list"]:
                self.platform_item_identity_dict[identity] = item["uuid"]
            count += 1
        logger.info(repo + " " + index + " finish count:" + str(count) + " " + str(datetime.now() - start_time))

    def processing_commit_data(self, index, repo, from_date, to_date):
        """ Start processing data, generate commit contributor profiles """

        def get_signed_off_and_reviewed(msg):
            """ Getting signed_off_by and reviewed_by user information from commit message """
            signed_off_dict = {}
            reviewed_dict = {}
            if not msg:
                return signed_off_dict, reviewed_dict
            for line in msg.splitlines():
                if line.startswith("Signed-off-by: "):
                    try:
                        signed_off_by_split = line.replace("Signed-off-by: ", "").split(" <")
                        if len(signed_off_by_split) == 2:
                            author_name = signed_off_by_split[0].strip()
                            if not author_name:
                                continue
                            email = signed_off_by_split[1].replace(">", "").strip()
                            signed_off_dict[author_name] = {
                                "type": "code_author",
                                "author_name": author_name,
                                "author_email": email
                            }
                    except Exception as e:
                        logger.info(e)
                elif line.startswith("Reviewed-by: "):
                    try:
                        reviewed_by_split = line.replace("Reviewed-by: ", "").split(" <")
                        if len(reviewed_by_split) == 2:
                            author_name = reviewed_by_split[0].strip()
                            if not author_name:
                                continue
                            email = reviewed_by_split[1].replace(">", "").strip()
                            reviewed_dict[author_name] = {
                                "type": "code_review",
                                "author_name": author_name,
                                "author_email": email
                            }
                    except Exception as e:
                        logger.info(e)
            return signed_off_dict, reviewed_dict

        def get_author_list(commit_source):
            signed_off_dict, reviewed_dict = get_signed_off_and_reviewed(commit_source.get("message_analyzed", ""))
            signed_off_dict[commit_source.get("author_name")] = {
                "type": "code_author",
                "author_name": commit_source.get("author_name"),
                "author_email": commit_source.get("author_email", None)
            }
            committer_dict = {
                "type": "code_committer",
                "author_name": commit_source.get("committer_name"),
                "author_email": commit_source.get("committer_email", None)
            }
            author_list = []
            if signed_off_dict:
                author_list.extend(list(signed_off_dict.values()))
            if reviewed_dict:
                author_list.extend(list(reviewed_dict.values()))
            if commit_source.get("committer_name") not in signed_off_dict:
                author_list.append(committer_dict)
            return author_list


        logger.info(repo + " " + index + " processing...")
        created_at = self.get_repo_created(repo)
        start_time = datetime.now()
        
        commit_hash = self.get_commit_hash_data(index, repo, from_date, to_date, page_size)
        pr_hits = []
        hash_list = [result["_source"]["hash"] for result in commit_hash]
        hash_list_group = split_list(hash_list)
        for hash_l in hash_list_group:
            pr_hit = self.get_pr_list_by_commit_hash(repo, hash_l)
            pr_hits = pr_hits + pr_hit
        pr_data_dict = {}
        for pr_hit in pr_hits:
            if pr_hit["_source"].get("merge_commit_sha"):
                pr_data_dict[pr_hit["_source"]["merge_commit_sha"]] = pr_hit["_source"]
            for pr_commit_hash in pr_hit["_source"]["commits_data"]:
                pr_data_dict[pr_commit_hash] = pr_hit["_source"]

        results = self.get_commit_enrich_data(index, repo, from_date, to_date, page_size)
        count = 0
        for result in results:
            source = result["_source"]
            if source.get("author_name") is None:
                continue
            grimoire_creation_date = datetime_to_utc(
                str_to_datetime(source["grimoire_creation_date"]).replace(tzinfo=None) + timedelta(microseconds=int(source["uuid"], 16) % 100000)).isoformat()
            
            code_direct_commit_date = None
            if grimoire_creation_date >= created_at and source["hash"] not in pr_data_dict \
                    and (
                        (self.source == "github" and len(source["parents"]) <= 1 and source["committer_name"] == "GitHub" and source["committer_email"] == "noreply@github.com")
                        or (self.source == "gitee" and len(source["parents"]) <= 1 and source["committer_name"] == "Gitee" and source["committer_email"] == "noreply@gitee.com")
                            or (self.source == "github" and source["committer_name"] == source["author_name"] and source["committer_email"] == source["author_email"])
                            ):
                code_direct_commit_date = grimoire_creation_date
            
            author_list = get_author_list(source)
            for author_item in author_list:
                author_name = author_item["author_name"]
                if author_name is None or not isinstance(author_name, str) or author_name in ["GitHub", "Gitee"]:
                    continue
                author_type = author_item["type"]
                date_field = author_type + "_date_list"
                id_identity_list = [author_item["author_name"], author_item["author_email"]]
                id_identity_list = set(
                    [exclude_special_str(x.lower()) for x in id_identity_list if x and x.lower() not in exclude_field_list and exclude_special_str(x) ])
                org_change_date_list = []
                if author_item["author_email"] is not None:
                    domain = get_email_prefix_domain(author_item["author_email"])[1]
                    if domain is not None:
                        org_name = self.get_org_name_by_email(author_item["author_email"])
                        org_date = {
                            "domain": domain,
                            "org_name": org_name,
                            "first_date": grimoire_creation_date,
                            "last_date": grimoire_creation_date
                        }
                        org_change_date_list.append(org_date)
                item = {
                    "uuid": get_uuid(repo, "git", author_item["author_name"], author_item["author_email"], grimoire_creation_date),
                    "id_git_author_name_list": set([author_item.get("author_name")] if author_item.get("author_name") else []),
                    "id_git_author_email_list": set([author_item.get("author_email")] if author_item.get("author_email") else []),
                    "id_identity_list": id_identity_list,
                    date_field: {grimoire_creation_date},
                    "last_contributor_date": grimoire_creation_date,
                    "org_change_date_list": org_change_date_list
                }
                if author_type == "code_author" and author_item["author_name"] == source["author_name"]:
                    item["code_direct_commit_date_list"] = {code_direct_commit_date} if code_direct_commit_date else set()

                old_item_dict = {}
                for identity in id_identity_list:
                    if identity in self.git_item_identity_dict.keys() and self.git_item_identity_dict[identity] in self.git_item_id_dict.keys():
                        old_item = self.git_item_id_dict.pop(self.git_item_identity_dict[identity])
                        old_item_dict[old_item["uuid"]] = old_item
                if len(old_item_dict) > 0:
                    item = self.get_merge_old_new_contributor_data(old_item_dict, {item["uuid"]: item})[0][item["uuid"]]

                self.git_item_id_dict[item["uuid"]] = item
                for identity in item["id_identity_list"]:
                    self.git_item_identity_dict[identity] = item["uuid"]
                count += 1
        logger.info(repo + " " + index + " finish count:" + str(count) + " " + str(datetime.now() - start_time))

    def get_merge_org_change_date(self, old_data_list, new_data_list):
        """ Consolidation of information on the same organization """
        result_data_list = []
        old_data_dict = {}
        for old_data in old_data_list:
            if old_data.get('org_name'):
                old_data_dict[old_data.get('org_name')] = old_data
            elif old_data.get('domain'):
                old_data_dict[old_data.get('domain')] = old_data
        for new_data in new_data_list:
            data_dict = new_data.copy()
            old_data = {}
            if new_data.get('org_name') and new_data.get('org_name') in old_data_dict:
                old_data = old_data_dict.pop(new_data.get('org_name'))
                data_dict = {
                    "domain": data_dict["domain"] if data_dict.get("domain") else old_data.get("domain"),
                    "org_name": data_dict["org_name"] if data_dict.get("org_name") else old_data.get("org_name"),
                    "first_date": get_oldest_date(data_dict["first_date"], old_data["first_date"]),
                    "last_date": get_latest_date(data_dict["last_date"], old_data["last_date"])
                }
            if new_data.get('domain') and new_data.get('domain') in old_data_dict:
                old_data = old_data_dict.pop(new_data.get('domain'))
                data_dict = {
                    "domain": data_dict["domain"] if data_dict.get("domain") else old_data.get("domain"),
                    "org_name": data_dict["org_name"] if data_dict.get("org_name") else old_data.get("org_name"),
                    "first_date": get_oldest_date(data_dict["first_date"], old_data["first_date"]),
                    "last_date": get_latest_date(data_dict["last_date"], old_data["last_date"])
                }
            result_data_list.append(data_dict)
        if len(old_data_dict) > 0:
            for old_data in old_data_dict.values():
                result_data_list.append(old_data)
        return result_data_list

    def get_merge_platform_git_contributor_data(self, repo, git_data_dict, platform_data_dict):
        """ Merging platform contributors and commit contributors """
        new_git_data_dict = git_data_dict.copy()
        new_platform_data_dict = {}
        login_author_name_dict = self.get_platform_login_git_author_dict(repo)

        git_author_uuid_dict = {author_name: git_data["uuid"] for git_data in git_data_dict.values()
                                for author_name in git_data["id_git_author_name_list"]}
        for platform_data in platform_data_dict.values():
            for platform_login_name in platform_data["id_platform_login_name_list"]:
                if platform_login_name in login_author_name_dict:
                    for author_name in login_author_name_dict[platform_login_name]:
                        if git_author_uuid_dict.get(author_name):
                            git_data = new_git_data_dict.pop(git_author_uuid_dict[author_name], None)
                            if git_data:
                                platform_data = self.get_merge_contributor_data(platform_data, git_data)
            new_platform_data_dict[platform_data["uuid"]] = platform_data

        result_item_dict, merge_id_set = self.get_merge_old_new_contributor_data(new_git_data_dict, new_platform_data_dict)
        for commit_data in new_git_data_dict.values():
            if commit_data["uuid"] in merge_id_set:
                continue
            result_item_dict[commit_data["uuid"]] = commit_data
        return result_item_dict

    def get_platform_login_git_author_dict(self, repo):
        """Mappinging of get the login and commit author name from the pull requst information. """
        created_at = self.get_repo_created(repo)
        login_author_name_dict = {}
        query_dsl = self.get_enrich_dsl("tag", repo + ".git", self.from_date, self.end_date, page_size)
        query_dsl["query"]["bool"]["filter"].append({"range": {"grimoire_creation_date": {"gte": created_at}}})
        results = get_all_index_data(self.client, index=self.git_index, body=query_dsl)
        if len(results) == 0:
            return login_author_name_dict
        pr_hits = []
        hash_git_dict = {result["_source"]["hash"]:result for result in results}
        hash_set = set(hash_git_dict.keys())
        hash_list_group = split_list(list(hash_set))
        for hash_l in hash_list_group:
            pr_hit = self.get_pr_list_by_commit_hash(repo, hash_l)
            pr_hits = pr_hits + pr_hit
        pr_data_dict = {}
        for pr_hit in pr_hits:
            if pr_hit["_source"].get("merge_commit_sha"):
                pr_data_dict[pr_hit["_source"]["merge_commit_sha"]] = pr_hit["_source"]
            for pr_commit_hash in pr_hit["_source"]["commits_data"]:
                pr_data_dict[pr_commit_hash] = pr_hit["_source"]
        for hit in results:
            data = hit["_source"]
            commit_author_name = data["author_name"]
            commit_committer_name = data["committer_name"]
            if data["hash"] in pr_data_dict:
                pr_data = pr_data_dict[data["hash"]]
                merge_login = pr_data["merge_author_login"]
                create_login = pr_data["user_login"]
                if data["hash"] in pr_data["commits_data"] or len(data["parents"]) > 1:
                    # merge
                    pr_commit_author_name = {hash_git_dict.get(pr_commit_hash)["_source"]["author_name"] for pr_commit_hash in pr_data["commits_data"] if hash_git_dict.get(pr_commit_hash)}
                    if len(pr_commit_author_name) > 1:
                        continue
                    if len(data["parents"]) > 1 and pr_data.get("merge_commit_sha") is not None and data["hash"] in pr_data["merge_commit_sha"] \
                            and data["committer_name"] in "GitHub" and data["committer_email"] in "noreply@github.com":
                        author_set = login_author_name_dict.get(merge_login, set())
                        author_set.add(commit_author_name)
                        login_author_name_dict[merge_login] = author_set
                    elif data["hash"] in pr_data["commits_data"] and commit_author_name == commit_committer_name:
                        author_set = login_author_name_dict.get(create_login, set())
                        author_set.add(commit_author_name)
                        login_author_name_dict[create_login] = author_set
                else:
                    if data["committer_name"] in "GitHub" and data["committer_email"] in "noreply@github.com":
                        # squash
                        author_set = login_author_name_dict.get(create_login, set())
                        author_set.add(commit_author_name)
                        login_author_name_dict[create_login] = author_set
                    else:
                        # rebase
                        author_set = login_author_name_dict.get(create_login, set())
                        author_set.add(commit_author_name)
                        login_author_name_dict[create_login] = author_set

                        committer_set = login_author_name_dict.get(merge_login, set())
                        committer_set.add(commit_committer_name)
                        login_author_name_dict[merge_login] = committer_set
        return login_author_name_dict

    def get_git_list_by_hash_list(self, repo, hash_list):
        """ Get a list of commit details based on the hash of the commit. """
        git_query_dsl = self.get_enrich_dsl("tag", repo + ".git", "1970-01-01", "2099-01-01", page_size, [])
        git_query_dsl["query"]["bool"]["must"].append({"terms": {"hash": hash_list}})
        git_list = self.client.search(index=self.git_index, body=git_query_dsl)["hits"]["hits"]
        return git_list

    def get_merge_old_new_contributor_data(self, old_data_dict, new_data_dict):
        """ Merge old contributors into new contributors """
        result_item_dict = {}
        identity_dict = {identity: item for item in old_data_dict.values() for identity in item["id_identity_list"]}
        result_identity_uuid_dict = {}
        merge_id_set = set()
        for uuid, item in new_data_dict.items():
            old_data_list_dict = {}
            for identity in item["id_identity_list"]:
                if identity in identity_dict.keys():
                    old_data_list_dict[identity_dict[identity]["uuid"]] = identity_dict[identity]

            if len(old_data_list_dict) == 0:
                result_item_dict[uuid] = item
                continue
            for old_data in old_data_list_dict.values():
                if old_data["uuid"] in merge_id_set:
                    for identity in item["id_identity_list"]:
                        if identity in result_identity_uuid_dict.keys() and result_identity_uuid_dict[identity] in result_item_dict.keys():
                            old_data = result_item_dict.pop(result_identity_uuid_dict[identity])
                            break
                else:
                    merge_id_set.add(old_data["uuid"])
                item = self.get_merge_contributor_data(item, old_data)
            result_item_dict[item["uuid"]] = item
            for identity_list in item["id_identity_list"]:
                result_identity_uuid_dict[identity_list] = item["uuid"]
        return result_item_dict, merge_id_set

    def get_merge_contributor_data(self, contributor1, contributor2):
        """ Two contributors are the same person, merge them. """
        id_platform_login_name_list = contributor1.get("id_platform_login_name_list", set())
        id_platform_login_author_name_list = contributor1.get("id_platform_login_author_name_list", set())
        id_platform_author_name_list = contributor1.get("id_platform_author_name_list", set())
        id_platform_author_email_list = contributor1.get("id_platform_author_email_list", set())
        id_git_author_name_list = contributor1.get("id_git_author_name_list", set())
        id_git_author_email_list = contributor1.get("id_git_author_email_list", set())
        identity_list = contributor1.get("id_identity_list", set())
        org_change_date_list = contributor1.get("org_change_date_list", [])


        id_platform_login_name_list.update(
            set(contributor2["id_platform_login_name_list"] if contributor2.get("id_platform_login_name_list") else []))
        id_platform_login_author_name_list.update(
            set(contributor2["id_platform_login_author_name_list"] if contributor2.get("id_platform_login_author_name_list") else []))
        id_platform_author_name_list.update(
            set(contributor2["id_platform_author_name_list"] if contributor2.get("id_platform_author_name_list") else []))
        id_platform_author_email_list.update(
            set(contributor2["id_platform_author_email_list"] if contributor2.get("id_platform_author_email_list") else []))
        id_git_author_name_list.update(
            set(contributor2["id_git_author_name_list"] if contributor2.get("id_git_author_name_list") else []))
        id_git_author_email_list.update(
            set(contributor2["id_git_author_email_list"] if contributor2.get("id_git_author_email_list") else []))
        identity_list.update(set(contributor2["id_identity_list"] if contributor2.get("id_identity_list") else []))
        if contributor2.get("org_change_date_list") is not None:
            org_change_date_list = self.get_merge_org_change_date(contributor2.get("org_change_date_list"),
                                                                  org_change_date_list)

        contributor1["id_platform_login_name_list"] = id_platform_login_name_list
        contributor1["id_platform_login_author_name_list"] = id_platform_login_author_name_list
        contributor1["id_platform_author_name_list"] = id_platform_author_name_list
        contributor1["id_platform_author_email_list"] = id_platform_author_email_list
        contributor1["id_git_author_name_list"] = id_git_author_name_list
        contributor1["id_git_author_email_list"] = id_git_author_email_list
        contributor1["id_identity_list"] = identity_list

        for data_field in self.date_field_list:
            contribution_data_list = contributor1.get(data_field, set())
            contribution_data_list.update(
                set(contributor2[data_field] if contributor2.get(data_field) else []))
            contributor1[data_field] = contribution_data_list
        contributor1["last_contributor_date"] = get_latest_date(contributor1["last_contributor_date"],
                                                        contributor2["last_contributor_date"])
        contributor1["org_change_date_list"] = org_change_date_list
        return contributor1

    def get_enrich_dsl(self, repo_field, repo, from_date, to_date, page_size=100, source=None):
        """ Query statement to get enrich information """
        query = {
            "size": page_size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                repo_field: repo
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                "grimoire_creation_date": {
                                    "gte": from_date,
                                    "lte": to_date
                                }
                            }
                        }
                    ]
                }
            }
        }
        if source is not None:
            query["_source"] = source
        return query

    def get_issue_enrich_data(self, index, repo, from_date, to_date, page_size=100):
        """ Get issue data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
        results = get_generator(self.client, index=index, body=query_dsl)
        return results

    def get_pr_enrich_data(self, index, repo, from_date, to_date, page_size=100):
        """ Get pr data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
        results = get_generator(self.client, index=index, body=query_dsl)
        return results

    def get_issue_comment_enrich_data(self, index, repo, from_date, to_date, page_size=100):
        """ Get issue comment data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"issue_pull_request": "false"}})
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"item_type": "comment"}})
        results = get_generator(self.client, index=index, body=query_dsl)
        return results

    def get_pr_comment_enrich_data(self, index, repo, from_date, to_date, page_size=100):
        """ Get pr comment data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"item_type": "comment"}})
        results = get_generator(self.client, index=index, body=query_dsl)
        return results

    def get_observe_enrich_data(self, index, repo, from_date, to_date, page_size=100):
        """ Get fork or star data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size)
        results = get_generator(self.client, index=index, body=query_dsl)
        return results

    def get_issue_event_enrich_data(self, index, repo, from_date, to_date, page_size=100, type="LabeledEvent"):
        """ Get issue event data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"event_type": type}})
        gitee_event_creatable_by_creator = ["RenamedTitleEvent", "ChangeDescriptionEvent", "ChangeIssueStateEvent", "ChangeIssueTypeEvent"]
        github_event_creatable_by_creator = ["ClosedEvent", "ReopenedEvent", "RenamedTitleEvent"]
        if (self.source == "gitee" and type in gitee_event_creatable_by_creator) or (self.source == "github" and type in github_event_creatable_by_creator):
            query_dsl["query"]["bool"]["must"].append({
                "script": {
                    "script": "doc['actor_username'].size() > 0 && doc['reporter_user_name'].size() > 0 &&  doc['actor_username'].value != doc['reporter_user_name'].value"
                }
            })
        results = get_generator(self.client, index=index, body=query_dsl)
        return results

    def get_pr_event_enrich_data(self, index, repo, from_date, to_date, page_size=100, type="LabeledEvent"):
        """ Get pr event data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"event_type": type}})
        gitee_event_creatable_by_creator = ["LabeledEvent", "UnlabeledEvent", "ClosedEvent", "ReopenedEvent", "AssignedEvent", 
                "MilestonedEvent", "DemilestonedEvent", "RenamedTitleEvent", "ChangeDescriptionEvent", "SettingPriorityEvent",
                "ChangePriorityEvent", "SetTesterEvent", "LinkIssueEvent", "UnlinkIssueEvent"]
        github_event_creatable_by_creator = ["ClosedEvent", "ReopenedEvent", "RenamedTitleEvent"]
        if (self.source == "gitee" and type in gitee_event_creatable_by_creator) or (self.source == "github" and type in github_event_creatable_by_creator):
            query_dsl["query"]["bool"]["must"].append({
                "script": {
                    "script": "doc['actor_username'].size() > 0 && doc['reporter_user_name'].size() > 0 &&  doc['actor_username'].value != doc['reporter_user_name'].value"
                }
            })
        if type in "PullRequestReview":
            query_dsl["query"]["bool"]["must"].append({
                "terms": {
                    "merge_state": [
                        "APPROVED",
                        "CHANGES_REQUESTED",
                        "DISMISSED"
                    ]
                }
            })
        results = get_generator(self.client, index=index, body=query_dsl)
        return results

    def get_commit_enrich_data(self, index, repo, from_date, to_date, page_size=100):
        """ Get commit data list """
        query_dsl = self.get_enrich_dsl("tag", repo + ".git", from_date, to_date, page_size)
        results = get_generator(self.client, index=index, body=query_dsl)
        return results

    def get_commit_hash_data(self, index, repo, from_date, to_date, page_size=100):
        """ Get commit data list """
        source = ["hash"]
        query_dsl = self.get_enrich_dsl("tag", repo + ".git", from_date, to_date, page_size, source=source)
        results = get_all_index_data(self.client, index=index, body=query_dsl)
        return results

    def get_org_name_by_email(self, email):
        """ Return organization name based on email """
        domain = get_email_prefix_domain(email)[1]
        if domain is None:
            return None
        org_name = self.organizations_dict.get(domain)
        if "facebook.com" in domain:
            org_name = "Facebook"
        if ("noreply.gitee.com" in domain or "noreply.github.com" in domain) and self.company is not None:
            org_name = self.company
        return org_name

    def is_bot_by_author_name(self, repo, author_name):
        """ Determine if a bot is a bot by author name """
        try:
            author_name = str(author_name)
            common_list = self.bots_dict["common"]
            if len(common_list) > 0:
                for common in common_list:
                    regex = re.compile(common)
                    if regex.match(author_name):
                        return True
            community_dict = self.bots_dict["community"]
            if len(community_dict) > 0:
                for community, community_values in community_dict.items():
                    if community in repo and author_name in community_values:
                        return True
            repo_dict = self.bots_dict["repo"]
            if len(repo_dict) > 0:
                if repo_dict.get(repo) and author_name in repo_dict.get(repo):
                    return True
            return False
        except Exception as e:
            logger.info(f"Error: {e} repo: {repo} author_name: {author_name}")
            return False


    def get_admin_date(self, contributor_data):
        """ Getting the time to become a manager """
        min_date_list = []
        max_date_list = []
        for date_field in self.admin_date_field_list:
            contribution_date_list = contributor_data.get(date_field)
            if contribution_date_list:
                min_date_list.append(contribution_date_list[0])
                max_date_list.append(contribution_date_list[-1])
        if len(min_date_list) > 0:
             return min(min_date_list), max(max_date_list)
        return None, None

    def get_repo_created(self, repo):
        """ Get repository creation time """
        repo_query = {
            "size": 1,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                "origin": repo
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "metadata__enriched_on": {
                        "order": "desc"
                    }
                }
            ]
        }
        hits = self.client.search(index=self.repo_index, body=repo_query)["hits"]["hits"]
        created_at = hits[0]["_source"]["created_at"]
        return datetime_to_utc(str_to_datetime(created_at)).isoformat()

    def delete_contributor(self, repo, contributors_index, from_date=None, end_date=None):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                "repo_name.keyword": repo
                            }
                        }
                    ]
                }
            }
        }
        if from_date and end_date:
            query["query"]["bool"]["filter"] = [
                        {
                            "range": {
                                "grimoire_creation_date": {
                                    "gte": from_date,
                                    "lte": end_date
                                }
                            }
                        }
                    ]
        self.client.delete_by_query(index=contributors_index, body=query, request_timeout=100)

    def get_pr_list_by_commit_hash(self, repo, hash_list):
        """ Get PR list based on commit hash value """
        pr_query = {
            "size": 10000,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                "origin": repo
                            }
                        },
                        {
                            "match_phrase": {
                                "merged": "true"
                            }
                        }
                    ],
                    "should": [
                        {
                            "terms": {
                                "merge_commit_sha": hash_list
                            }
                        },
                        {
                            "terms": {
                                "commits_data": hash_list
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            }
        }
        pr_hits = self.client.search(index=self.pr_index, body=pr_query)[
            "hits"]["hits"]
        return pr_hits
        
    def contributor_enrich(self, repo):
        """ save enrichment contributor data for the past 90 days. """
        start_time = datetime.now()
        es_exist = self.client.indices.exists(index=self.contributors_enriched_index)
        if not es_exist:
            self.client.indices.create(index=self.contributors_enriched_index, body=get_base_index_mapping())
        date_list = get_date_list(self.from_date, self.end_date)
        count = 0
        item_datas = []
        self.delete_contributor(repo, self.contributors_enriched_index, self.from_date, self.end_date)
        for date in date_list:
            created_since_metric = created_since(self.client, self.git_index, date, [repo])
            if created_since_metric is None:
                continue
            from_date = date - timedelta(days=7)
            contributor_list = contributor_eco_type_list(self.client, self.contributors_index, from_date, date, [repo])["contributor_eco_type_list"]
            count += len(contributor_list)
            for item in contributor_list:
                item_uuid = get_uuid(item["contributor"], repo, str(date))
                contributor_data = {
                    "_index": self.contributors_enriched_index,
                    "_id": item_uuid,
                    "_source": {
                        "uuid": item_uuid,
                        "contributor": item["contributor"],
                        "contribution": item["contribution"],
                        "contribution_without_observe": item["contribution_without_observe"],
                        "ecological_type": item["ecological_type"],
                        "organization": item["organization"],
                        "contribution_type_list": item["contribution_type_list"],
                        "is_bot": item["is_bot"],
                        "repo_name": repo,
                        'grimoire_creation_date': date.isoformat(),
                        'metadata__enriched_on': datetime_utcnow().isoformat()
                    }
                }
                item_datas.append(contributor_data)
                if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                    helpers().bulk(client=self.client, actions=item_datas)
                    item_datas = []
        helpers().bulk(client=self.client, actions=item_datas)
        logger.info(repo + " contributor enrich data save finish count:" + str(count) + " " + str(datetime.now() - start_time))


    def find_non_overlap_ranges(self, start_time1, end_time1, start_time2, end_time2):
        non_overlap = []
        if check_times_has_overlap(start_time1, end_time1, start_time2, end_time2):
            if start_time2 < start_time1:
                non_overlap.append([start_time2, start_time1])
            if end_time2 > end_time1:
                non_overlap.append([end_time1, end_time2])
        else:
            non_overlap.append([start_time2, end_time2])
        return non_overlap

    def org_change_data_priority_processing(self, original_org_change_date_list):
        new_org_change_date_list = []
        for org_item in original_org_change_date_list:
            first_date, last_date = org_item["first_date"], org_item["last_date"]
            org_item_date_deque = deque()
            org_item_date_deque.append([first_date, last_date])
            for new_org_item in new_org_change_date_list:
                org_item_date_deque_tmp = deque()
                while org_item_date_deque:
                    date_item = org_item_date_deque.popleft()
                    non_overlap_date_list = self.find_non_overlap_ranges(
                        new_org_item["first_date"], new_org_item["last_date"], date_item[0], date_item[1])
                    for non_overlap_date_item in non_overlap_date_list:
                        org_item_date_deque_tmp.append(non_overlap_date_item)
                org_item_date_deque = org_item_date_deque_tmp
            for org_item_date in org_item_date_deque:
                new_org_change_date_list.append({
                    "domain": org_item.get("domain"),
                    "org_name": org_item.get("org_name"),
                    "first_date": org_item_date[0],
                    "last_date": org_item_date[1]
                })
        if new_org_change_date_list:
            return sorted(new_org_change_date_list, key=lambda x: x["first_date"])
        return new_org_change_date_list

    def get_org_change_date_list_and_bot(self, repo, item, contributor_org_dict):
        contributor_name = self.get_contributor_name(item)
        contributor_name_key_list = [
            f"User Individual&&{contributor_name}",
            f"System Admin&&{contributor_name}",
            f"Repo Admin&&{contributor_name}",
            f"URL&&{contributor_name}",
        ]
        org_change_date_list = []
        bot_list = []
        for contributor_name_key in contributor_name_key_list:
            if contributor_name_key in contributor_org_dict:
                contributor_org_info = contributor_org_dict[contributor_name_key]
                org_change_date_list.extend(contributor_org_info["org_change_date_list"])
                bot_list.append(contributor_org_info["is_bot"])
        email_org_list = list(item.get("org_change_date_list", []))
        if len(email_org_list) > 0:
            filtered_org_list = [org_item for org_item in email_org_list if org_item["org_name"]]
            if filtered_org_list:
                max_last_date_org = max(filtered_org_list, key=lambda obj: obj["last_date"])
                max_last_date_org["last_date"] = item["last_contributor_date"]
            email_org_list = sorted(email_org_list, key=lambda x: (x["org_name"] is None, x["org_name"]))
            org_change_date_list.extend(email_org_list)
        bot_list.append(self.is_bot_by_author_name(repo, contributor_name))
        result_org_change_date_list = self.org_change_data_priority_processing(org_change_date_list)
        return result_org_change_date_list, email_org_list, any(bot_list)

    def get_contributor_name_list(self, contributor_items):
        contributor_name_list = []
        for item in contributor_items.values():
            contributor_name = self.get_contributor_name(item)
            if contributor_name:
                contributor_name_list.append(contributor_name)
        return contributor_name_list

    def get_contributor_name(self, contributor_item):
        contributor_name = None
        id_git_author_name_list = list(contributor_item.get("id_git_author_name_list", []))
        id_platform_login_name_list = list(contributor_item.get("id_platform_login_name_list", []))
        id_git_author_name_list.sort()
        id_platform_login_name_list.sort()
        if len(id_platform_login_name_list) > 0:
            contributor_name = id_platform_login_name_list[0]
        elif len(id_git_author_name_list) > 0:
            contributor_name = id_git_author_name_list[0]
        return contributor_name

