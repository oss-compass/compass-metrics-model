import json
import yaml
import re
import logging
from datetime import datetime, timedelta
import urllib3
from elasticsearch import helpers
from compass_common.datetime import (datetime_utcnow, str_to_datetime, datetime_to_utc, get_date_list)
from compass_common.uuid_utils import get_uuid 
from compass_common.opensearch_client_utils import get_elasticsearch_client  
from compass_common.datetime import get_latest_date, get_oldest_date  
from compass_metrics.contributor_metrics import contributor_detail_list
from compass_metrics.git_metrics import created_since
import time

logger = logging.getLogger(__name__)
urllib3.disable_warnings()
page_size = 1000
MAX_BULK_UPDATE_SIZE = 5000

exclude_field_list = ["unknown", "-- undefined --"]

def exclude_special_str(str):
    """ For strings of author names, exclude special characters. """
    regEx = "[`~!#$%^&*()+=|{}':;',\\[\\]<>/?~！#￥%……&*（）——+|{}【】‘；：”“’\"\"。 ，、？]"
    return re.sub(regEx, "",str)

def get_organizations_info(file_path):
    """ Get profile data to determine which organization a contributor belongs to. """
    organizations_dict = {}
    organizations_config = json.load(open(file_path))
    for org_name in organizations_config["organizations"].keys():
        for domain in organizations_config["organizations"][org_name]:
            organizations_dict[domain["domain"]] = org_name
    return organizations_dict

def get_identities_info(file_path):
    """ Get profile data to identify the contributors """
    identities_dict = {}
    identities_config = yaml.safe_load(open(file_path))
    for identities in identities_config:
        for email in identities["email"]:
            enrollments = identities.get("enrollments")
            if enrollments is not None:
                identities_dict[email] = enrollments[0]["organization"]
    return identities_dict

def get_bots_info(file_path):
    """ Get the profile data to determine if a contributor is a bot. """
    bots_config = json.load(open(file_path))
    common = []
    community_dict = {}
    repo_dict = {}
    if bots_config.get("common") and bots_config["common"].get("pattern") and len(bots_config["common"].get("pattern")):
        common = bots_config["common"]["pattern"]
    for community, community_values in bots_config["community"].items():
        if community_values.get("author_name") and len(community_values.get("author_name")) > 0:
            community_dict[community] = community_values["author_name"]
        if community_values.get("repo"):
            for repo, repo_values in community_values["repo"].items():
                if repo_values.get("author_name") and len(repo_values.get("author_name")) > 0:
                    repo_dict[repo] = repo_values["author_name"]

    bots_dict = {
        "common": common,
        "community": community_dict,
        "repo": repo_dict
    }
    return bots_dict

