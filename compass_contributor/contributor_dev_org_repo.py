from perceval.backend import uuid
import json
import yaml
import re
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse
import urllib3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import helpers
from grimoirelab_toolkit.datetime import (datetime_utcnow,
                                          str_to_datetime,
                                          datetime_to_utc)

logger = logging.getLogger(__name__)
urllib3.disable_warnings()
page_size = 1000

exclude_field_list = ["unknown", "-- undefined --"]


def str_is_not_empty(str):
    return False if str == None or len(str) == 0 else True

def exclude_special_str(str):
    regEx = "[`~!@#$%^&*()+=|{}':;',\\[\\].<>/?~！@#￥%……&*（）——+|{}【】‘；：”“’\"\"。 ，、？_-]"
    return re.sub(regEx, "",str)


def get_uuid(*args):
    args_list = []
    for arg in args:
        if arg is None or arg == '':
            continue
        args_list.append(arg)
    return uuid(*args_list)

def get_elasticsearch_client(elastic_url):
    is_https = urlparse(elastic_url).scheme == 'https'
    client = Elasticsearch(
        elastic_url, use_ssl=is_https, verify_certs=False, connection_class=RequestsHttpConnection)
    return client


def get_organizations_info(file_path):
    organizations_dict = {}
    organizations_config = json.load(open(file_path))
    for org_name in organizations_config["organizations"].keys():
        for domain in organizations_config["organizations"][org_name]:
            organizations_dict[domain["domain"]] = org_name
    return organizations_dict


def get_identities_info(file_path):
    identities_dict = {}
    identities_config = yaml.safe_load(open(file_path))
    for identities in identities_config:
        for email in identities["email"]:
            enrollments = identities.get("enrollments")
            if enrollments is not None:
                identities_dict[email] = enrollments[0]["organization"]
    return identities_dict


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


def list_of_groups(list_info, per_list_len):
    list_of_group = zip(*(iter(list_info),) * per_list_len)
    end_list = [list(i) for i in list_of_group]
    count = len(list_info) % per_list_len
    end_list.append(list_info[-count:]) if count != 0 else end_list
    return end_list


def get_email_prefix_domain(email):
    email_prefix = None
    domain = None
    try:
        email_prefix = email.split("@")[0]
        domain = email.split("@")[1]
    except (IndexError, AttributeError):
        return email_prefix, domain
    return email_prefix, domain


def get_oldest_date(date1, date2):
    return date2 if date1 >= date2 else date1


def get_latest_date(date1, date2):
    return date1 if date1 >= date2 else date2