def is_bot_by_author_name(bots_dict, repo, author_name_list):
    """ Determine if a contributor is a bot by author name """
    for author_name in author_name_list:
        common_list = bots_dict["common"]
        if len(common_list) > 0:
            for common in common_list:
                pattern = f"^{common.replace('*', '.*')}$"
                regex = re.compile(pattern)
                if regex.match(author_name):
                    return True
        community_dict = bots_dict["community"]
        if len(community_dict) > 0:
            for community, community_values in community_dict.items():
                if community in repo and author_name in community_values:
                    return True
        repo_dict = bots_dict["repo"]
        if len(repo_dict) > 0:
            if repo_dict.get(repo) and author_name in repo_dict.get(repo):
                return True
    return False

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
    def __init__(self, json_file, identities_config_file, organizations_config_file, bots_config_file, issue_index,
                 pr_index, issue_comments_index, pr_comments_index, git_index, contributors_index, contributors_enriched_index, 
                 from_date, end_date, repo_index, event_index=None, company=None, stargazer_index=None, fork_index=None):
        """ Build a contributor profile of the repository, including issues, pr, commit, organization, etc.
        :param json_file: the path of json file containing repository message.
        :param identities_config_file: the path of json file containing contributor identity message.
        :param organizations_config_file: the path of json file containing contributor organization message.
        :param bots_config_file: the path of json file containing contributor is not a robot message
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
        self.organizations_dict = get_organizations_info(organizations_config_file)
        self.identities_dict = get_identities_info(identities_config_file)
        self.bots_dict = get_bots_info(bots_config_file)
        self.company = None if company or company == 'None' else company
        self.event_index = event_index
        self.stargazer_index = stargazer_index
        self.fork_index = fork_index
        self.client = None
        self.all_repo = get_all_repo(json_file, 'gitee' if 'gitee' in issue_index else 'github')

        self.platform_item_id_dict = {}
        self.platform_item_identity_dict = {}
        self.git_item_id_dict = {}
        self.git_item_identity_dict = {}
        self.date_field_list = []

    def run(self, elastic_url):
        """Run tasks"""
        self.client = get_elasticsearch_client(elastic_url)
        exist = self.client.indices.exists(index=self.contributors_index)
        if not exist:
            self.client.indices.create(index=self.contributors_index, body=self.get_contributor_index_mapping())
        for repo in self.all_repo:
            self.processing_data(repo)
            time.sleep(5)  #Ensure that data has been saved to ES
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
            # fork and star
            "fork": {"index": self.fork_index, "date_field": "fork_date_list"},
            "star": {"index": self.stargazer_index, "date_field": "star_date_list"},
            # issue and issue comment
            "issue": {"index": self.issue_index, "date_field": "issue_creation_date_list"},
            "issue_comments": {"index": self.issue_comments_index, "date_field": "issue_comments_date_list"},
            # issue event
            "issue_LabeledEvent": {"index": self.event_index, "date_field": "issue_label_date_list"},
            "issue_ClosedEvent": {"index": self.event_index, "date_field": "issue_close_date_list"},
            "issue_ReopenedEvent": {"index": self.event_index, "date_field": "issue_reopen_date_list"},
            "issue_AssignedEvent": {"index": self.event_index, "date_field": "issue_assign_date_list"},
            "issue_MilestonedEvent": {"index": self.event_index, "date_field": "issue_milestone_date_list"},
            "issue_MarkedAsDuplicateEvent": {"index": self.event_index, "date_field": "issue_mark_as_duplicate_date_list"},
            "issue_TransferredEvent": {"index": self.event_index, "date_field": "issue_transfer_date_list"},
            "issue_LockedEvent": {"index": self.event_index, "date_field": "issue_lock_date_list"},
            # pr and pr comment
            "pr": {"index": self.pr_index, "date_field": "pr_creation_date_list"},
            "pr_comments": {"index": self.pr_comments_index, "date_field": "pr_comments_date_list"},
            # pr event
            "pr_LabeledEvent": {"index": self.event_index, "date_field": "pr_label_date_list"},
            "pr_ClosedEvent": {"index": self.event_index, "date_field": "pr_close_date_list"},
            "pr_AssignedEvent": {"index": self.event_index, "date_field": "pr_assign_date_list"},
            "pr_ReopenedEvent": {"index": self.event_index, "date_field": "pr_reopen_date_list"},
            "pr_MilestonedEvent": {"index": self.event_index, "date_field": "pr_milestone_date_list"},
            "pr_MarkedAsDuplicateEvent": {"index": self.event_index, "date_field": "pr_mark_as_duplicate_date_list"},
            "pr_TransferredEvent": {"index": self.event_index, "date_field": "pr_transfer_date_list"},
            "pr_LockedEvent": {"index": self.event_index, "date_field": "pr_lock_date_list"},
            "pr_MergedEvent": {"index": self.event_index, "date_field": "pr_merge_date_list"},
            "pr_PullRequestReview": {"index": self.event_index, "date_field": "pr_review_date_list"},
        }
        if self.git_index is not None:
            self.date_field_list.append("code_commit_date_list")
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
        self.delete_contributor(repo)
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

            org_change_date_list = list(item.get("org_change_date_list", []))
            if len(org_change_date_list) > 0:
                sorted(org_change_date_list, key=lambda x: x["first_date"])
            is_bot = self.is_bot_by_author_name(repo, list(item.get("id_git_author_name_list", []))
                                                + list(item.get("id_platform_login_name_list", []))
                                                + list(item.get("id_platform_author_name_list", [])))
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
                helpers.bulk(client=self.client, actions=all_bulk_data, request_timeout=100)
                all_bulk_data = []
        helpers.bulk(client=self.client, actions=all_bulk_data, request_timeout=100)
        logger.info(repo + " finish count:" + str(len(all_items_dict)) + " " + str(datetime.now() - start_time))

    def processing_platform_data(self, index, repo, from_date, to_date, date_field, type="issue"):
        """ Start processing data, generate gitee or github contributor profiles """
        logger.info(f"{repo} {index}  {type} processing...")
        search_after = []
        count = 0
        start_time = datetime.now()
        while True:
            results = []
            if type == "issue":
                results = self.get_issue_enrich_data(index, repo, from_date, to_date, page_size, search_after)
            elif type == "pr":
                results = self.get_pr_enrich_data(index, repo, from_date, to_date, page_size, search_after)
            elif type == "issue_comments":
                results = self.get_issue_comment_enrich_data(index, repo, from_date, to_date, page_size, search_after)
            elif type == "pr_comments":
                results = self.get_pr_comment_enrich_data(index, repo, from_date, to_date, page_size, search_after)
            elif type in ["fork", "star", "watch"]:
                results = self.get_observe_enrich_data(index, repo, from_date, to_date, page_size, search_after)
            elif type in ["issue_LabeledEvent", "issue_ClosedEvent", "issue_ReopenedEvent", "issue_AssignedEvent",
                          "issue_MilestonedEvent", "issue_MarkedAsDuplicateEvent", "issue_TransferredEvent",
                          "issue_LockedEvent"]:
                results = self.get_issue_event_enrich_data(index, repo, from_date, to_date, page_size, search_after, type.replace("issue_", ""))
            elif type in ["pr_LabeledEvent", "pr_ClosedEvent", "pr_ReopenedEvent", "pr_AssignedEvent",
                          "pr_MilestonedEvent", "pr_MarkedAsDuplicateEvent", "pr_TransferredEvent",
                          "pr_LockedEvent", "pr_MergedEvent", "pr_PullRequestReview"]:
                results = self.get_pr_event_enrich_data(index, repo, from_date, to_date, page_size, search_after, type.replace("pr_", ""))

            count = count + len(results)
            if len(results) == 0:
                break
            search_after = results[len(results) - 1]["sort"]
            for result in results:
                source = result["_source"]
                grimoire_creation_date = datetime_to_utc(
                    str_to_datetime(source["grimoire_creation_date"]).replace(tzinfo=None) + timedelta(microseconds=int(source["uuid"], 16) % 100000)).isoformat()
                user_login = source.get("user_login")
                if user_login is None:
                    continue
                id_identity_list = [
                    user_login,
                    source.get("user_email")
                ]
                id_identity_list = set(
                    [exclude_special_str(x.lower()) for x in id_identity_list if x and x.lower() not in exclude_field_list and exclude_special_str(x) ])
                org_change_date_list = []
                if source.get("user_email") is not None:
                    domain = get_email_prefix_domain(source.get("user_email"))[1]
                    if domain is not None:
                        org_name = self.get_org_name_by_email(source.get("user_email"))
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
        logger.info(repo + " " + index + " finish count:" + str(count) + " " + str(datetime.now() - start_time))

    def processing_commit_data(self, index, repo, from_date, to_date):
        """ Start processing data, generate commit contributor profiles """
        logger.info(repo + " " + index + " processing...")
        created_at = self.get_repo_created(repo)
        search_after = []
        count = 0
        start_time = datetime.now()
        while True:
            results = self.get_commit_enrich_data(index, repo, from_date, to_date, page_size, search_after)
            count = count + len(results)
            if len(results) == 0:
                break
            search_after = results[len(results) - 1]["sort"]
            hash_list = [result["_source"]["hash"] for result in results]
            pr_hits = self.get_pr_list_by_commit_hash(repo, hash_list)
            pr_data_dict = {}
            for pr_hit in pr_hits:
                pr_data_dict[pr_hit["_source"]["merge_commit_sha"]] = pr_hit["_source"]
                for pr_commit_hash in pr_hit["_source"]["commits_data"]:
                    pr_data_dict[pr_commit_hash] = pr_hit["_source"]
            for result in results:
                source = result["_source"]
                if source.get("author_name") is None:
                    continue
                grimoire_creation_date = datetime_to_utc(
                    str_to_datetime(source["grimoire_creation_date"]).replace(tzinfo=None) + timedelta(microseconds=int(source["uuid"], 16) % 100000)).isoformat()
                id_identity_list = [
                    source.get("author_name"),
                    source.get("author_email", None)
                ]
                id_identity_list = set(
                    [exclude_special_str(x.lower()) for x in id_identity_list if x and x.lower() not in exclude_field_list and exclude_special_str(x) ])
                org_change_date_list = []
                if source.get("author_email") is not None:
                    domain = get_email_prefix_domain(source.get("author_email"))[1]
                    if domain is not None:
                        org_name = self.get_org_name_by_email(source.get("author_email"))
                        org_date = {
                            "domain": domain,
                            "org_name": org_name,
                            "first_date": grimoire_creation_date,
                            "last_date": grimoire_creation_date
                        }
                        org_change_date_list.append(org_date)
                code_direct_commit_date = None
                if grimoire_creation_date >= created_at and source["hash"] not in pr_data_dict \
                        and ((source["committer_name"] in "GitHub" and source["committer_email"] in "noreply@github.com")
                             or (source["committer_name"] == source["author_name"] and source["committer_email"] == source["author_email"])):
                    code_direct_commit_date = grimoire_creation_date

                item = {
                    "uuid": get_uuid(repo, "git", source["author_name"], source.get("author_email"), grimoire_creation_date),
                    "id_git_author_name_list": set([source.get("author_name")] if source.get("author_name") else []),
                    "id_git_author_email_list": set([source.get("author_email")] if source.get("author_email") else []),
                    "id_identity_list": id_identity_list,
                    "code_commit_date_list": {grimoire_creation_date},
                    "code_direct_commit_date_list": {code_direct_commit_date} if code_direct_commit_date else set(),
                    "last_contributor_date": grimoire_creation_date,
                    "org_change_date_list": org_change_date_list
                }

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
        logger.info(repo + " " + index + " finish count:" + str(count) + " " + str(datetime.now() - start_time))

    def get_merge_org_change_date(self, old_data_list, new_data_list):
        """ Consolidation of information on the same organization """
        result_data_list = []
        old_data_dict = {}
        for old_data in old_data_list:
            old_key = old_data["domain"]+":"+(old_data["org_name"] if old_data["org_name"] else "")
            old_data_dict[old_key] = old_data
        for new_data in new_data_list:
            new_key = new_data["domain"]+":"+(new_data["org_name"] if new_data["org_name"] else "")
            if new_key in old_data_dict.keys():
                old_data = old_data_dict.pop(new_key)
                data_dict = {
                    "domain": new_data["domain"],
                    "org_name": new_data["org_name"],
                    "first_date": get_oldest_date(new_data["first_date"], old_data["first_date"]),
                    "last_date": get_latest_date(new_data["last_date"], old_data["last_date"])
                }
                result_data_list.append(data_dict)
                continue
            result_data_list.append(new_data)
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
        search_after = []
        login_author_name_dict = {}
        while True:
            query_dsl = self.get_enrich_dsl("tag", repo + ".git", self.from_date, self.end_date, page_size, search_after)
            query_dsl["query"]["bool"]["filter"].append({"range": {"grimoire_creation_date": {"gte": created_at}}})
            results = self.client.search(index=self.git_index, body=query_dsl)["hits"]["hits"]
            if len(results) == 0:
                break
            search_after = results[len(results) - 1]["sort"]
            hash_git_dict = {result["_source"]["hash"]:result for result in results}
            hash_set = set(hash_git_dict.keys())
            pr_hits = self.get_pr_list_by_commit_hash(repo, list(hash_set))
            pr_data_dict = {}
            for pr_hit in pr_hits:
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
                    if len(set(pr_data["commits_data"]) & hash_set) > 0 or len(data["parents"]) > 1:
                        # merge
                        pr_commit_author_name = {hash_git_dict.get(pr_commit_hash)["_source"]["author_name"] for pr_commit_hash in pr_data["commits_data"] if hash_git_dict.get(pr_commit_hash)}
                        if len(pr_commit_author_name) > 1:
                            continue
                        if pr_data["merge_commit_sha"] is not None and data["hash"] in pr_data["merge_commit_sha"] and data["committer_name"] in "GitHub" and data["committer_email"] in "noreply@github.com":
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

    def get_enrich_dsl(self, repo_field, repo, from_date, to_date, page_size=100, search_after=[]):
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
            },
            "sort": [
                {
                    "grimoire_creation_date": {
                        "order": "asc"
                    }
                },
                {
                    "_id": {
                        "order": "asc"
                    }
                }
            ]
        }
        if len(search_after) > 0:
            query['search_after'] = search_after
        return query

    def get_issue_enrich_data(self, index, repo, from_date, to_date, page_size=100, search_after=[]):
        """ Get issue data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size, search_after)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
        results = self.client.search(index=index, body=query_dsl)["hits"]["hits"]
        return results

    def get_pr_enrich_data(self, index, repo, from_date, to_date, page_size=100, search_after=[]):
        """ Get pr data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size, search_after)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
        results = self.client.search(index=index, body=query_dsl)["hits"]["hits"]
        return results

    def get_issue_comment_enrich_data(self, index, repo, from_date, to_date, page_size=100, search_after=[]):
        """ Get issue comment data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size, search_after)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"issue_pull_request": "false"}})
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"item_type": "comment"}})
        results = self.client.search(index=index, body=query_dsl)["hits"]["hits"]
        return results

    def get_pr_comment_enrich_data(self, index, repo, from_date, to_date, page_size=100, search_after=[]):
        """ Get pr comment data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size, search_after)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"item_type": "comment"}})
        results = self.client.search(index=index, body=query_dsl)["hits"]["hits"]
        return results

    def get_observe_enrich_data(self, index, repo, from_date, to_date, page_size=100, search_after=[]):
        """ Get fork or star data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size, search_after)
        results = self.client.search(index=index, body=query_dsl)["hits"]["hits"]
        return results

    def get_issue_event_enrich_data(self, index, repo, from_date, to_date, page_size=100, search_after=[], type="LabeledEvent"):
        """ Get issue event data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size, search_after)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false"}})
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"event_type": type}})
        if type in ["ClosedEvent", "ReopenedEvent"]:
            query_dsl["query"]["bool"]["must"].append({
                "script": {
                    "script": "doc['actor_username'].size() > 0 && doc['reporter_user_name'].size() > 0 &&  doc['actor_username'].value != doc['reporter_user_name'].value"
                }
            })
        results = self.client.search(index=index, body=query_dsl)["hits"]["hits"]
        return results

    def get_pr_event_enrich_data(self, index, repo, from_date, to_date, page_size=100, search_after=[], type="LabeledEvent"):
        """ Get pr event data list """
        query_dsl = self.get_enrich_dsl("tag", repo, from_date, to_date, page_size, search_after)
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
        query_dsl["query"]["bool"]["must"].append({"match_phrase": {"event_type": type}})
        if type in ["ClosedEvent", "ReopenedEvent"]:
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
        results = self.client.search(index=index, body=query_dsl)["hits"]["hits"]
        return results

    def get_commit_enrich_data(self, index, repo, from_date, to_date, page_size=100, search_after=[]):
        """ Get commit data list """
        query_dsl = self.get_enrich_dsl("tag", repo + ".git", from_date, to_date, page_size, search_after)
        results = self.client.search(index=index, body=query_dsl)["hits"]["hits"]
        return results

    def get_contributor_index_mapping(self):
        """ Get Elasticsearch mapping. """
        mapping = {
            "mappings": {
                "properties": {
                    "uuid": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    }
                }
            }
        }
        return mapping

    def get_org_name_by_email(self, email):
        """ Return organization name based on email """
        domain = get_email_prefix_domain(email)[1]
        if domain is None:
            return None
        org_name = self.identities_dict[email] if self.identities_dict.get(email) else self.organizations_dict.get(domain)
        if "facebook.com" in domain:
            org_name = "Facebook"
        if ("noreply.gitee.com" in domain or "noreply.github.com" in domain) and self.company is not None:
            org_name = self.company
        return org_name

    def is_bot_by_author_name(self, repo, author_name_list):
        """ Determine if a bot is a bot by author name """
        for author_name in author_name_list:
            common_list = self.bots_dict["common"]
            if len(common_list) > 0:
                for common in common_list:
                    pattern = f"^{common.replace('*', '.*')}$"
                    regex = re.compile(pattern)
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
        return created_at.replace("Z", "")

    def delete_contributor(self, repo):
        query = {
            "query": { 
                "match_phrase": {
                    "repo_name.keyword": repo
                }
            }
        }
        self.client.delete_by_query(index=self.contributors_index, body=query)

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
            self.client.indices.create(index=self.contributors_enriched_index, body=self.get_contributor_index_mapping())
        date_list = get_date_list(self.from_date, self.end_date)
        count = 0
        item_datas = []
        for date in date_list:
            created_since_metric = created_since(self.client, self.git_index, date, [repo])
            if created_since_metric is None:
                continue
            from_date = date - timedelta(days=7)
            contributor_list = contributor_detail_list(self.client, self.contributors_index, from_date, date, [repo])["contributor_detail_list"]
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
                    helpers.bulk(client=self.client, actions=item_datas)
                    item_datas = []
        helpers.bulk(client=self.client, actions=item_datas)
        logger.info(repo + " contributor enrich data save finish count:" + str(count) + " " + str(datetime.now() - start_time))