class ContributorDevOrgRepo:
    def __init__(self, json_file, identities_config_file, organizations_config_file, issue_index, pr_index,
                 issue_comments_index, pr_comments_index, git_index, contributors_index, from_date, end_date, C0_index=None, company=None):
        self.issue_index = issue_index
        self.pr_index = pr_index
        self.issue_comments_index = issue_comments_index
        self.pr_comments_index = pr_comments_index
        self.git_index = git_index
        self.C0_index = C0_index
        self.contributors_index = contributors_index
        self.from_date = from_date
        self.end_date = end_date
        self.organizations_dict = get_organizations_info(organizations_config_file)
        self.identities_dict = get_identities_info(identities_config_file)
        self.company = None if company == None or company == 'None' else company
        self.client = None
        self.all_repo = get_all_repo(json_file, 'gitee' if 'gitee' in issue_index else 'github')
        self.platform_item_id_dict = {}
        self.platform_item_identity_dict = {}
        self.git_item_id_dict = {}
        self.git_item_identity_dict = {}

    def run(self, elastic_url):
        self.client = get_elasticsearch_client(elastic_url)
        exist = self.client.indices.exists(index=self.contributors_index)
        if not exist:
            self.client.indices.create(index=self.contributors_index, body=self.get_contributor_index_mapping())
        for repo in self.all_repo:
            self.processing_data(repo)

    def processing_data(self, repo):
        logger.info(repo + " start")
        start_time = datetime.now()
        self.platform_item_id_dict = {}
        self.platform_item_identity_dict = {}
        self.git_item_id_dict = {}
        self.git_item_identity_dict = {}

        issue_pr_index_dict = {
            self.issue_index: "issue_creation_date_list",
            self.pr_index: "pr_creation_date_list",
            self.issue_comments_index: "issue_comments_date_list"
            # self.pr_comments_index: "pr_review_date_list"
        }
        fork_star_dict = {
            "fork": "fork_date_list",
            "star": "star_date_list"
        }
        for issue_pr_index in issue_pr_index_dict.keys():
           self.processing_platform_data(issue_pr_index, repo, self.from_date, self.end_date, issue_pr_index_dict[issue_pr_index])
        # for fork_star in fork_star_dict.keys():
            # self.processing_platform_data(self.C0_index, repo, self.from_date, self.end_date, fork_star_dict[fork_star], fork_star)
        self.processing_commit_data(self.git_index, repo, self.from_date, self.end_date)
        if len(self.platform_item_id_dict) == 0 and len(self.git_item_id_dict) == 0:
            logger.info(repo + " finish count:" + str(0) + " " + str(datetime.now() - start_time))
            return
        
        new_items_dict = self.get_merge_platform_git_contributor_data(self.git_item_id_dict, self.platform_item_id_dict)
        old_items_dict = self.query_contributors_org_dict(self.contributors_index, repo)
        all_items_dict, merge_item_id_set = self.get_merge_old_new_contributor_data(old_items_dict, new_items_dict)
        logger.info(repo + "  save data...")
        if len(merge_item_id_set) > 0:
            merge_item_id_list = list_of_groups(list(merge_item_id_set), 100)
            for merge_id in merge_item_id_list:
                query = self.get_contributors_dsl(repo, "uuid", merge_id)
                self.client.delete_by_query(index=self.contributors_index, body=query)
        all_bulk_data = []
        community =repo.split("/")[-2]
        platform_type = repo.split("/")[-3].split(".")[0]
        for item in all_items_dict.values():
            issue_creation_date_list = list(item.get("issue_creation_date_list", []))
            pr_creation_date_list = list(item.get("pr_creation_date_list", []))
            issue_comments_date_list = list(item.get("issue_comments_date_list", []))
            pr_review_date_list = list(item.get("pr_review_date_list", []))
            code_commit_date_list = list(item.get("code_commit_date_list", []))
            fork_date_list = list(item.get("fork_date_list", []))
            star_date_list = list(item.get("star_date_list", []))
            org_change_date_list = list(item.get("org_change_date_list", []))

            issue_creation_date_list.sort()
            pr_creation_date_list.sort()
            issue_comments_date_list.sort()
            pr_review_date_list.sort()
            code_commit_date_list.sort()
            fork_date_list.sort()
            star_date_list.sort()
            if len(org_change_date_list) > 0:
                sorted(org_change_date_list, key=lambda x: x["first_date"])

            contributor_data = {
                "_index": self.contributors_index,
                "_id": item.get("uuid"),
                "_source": {
                    "uuid": item.get("uuid"),
                    "id_git_author_name_list": list(item.get("id_git_author_name_list", [])),
                    "id_git_author_email_list": list(item.get("id_git_author_email_list", [])),
                    "id_platform_login_name_list": list(item.get("id_platform_login_name_list", [])),
                    "id_platform_author_name_list": list(item.get("id_platform_author_name_list", [])),
                    "id_platform_author_email_list": list(item.get("id_platform_author_email_list", [])),
                    "id_identity_list": list(item.get("id_identity_list", [])),
                    "first_issue_creation_date": issue_creation_date_list[0] if len(issue_creation_date_list) > 0 else None,
                    "first_pr_creation_date": pr_creation_date_list[0] if len(pr_creation_date_list) > 0 else None,
                    "first_issue_comments_date": issue_comments_date_list[0] if len(issue_comments_date_list) > 0 else None,
                    "first_pr_review_date": pr_review_date_list[0] if len(pr_review_date_list) > 0 else None,
                    "first_code_commit_date": code_commit_date_list[0] if len(code_commit_date_list) > 0 else None,
                    "first_fork_date": fork_date_list[0] if len(fork_date_list) > 0 else None,
                    "first_star_date": star_date_list[0] if len(star_date_list) > 0 else None,
                    "issue_creation_date_list": issue_creation_date_list,
                    "pr_creation_date_list": pr_creation_date_list,
                    "issue_comments_date_list": issue_comments_date_list,
                    "pr_review_date_list": pr_review_date_list,
                    "code_commit_date_list": code_commit_date_list,
                    "fork_date_list": fork_date_list,
                    "star_date_list": star_date_list,
                    "last_contributor_date": item["last_contributor_date"],
                    "org_change_date_list": org_change_date_list,
                    "platform_type": platform_type,
                    "domain": org_change_date_list[len(org_change_date_list)-1]["domain"] if len(org_change_date_list) > 0 else None,
                    "org_name": org_change_date_list[len(org_change_date_list)-1]["org_name"] if len(org_change_date_list) > 0 else None,
                    "community": community,
                    "repo_name": repo,
                    "update_at_date": datetime_utcnow().isoformat()        
                }
            }
            all_bulk_data.append(contributor_data)
            if len(all_bulk_data) > 100:
                helpers.bulk(client=self.client, actions=all_bulk_data)
                all_bulk_data = []
        helpers.bulk(client=self.client, actions=all_bulk_data)
        logger.info(repo + " finish count:" + str(len(all_items_dict)) + " " + str(datetime.now() - start_time))

    def processing_platform_data(self, index, repo, from_date, to_date, date_field, fork_star=None):
        logger.info(repo + " " + index + " processing...")
        search_after = []
        count = 0
        start_time = datetime.now()
        while True:
            results = self.get_enrich_data(index, repo, from_date, to_date, fork_star, page_size, search_after)
            count = count + len(results)
            if len(results) == 0:
                break
            for result in results:
                search_after = result["sort"]
                source = result["_source"]
                grimoire_creation_date = datetime_to_utc(
                    str_to_datetime(source["grimoire_creation_date"]).replace(tzinfo=None) + timedelta(microseconds=int(source["uuid"], 16) % 100000)).isoformat()
                id_identity_list = [
                    source.get("user_login"),
                    source.get("author_name"),
                    get_email_prefix_domain(source.get("user_email"))[0] if source.get("user_email") else None
                ]
                id_identity_list = set(
                    [exclude_special_str(x.lower()) for x in id_identity_list if str_is_not_empty(x) and x not in exclude_field_list and str_is_not_empty(exclude_special_str(x)) ])
                org_change_date_list = []
                if source.get("user_email") is not None:
                    domain = get_email_prefix_domain(source.get("user_email"))[1]
                    if domain is not None:
                        org_name = self.identities_dict[source.get("user_email")] if self.identities_dict.get(source.get("user_email")) else self.organizations_dict.get(domain)    
                        if domain in "facebook.com":
                            org_name = "Facebook"
                        if domain in ["noreply.github.com","noreply.github.com"] and self.company is not None:
                            org_name = self.company
                        org_date = {
                            "domain": domain,
                            "org_name": org_name,
                            "first_date": grimoire_creation_date,
                            "last_date": grimoire_creation_date
                        }
                        org_change_date_list.append(org_date)

                item = {
                    "uuid": get_uuid(repo, "platform", source["user_login"], source.get("author_name"), source.get("user_email"), grimoire_creation_date),
                    "id_platform_login_name_list": set([source.get("user_login")] if source.get("user_login") else []),
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
        logger.info(repo + " " + index + " processing...")
        search_after = []
        count = 0
        start_time = datetime.now()
        while True:
            results = self.get_enrich_data(index, repo + ".git", from_date, to_date, page_size=page_size, search_after=search_after)
            count = count + len(results)
            if len(results) == 0:
                break
            for result in results:
                search_after = result["sort"]
                source = result["_source"]
                if source.get("author_name") is None:
                    continue
                grimoire_creation_date = datetime_to_utc(
                    str_to_datetime(source["grimoire_creation_date"]).replace(tzinfo=None) + timedelta(microseconds=int(source["uuid"], 16) % 100000)).isoformat()
                id_identity_list = [
                    source.get("author_name"),
                    get_email_prefix_domain(source.get("author_email"))[0] if source.get("author_email") else None
                ]
                id_identity_list = set(
                    [exclude_special_str(x.lower()) for x in id_identity_list if str_is_not_empty(x) and x not in exclude_field_list and str_is_not_empty(exclude_special_str(x)) ])
                org_change_date_list = []
                if source.get("author_email") is not None:
                    domain = get_email_prefix_domain(source.get("author_email"))[1]
                    if domain is not None:
                        org_name = self.identities_dict[source.get("author_email")] if self.identities_dict.get(source.get("author_email")) else self.organizations_dict.get(domain)
                        if domain in "facebook.com":
                            org_name = "Facebook"
                        if domain in ["noreply.github.com","noreply.github.com"] and self.company is not None:
                            org_name = self.company
                        org_date = {
                            "domain": domain,
                            "org_name": org_name,
                            "first_date": grimoire_creation_date,
                            "last_date": grimoire_creation_date
                        }
                        org_change_date_list.append(org_date)

                item = {
                    "uuid": get_uuid(repo, "git", source["author_name"], source.get("author_email"), grimoire_creation_date),
                    "id_git_author_name_list": set([source.get("author_name")] if source.get("author_name") else []),
                    "id_git_author_email_list": set([source.get("author_email")] if source.get("author_email") else []),
                    "id_identity_list": id_identity_list,
                    "code_commit_date_list": {grimoire_creation_date},
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

    def get_merge_platform_git_contributor_data(self, git_data_dict, platform_data_dict):
        result_item_dict, merge_id_set = self.get_merge_old_new_contributor_data(git_data_dict, platform_data_dict)
        for commit_data in git_data_dict.values():
            if commit_data["uuid"] in merge_id_set:
                continue
            result_item_dict[commit_data["uuid"]] = commit_data
        return result_item_dict

    def get_merge_old_new_contributor_data(self, old_data_dict, new_data_dict):
        result_item_dict = {}
        identity_dict = {}
        for item in old_data_dict.values():
            for identity in item["id_identity_list"]:
                identity_dict[identity] = item
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
                        if identity in result_identity_uuid_dict.keys():
                            old_data = result_item_dict.pop(result_identity_uuid_dict[identity])
                            break
                else:
                    merge_id_set.add(old_data["uuid"])

                id_platform_login_name_list = item.get("id_platform_login_name_list", set())
                id_platform_author_name_list = item.get("id_platform_author_name_list", set())
                id_platform_author_email_list = item.get("id_platform_author_email_list", set())
                id_git_author_name_list = item.get("id_git_author_name_list", set())
                id_git_author_email_list = item.get("id_git_author_email_list", set())
                identity_list = item.get("id_identity_list", set())
                issue_creation_date_list = item.get("issue_creation_date_list", set())
                pr_creation_date_list = item.get("pr_creation_date_list", set())
                issue_comments_date_list = item.get("issue_comments_date_list", set())
                pr_review_date_list = item.get("pr_review_date_list", set())
                code_commit_date_list = item.get("code_commit_date_list", set())
                fork_date_list = item.get("fork_date_list", set())
                star_date_list = item.get("star_date_list", set())
                org_change_date_list = item.get("org_change_date_list", [])

                id_platform_login_name_list.update(set(old_data["id_platform_login_name_list"] if old_data.get("id_platform_login_name_list") else []))
                id_platform_author_name_list.update(set(old_data["id_platform_author_name_list"] if old_data.get("id_platform_author_name_list") else []))
                id_platform_author_email_list.update(set(old_data["id_platform_author_email_list"] if old_data.get("id_platform_author_email_list") else []))
                id_git_author_name_list.update(set(old_data["id_git_author_name_list"] if old_data.get("id_git_author_name_list") else []))
                id_git_author_email_list.update(set(old_data["id_git_author_email_list"] if old_data.get("id_git_author_email_list") else []))
                identity_list.update(set(old_data["id_identity_list"] if old_data.get("id_identity_list") else []))
                issue_creation_date_list.update(set(old_data["issue_creation_date_list"] if old_data.get("issue_creation_date_list") else []))
                pr_creation_date_list.update(set(old_data["pr_creation_date_list"] if old_data.get("pr_creation_date_list") else []))
                issue_comments_date_list.update(set(old_data["issue_comments_date_list"] if old_data.get("issue_comments_date_list") else []))
                pr_review_date_list.update(set(old_data["pr_review_date_list"] if old_data.get("pr_review_date_list") else []))
                code_commit_date_list.update(set(old_data["code_commit_date_list"] if old_data.get("code_commit_date_list") else []))
                fork_date_list.update(set(old_data["fork_date_list"] if old_data.get("fork_date_list") else []))
                star_date_list.update(set(old_data["star_date_list"] if old_data.get("star_date_list") else []))
                if old_data.get("org_change_date_list") is not None:
                    org_change_date_list = self.get_merge_org_change_date(old_data.get("org_change_date_list"), org_change_date_list)

                item["id_platform_login_name_list"] = id_platform_login_name_list
                item["id_platform_author_name_list"] = id_platform_author_name_list
                item["id_platform_author_email_list"] = id_platform_author_email_list
                item["id_git_author_name_list"] = id_git_author_name_list
                item["id_git_author_email_list"] = id_git_author_email_list
                item["id_identity_list"] = identity_list
                item["issue_creation_date_list"] = issue_creation_date_list
                item["pr_creation_date_list"] = pr_creation_date_list
                item["issue_comments_date_list"] = issue_comments_date_list
                item["pr_review_date_list"] = pr_review_date_list
                item["code_commit_date_list"] = code_commit_date_list
                item["fork_date_list"] = fork_date_list
                item["star_date_list"] = star_date_list
                item["last_contributor_date"] = get_latest_date(item["last_contributor_date"], old_data["last_contributor_date"])
                item["org_change_date_list"] = org_change_date_list

            result_item_dict[item["uuid"]] = item
            for identity_list in item["id_identity_list"]:
                result_identity_uuid_dict[identity_list] = item["uuid"]
        return result_item_dict, merge_id_set

    def get_enrich_data(self, index, repo, from_date, to_date, fork_star_type=None, page_size=100, search_after=[]):
        query = {
            "size": page_size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                "tag": repo
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
        if fork_star_type is not None:
            query["query"]["bool"]["must"].append({"match_phrase": {"type": fork_star_type}})
        if len(search_after) > 0:
            query['search_after'] = search_after
        results = self.client.search(index=index, body=query)["hits"]["hits"]
        return results

    def get_contributor_index_mapping(self):
        mapping = {
            "mappings" : {
                "properties" : {
                "code_commit_date_list" : {
                    "type" : "date"
                },
                "community" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "domain" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "first_code_commit_date" : {
                    "type" : "date"
                },
                "first_issue_comments_date" : {
                    "type" : "date"
                },
                "first_issue_creation_date" : {
                    "type" : "date"
                },
                "first_pr_creation_date" : {
                    "type" : "date"
                },
                "first_pr_review_date" : {
                    "type" : "date"
                },
                "id_git_author_email_list" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "id_git_author_name_list" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "id_identity_list" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "id_platform_author_email_list" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "id_platform_author_name_list" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "id_platform_login_name_list" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "issue_comments_date_list" : {
                    "type" : "date"
                },
                "issue_creation_date_list" : {
                    "type" : "date"
                },
                "last_contributor_date" : {
                    "type" : "date"
                },
                "org_change_date_list" : {
                    "properties" : {
                    "domain" : {
                        "type" : "text",
                        "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                        }
                    },
                    "first_date" : {
                        "type" : "date"
                    },
                    "last_date" : {
                        "type" : "date"
                    },
                    "org_name" : {
                        "type" : "text",
                        "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                        }
                    }
                    }
                },
                "org_name" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "platform_type" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "pr_creation_date_list" : {
                    "type" : "date"
                },
                "pr_review_date_list" : {
                    "type" : "date"
                },
                "repo_name" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                },
                "update_at_date" : {
                    "type" : "date"
                },
                "uuid" : {
                    "type" : "text",
                    "fields" : {
                    "keyword" : {
                        "type" : "keyword",
                        "ignore_above" : 256
                    }
                    }
                }
                }
            }
        }
        return mapping

    def get_contributors_dsl(self, repo, field, field_value_list):
        query = {
            "size": 10000,
            "query": {
                "bool": {
                    "must": [
                        {
                            "terms": {
                                field + ".keyword": field_value_list
                            }
                        },
                        {
                            "match_phrase": {
                                "repo_name.keyword": repo
                            }
                        }
                    ]
                }
            }
        }
        return query

    def query_contributors_org_dict(self, index, repo):
        result_list = []
        all_identity_set = set()
        all_identity_set.update(self.platform_item_identity_dict.keys())
        all_identity_set.update(self.git_item_identity_dict.keys())
        for identity_list in list_of_groups(list(all_identity_set), page_size):
            query = self.get_contributors_dsl(repo, "id_identity_list", identity_list)
            contributors_list = self.client.search(index=index, body=query)["hits"]["hits"]
            if len(contributors_list) > 0:
                result_list = result_list + [contributor["_source"] for contributor in contributors_list]
        return dict(zip([item["uuid"] for item in result_list], result_list))


