import json
import logging
import hashlib
import pendulum
import urllib3
import pkg_resources
import yaml

from compass_common.opensearch_utils import get_client, get_helpers as helpers
from compass_common.datetime import (get_date_list,                                    
                                     datetime_utcnow,
                                     get_last_three_years_dates)
from compass_common.uuid_utils import get_uuid
from compass_common.algorithm_utils import get_score_by_criticality_score, normalize
from compass_metrics.db_dsl import get_release_index_mapping, get_repo_message_query
from compass_metrics.git_metrics import (created_since,
                                         updated_since,
                                         commit_frequency,
                                         org_count,
                                         is_maintained,
                                         commit_pr_linked_ratio,
                                         commit_count,
                                         commit_pr_linked_count,
                                         lines_of_code_frequency,
                                         lines_add_of_code_frequency,
                                         lines_remove_of_code_frequency,
                                         org_commit_frequency,
                                         org_contribution_last,
                                         commit_count_year,
                                         lines_of_code_frequency_year,
                                         LOC_frequency_year
                                         )
from compass_metrics.repo_metrics import recent_releases_count
from compass_metrics.contributor_metrics import (contributor_count,
                                                 code_contributor_count, 
                                                 commit_contributor_count,
                                                 pr_authors_contributor_count,
                                                 pr_review_contributor_count,
                                                 issue_authors_contributor_count,
                                                 issue_comments_contributor_count,
                                                 org_contributor_count,
                                                 bus_factor,
                                                 activity_casual_contributor_count,
                                                 activity_regular_contributor_count,
                                                 activity_core_contributor_count,
                                                 activity_organization_contributor_count,
                                                 activity_individual_contributor_count,
                                                 activity_observation_contributor_count,
                                                 activity_code_contributor_count,
                                                 activity_issue_contributor_count,
                                                 activity_casual_contribution_per_person,
                                                 activity_regular_contribution_per_person,
                                                 activity_core_contribution_per_person,
                                                 activity_organization_contribution_per_person,
                                                 activity_individual_contribution_per_person,
                                                 activity_observation_contribution_per_person,
                                                 activity_code_contribution_per_person,
                                                 activity_issue_contribution_per_person,
                                                 types_of_contributions,
                                                 contributor_count_year,
                                                 org_contributor_count_year
                                                 )
from compass_metrics.issue_metrics import (comment_frequency,
                                           closed_issues_count,
                                           updated_issues_count,
                                           issue_first_reponse,
                                           bug_issue_open_time,
                                           time_to_close,
                                           issue_count_year,
                                           issue_completion_ratio_year,
                                           comment_frequency_year)
from compass_metrics.pr_metrics import (code_review_count,
                                        pr_open_time,
                                        close_pr_count,
                                        code_review_ratio,
                                        pr_count,
                                        pr_count_with_review,
                                        code_merge_ratio,
                                        pr_issue_linked_ratio,
                                        pr_time_to_first_response,
                                        change_request_closure_ratio,
                                        change_request_closure_ratio_recently_period,
                                        total_create_close_pr_count,
                                        total_pr_count,
                                        create_close_pr_count,
                                        code_merge_count_with_non_author,
                                        code_merge_count,
                                        pr_issue_linked_count,
                                        pr_count_year,
                                        close_pr_ratio_year,
                                        code_review_count_year
                                        )
from typing import Dict, Any


from compass_metrics.code_readability import evaluate_code_readability
from compass_metrics.document_metric import Industry_Support
from compass_metrics.security_metric import VulnerabilityMetrics


logger = logging.getLogger(__name__)
urllib3.disable_warnings()

MAX_BULK_UPDATE_SIZE = 500

SOFTWARE_ARTIFACT = "software-artifact"
GOVERNANCE = "governance"

DECAY_COEFFICIENT = 0.0027
INCREMENT_DECAY_METRICS = ["issue_first_reponse_avg",
                           "issue_first_reponse_mid",
                           "bug_issue_open_time_avg",
                           "bug_issue_open_time_mid",
                           "pr_open_time_avg",
                           "pr_open_time_mid",
                           "pr_time_to_first_response_avg",
                           "pr_time_to_first_response_mid",
                           "time_to_close_avg",
                           "time_to_close_mid"]
DECREASE_DECAY_METRICS = ["comment_frequency",
                          "code_review_count",
                          "code_merge_ratio",
                          "code_review_ratio",
                          "pr_issue_linked_ratio",
                          "commit_pr_linked_ratio"]
NEGATICE_METRICS=["updated_since",
                  "issue_first_reponse",
                  "bug_issue_open_time",
                  "pr_open_time",
                  "pr_time_to_first_response",
                  "time_to_close"]


def get_dict_hash(dictionary: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def get_repo_list(json_file, source):
    """ Get list of repositories """
    all_repo = []
    all_repo_json = json.load(open(json_file))
    for project in all_repo_json:
        origin_software_artifact = source + "-" + SOFTWARE_ARTIFACT
        origin_governance = source + "-" + GOVERNANCE
        for key in all_repo_json[project].keys():
            if key == origin_software_artifact or key == origin_governance or key == source:
                for repo in all_repo_json[project].get(key):
                    all_repo.append(repo)
    return all_repo


def get_community_repo_list(json_file, source):
    """ Get community repositories, distinguish between software artifact and governance repositories. """
    software_artifact_repo = []
    governance_repo = []
    all_repo_json = json.load(open(json_file))
    for project in all_repo_json:
        origin_software_artifact = source + "-" + SOFTWARE_ARTIFACT
        origin_governance = source + "-" + GOVERNANCE
        for key in all_repo_json[project].keys():
            if key == origin_software_artifact:
                for j in all_repo_json[project].get(key):
                    software_artifact_repo.append(j)
            if key == origin_governance:
                for j in all_repo_json[project].get(key):
                    governance_repo.append(j)
    software_artifact_repo = list(set(software_artifact_repo))
    governance_repo = list(set(governance_repo))
    return software_artifact_repo, governance_repo


def add_release_message(es_client, all_repo, repo_index, release_index):
    """ Save repository release information to the database """
    es_exist = es_client.indices.exists(index=release_index)
    if not es_exist:
        es_client.indices.create(index=release_index, body=get_release_index_mapping())
    for repo_url in all_repo:
        query = get_repo_message_query(repo_url)
        query_hits = es_client.search(index=repo_index, body=query)["hits"]["hits"]
        if len(query_hits) > 0 and query_hits[0]["_source"].get("releases"):
            releases = query_hits[0]["_source"]["releases"]
            item_datas = []
            for item in releases:
                release_data = {
                    "_index": release_index,
                    "_id": get_uuid(str(item["id"])),
                    "_source": {
                        "uuid": get_uuid(str(item["id"])),
                        "id": item["id"],
                        "tag": repo_url,
                        "tag_name": item["tag_name"],
                        "target_commitish": item["target_commitish"],
                        "prerelease": item["prerelease"],
                        "name": item["name"],
                        "author_login": item["author"]["login"],
                        "author_name": item["author"]["name"],
                        "grimoire_creation_date": item["created_at"],
                        'metadata__enriched_on': datetime_utcnow().isoformat()
                    }
                }
                item_datas.append(release_data)
                if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                    helpers().bulk(client=es_client, actions=item_datas)
                    item_datas = []
            helpers().bulk(client=es_client, actions=item_datas)


def cache_last_metrics_data(item, last_metrics_data):
    """ Cache last non None metrics, used for decay function """
    cache_metrics = INCREMENT_DECAY_METRICS + DECREASE_DECAY_METRICS
    for metrics in cache_metrics:
        if metrics in item and item[metrics]:
            data = [item[metrics], item['grimoire_creation_date']]
            last_metrics_data[metrics] = data



def increment_decay(last_data, threshold, days):
    """ Decay function with gradually increasing values"""
    return min(last_data + DECAY_COEFFICIENT * threshold * days, threshold)


def decrease_decay(last_data, threshold, days):
    """ Decay function with decreasing values  """
    return max(last_data - DECAY_COEFFICIENT * threshold * days, 0)


class BaseMetricsModel:
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, model_name, metrics_weights_thresholds, algorithm="criticality_score", custom_fields=None,
                 contributors_enriched_index=None):
        """ Metrics Model is designed for the integration of multiple CHAOSS metrics.
        :param repo_index: repo index
        :param git_index: git index
        :param issue_index: Issue index
        :param pr_index: pr index
        :param issue_comments_index: issue comment index
        :param pr_comments_index: pr comment index
        :param contributors_index: contributor index
        :param release_index: release index
        :param out_index: target index for Metrics Model.
        :param from_date: the beginning of time for metric model
        :param end_date: the end of time for metric model,
        :param level: str representation of the metrics, choose from repo, project, community.
        :param community: used to mark the repo belongs to which community.
        :param source: Is the repo data source gitee or github
        :param json_file: the path of json file containing repository message.
        :param model_name: the model name
        :param metrics_weights_thresholds: dict representation of metrics, the dict values include weights and thresholds.
        :param algorithm: The algorithm chosen by the model,include criticality_score.
        :param custom_fields: custom_fields
        :param contributors_enriched_index: contributor enrich index
        """
        self.repo_index = repo_index
        self.git_index = git_index
        self.issue_index = issue_index
        self.pr_index = pr_index
        self.issue_comments_index = issue_comments_index
        self.pr_comments_index = pr_comments_index
        self.contributors_index = contributors_index
        self.contributors_enriched_index = contributors_enriched_index
        self.release_index = release_index
        self.out_index = out_index
        self.from_date = from_date
        self.end_date = end_date
        self.level = level
        self.community = community
        self.source = source
        self.json_file = json_file
        self.model_name = model_name
        self.algorithm = algorithm
        self.client = None

        if type(metrics_weights_thresholds) == dict:
            default_metrics_thresholds = self.get_default_metrics_thresholds()
            for metrics, weights_thresholds in metrics_weights_thresholds.items():
                if weights_thresholds["threshold"] is None:
                    weights_thresholds["threshold"] = default_metrics_thresholds[metrics]
                weights_thresholds["weight"] = abs(weights_thresholds["weight"])
                if metrics in NEGATICE_METRICS:
                    weights_thresholds["weight"] = -weights_thresholds["weight"]
            self.metrics_weights_thresholds = metrics_weights_thresholds
            self.metrics_weights_thresholds_hash = get_dict_hash(metrics_weights_thresholds)
        else:
            raise Exception("Invalid metrics param.")

        if type(custom_fields) == dict:
            self.custom_fields = custom_fields
            self.custom_fields_hash = get_dict_hash(custom_fields)
        else:
            self.custom_fields = {}
            self.custom_fields_hash = None
    

    def get_default_metrics_thresholds(self):
        """ Get default thresholds for metrics """
        thresholds_resouces = pkg_resources.resource_string('compass_metrics', 'resources/thresholds.yaml')
        thresholds_data = yaml.load(thresholds_resouces, Loader=yaml.FullLoader)["metrics_default_threshold"]
        metrics_thresholds_data = {}
        for thresholds_list in thresholds_data.values():
            for thresholds in thresholds_list:
                if self.level == "repo":
                    metrics_thresholds_data[thresholds["metric"]] = thresholds["repo_threshold"]
                elif self.level == "community":
                    metrics_thresholds_data[thresholds["metric"]] = thresholds["multiple_threshold"]
        return metrics_thresholds_data


    def metrics_model_metrics(self, elastic_url):
        """ Execute model calculation tasks """
        self.client = get_client(elastic_url)
        if self.level == "repo":
            repo_list = get_repo_list(self.json_file, self.source)
            if len(repo_list) > 0:
                for repo in repo_list:
                     metric_field = next(iter(self.metrics_weights_thresholds.keys()), None)
                     if metric_field:
                         if '_year' in metric_field:
                             self.metrics_model_enrich_year([repo], repo, self.level)
                         else:
                             self.metrics_model_enrich([repo], repo, self.level)
        if self.level == "community":
            software_artifact_repo_list, governance_repo_list = get_community_repo_list(self.json_file, self.source)
            metric_field = next(iter(self.metrics_weights_thresholds.keys()), None)
            if metric_field:
                if '_year' in metric_field:
                    combined_repo_list = software_artifact_repo_list + governance_repo_list
                    if len(combined_repo_list) > 0:
                        self.metrics_model_enrich_year(software_artifact_repo_list, self.community, self.level,
                                                  SOFTWARE_ARTIFACT)
                else:
                    if len(software_artifact_repo_list) > 0:
                        self.metrics_model_enrich(software_artifact_repo_list, self.community, self.level,
                                                  SOFTWARE_ARTIFACT)
                    if len(governance_repo_list) > 0:
                        self.metrics_model_enrich(governance_repo_list, self.community, self.level, GOVERNANCE)

    def metrics_model_enrich(self, repo_list, label, level, type=None):
        """Calculate the metrics model data of the repo list, and output the metrics model data once a week on Monday"""
        last_metrics_data = {}
        add_release_message(self.client, repo_list, self.repo_index, self.release_index)
        date_list = get_date_list(self.from_date, self.end_date)
        item_datas = []
        for date in date_list:
            logger.info(f"{str(date)}--{self.model_name}--{label}")
            created_since_metric = created_since(self.client, self.git_index, date, repo_list)["created_since"]
            if created_since_metric is None:
                continue
            metrics = self.get_metrics(date, repo_list)
            metrics_uuid = get_uuid(str(date), self.community, level, label, self.model_name, type,
                                    self.custom_fields_hash)
            metrics_data = {
                'uuid': metrics_uuid,
                'level': level,
                'type': type,
                'label': label,
                'model_name': self.model_name,
                **metrics,
                'grimoire_creation_date': date.isoformat(),
                'metadata__enriched_on': datetime_utcnow().isoformat(),
                **self.custom_fields
            }
            cache_last_metrics_data(metrics_data, last_metrics_data)
            metrics_data["score"] = self.get_metrics_score(self.metrics_decay(metrics_data, last_metrics_data))
            item_data = {
                "_index": self.out_index,
                "_id": metrics_uuid,
                "_source": metrics_data
            }
            item_datas.append(item_data)
            if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                helpers().bulk(client=self.client, actions=item_datas)
                item_datas = []
        helpers().bulk(client=self.client, actions=item_datas)

    def metrics_model_enrich_year(self, repo_list, label, level, type=None):
        """ Calculate the metrics model data of the repo list, and output the metrics model data once a year """
        last_metrics_data = {}
        add_release_message(self.client, repo_list, self.repo_index, self.release_index)
        date_list = get_last_three_years_dates()
        item_datas = []
        for date in date_list:
            logger.info(f"{str(date)}--{self.model_name}--{label}")
            created_since_metric = created_since(self.client, self.git_index, date, repo_list)["created_since"]
            if created_since_metric is None:
                continue
            metrics = self.get_metrics(date, repo_list)
            metrics_uuid = get_uuid(str(date), self.community, level, label, self.model_name, type,
                                    self.custom_fields_hash,"year")
            metrics_data = {
                'uuid': metrics_uuid,
                'level': level,
                'type': type,
                'label': label,
                'model_name': self.model_name,
                **metrics,
                'grimoire_creation_date': date.isoformat(),
                'metadata__enriched_on': datetime_utcnow().isoformat(),
                **self.custom_fields
            }
            cache_last_metrics_data(metrics_data, last_metrics_data)
            metrics_data["score"] = self.get_metrics_score(self.metrics_decay(metrics_data, last_metrics_data))
            item_data = {
                "_index": self.out_index,
                "_id": metrics_uuid,
                "_source": metrics_data
            }
            item_datas.append(item_data)
            print(len(item_datas))
            if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                helpers().bulk(client=self.client, actions=item_datas)
                item_datas = []
        helpers().bulk(client=self.client, actions=item_datas)

    def get_metrics(self, date, repo_list):
        """ Get the corresponding metrics data according to the metrics field """
        metrics_switch = {
            # git metadata
            "commit_frequency": lambda: commit_frequency(self.client, self.contributors_index, date, repo_list),
            "created_since": lambda: created_since(self.client, self.git_index, date, repo_list),
            "updated_since": lambda: updated_since(self.client, self.git_index, self.contributors_index, date, repo_list, self.level),
            "org_count": lambda: org_count(self.client, self.contributors_index, date, repo_list),
            "lines_of_code_frequency": lambda: lines_of_code_frequency(self.client, self.git_index, date, repo_list),
            "lines_add_of_code_frequency": lambda: lines_add_of_code_frequency(self.client, self.git_index, date, repo_list),
            "lines_remove_of_code_frequency": lambda: lines_remove_of_code_frequency(self.client, self.git_index, date, repo_list),
            "is_maintained": lambda: is_maintained(self.client, self.git_index, self.contributors_index, date, repo_list, self.level),
            "commit_pr_linked_ratio": lambda: commit_pr_linked_ratio(self.client, self.contributors_index, self.git_index, self.pr_index, date, repo_list),
            "commit_count": lambda: commit_count(self.client, self.contributors_index, date, repo_list),
            "commit_pr_linked_count": lambda: commit_pr_linked_count(self.client, self.git_index, self.pr_index, date, repo_list),
            "org_commit_frequency": lambda: org_commit_frequency(self.client, self.contributors_index, date, repo_list),
            "org_contribution_last": lambda: org_contribution_last(self.client, self.contributors_index, date, repo_list),
            "commit_count_year": lambda: commit_count_year(self.client, self.contributors_index, date, repo_list),
            "lines_of_code_frequency_year": lambda: lines_of_code_frequency_year(self.client, self.git_index, date, repo_list),
            # issue
            "issue_first_reponse": lambda: issue_first_reponse(self.client, self.issue_index, date, repo_list),
            "bug_issue_open_time": lambda: bug_issue_open_time(self.client, self.issue_index, date, repo_list),
            "comment_frequency": lambda: comment_frequency(self.client, self.issue_index, date, repo_list),
            "closed_issues_count": lambda: closed_issues_count(self.client, self.issue_index, date, repo_list),
            "updated_issues_count": lambda: updated_issues_count(self.client, self.issue_comments_index, date, repo_list),
            "time_to_close": lambda: time_to_close(self.client, self.issue_index, date, repo_list),
            "issue_count_year": lambda: issue_count_year(self.client, self.issue_index, date, repo_list),
            "issue_completion_ratio_year": lambda: issue_completion_ratio_year(self.client, self.issue_index, date, repo_list),
            "comment_frequency_year": lambda: comment_frequency_year(self.client, self.issue_index, date, repo_list),
            # pr
            "pr_open_time": lambda: pr_open_time(self.client, self.pr_index, date, repo_list),
            "close_pr_count": lambda: close_pr_count(self.client, self.pr_index, date, repo_list),
            "code_review_count": lambda: code_review_count(self.client, self.pr_index, date, repo_list),
            "code_review_ratio": lambda: code_review_ratio(self.client, self.pr_index, date, repo_list),
            "pr_count": lambda: pr_count(self.client, self.pr_index, date, repo_list),
            "pr_count_with_review": lambda: pr_count_with_review(self.client, self.pr_index, date, repo_list),
            "code_merge_ratio": lambda: code_merge_ratio(self.client, self.pr_index, date, repo_list),
            "pr_issue_linked_ratio": lambda: pr_issue_linked_ratio(self.client, self.pr_index, self.pr_comments_index, date, repo_list),
            "pr_time_to_first_response": lambda: pr_time_to_first_response(self.client, self.pr_index, date, repo_list),
            "change_request_closure_ratio": lambda: change_request_closure_ratio(self.client, self.pr_index, date, repo_list),
            "change_request_closure_ratio_recently_period": lambda: change_request_closure_ratio_recently_period(self.client, self.pr_index, date, repo_list),
            "total_create_close_pr_count": lambda: total_create_close_pr_count(self.client, self.pr_index, date, repo_list),
            "total_pr_count": lambda: total_pr_count(self.client, self.pr_index, date, repo_list),
            "create_close_pr_count": lambda: create_close_pr_count(self.client, self.pr_index, date, repo_list),
            "code_merge_count_with_non_author": lambda: code_merge_count_with_non_author(self.client, self.pr_index, date, repo_list),
            "code_merge_count": lambda: code_merge_count(self.client, self.pr_index, date, repo_list),
            "pr_issue_linked_count": lambda: pr_issue_linked_count(self.client, self.pr_index, self.pr_comments_index, date, repo_list),
            "pr_count_year": lambda: pr_count_year(self.client, self.pr_index, date, repo_list),
            "close_pr_ratio_year": lambda: close_pr_ratio_year(self.client, self.pr_index, date, repo_list),
            "code_review_count_year": lambda: code_review_count_year(self.client, self.pr_index, date, repo_list),

            # repo
            "recent_releases_count": lambda: recent_releases_count(self.client, self.release_index, date, repo_list),
            # contributor
            "contributor_count": lambda: contributor_count(self.client, self.contributors_index, date, repo_list),
            "code_contributor_count": lambda: code_contributor_count(self.client, self.contributors_index, date, repo_list),
            "commit_contributor_count": lambda: commit_contributor_count(self.client, self.contributors_index, date, repo_list),
            "pr_authors_contributor_count": lambda: pr_authors_contributor_count(self.client, self.contributors_index, date, repo_list),
            "pr_review_contributor_count": lambda: pr_review_contributor_count(self.client, self.contributors_index, date, repo_list),
            "issue_authors_contributor_count": lambda: issue_authors_contributor_count(self.client, self.contributors_index, date, repo_list),
            "issue_comments_contributor_count": lambda: issue_comments_contributor_count(self.client, self.contributors_index, date, repo_list),
            "org_contributor_count": lambda: org_contributor_count(self.client, self.contributors_index, date, repo_list),
            "bus_factor": lambda: bus_factor(self.client, self.contributors_index, date, repo_list),
            "activity_casual_contributor_count": lambda: activity_casual_contributor_count(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_regular_contributor_count": lambda: activity_regular_contributor_count(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_core_contributor_count": lambda: activity_core_contributor_count(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_organization_contributor_count": lambda: activity_organization_contributor_count(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_individual_contributor_count": lambda: activity_individual_contributor_count(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_observation_contributor_count": lambda: activity_observation_contributor_count(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_code_contributor_count": lambda: activity_code_contributor_count(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_issue_contributor_count": lambda: activity_issue_contributor_count(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_casual_contribution_per_person": lambda: activity_casual_contribution_per_person(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_regular_contribution_per_person": lambda: activity_regular_contribution_per_person(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_core_contribution_per_person": lambda: activity_core_contribution_per_person(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_organization_contribution_per_person": lambda: activity_organization_contribution_per_person(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_individual_contribution_per_person": lambda: activity_individual_contribution_per_person(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_observation_contribution_per_person": lambda: activity_observation_contribution_per_person(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_code_contribution_per_person": lambda: activity_code_contribution_per_person(self.client, self.contributors_enriched_index, date, repo_list),
            "activity_issue_contribution_per_person": lambda: activity_issue_contribution_per_person(self.client, self.contributors_enriched_index, date, repo_list),
            "types_of_contributions": lambda: types_of_contributions(self.client, self.contributors_enriched_index, date, repo_list),
            "contributor_count_year": lambda: contributor_count_year(self.client, self.contributors_index, date, repo_list),
            "org_contributor_count_year": lambda: org_contributor_count_year(self.client, self.contributors_index, date, repo_list),


            # code_readability
            "code_readability": lambda: evaluate_code_readability(repo_list),

            # industry_support
            "doc_quarty": lambda: Industry_Support(self.client,repo_list).get_doc_quarty(),
            "doc_number": lambda: Industry_Support(self.client,repo_list).get_doc_number(),
            "zh_files_number": lambda: Industry_Support(self.client,repo_list).get_zh_files_number(),
            "org_contribution": lambda: Industry_Support(self.client,repo_list).get_org_contribution(),
            
            # security2
            "vul_dectect_time": lambda: VulnerabilityMetrics(repo_list).get_vul_detect_time(),
            "vulnerablity_feedback_channels": lambda: VulnerabilityMetrics(repo_list).get_vulnerablity_feedback_channels(),
            "vul_levels": lambda: VulnerabilityMetrics(repo_list).get_vul_levels(),

            # activity
            "activity_quarterly_contribution": lambda: activity_quarterly_contribution(self.client, self.contributors_index, repo_list, date),
            # license
            "license_conflicts_exist": lambda: license_conflicts_exist(self.client, self.contributors_index, date, repo_list),
            "license_dep_conflicts_exist": lambda: license_dep_conflicts_exist(self.client, self.contributors_index, date, repo_list),
            "license_is_weak": lambda: license_is_weak(self.client, self.contributors_index, date, repo_list),
            "license_change_claims_required": lambda: license_change_claims_required(self.client, self.contributors_index, date, repo_list),
            "license_commercial_allowed": lambda: license_commercial_allowed(self.client, self.contributors_index, date, repo_list),
            # security
            "security_vul_stat": lambda: security_vul_stat(self.client, self.contributors_index, date, repo_list),
            "security_vul_fixed": lambda: security_vul_fixed(self.client, self.contributors_index, date, repo_list),
            "security_scanned": lambda: security_scanned(self.client, self.contributors_index, date, repo_list),

        }

        
        
        metrics = {}
        for metric_field in self.metrics_weights_thresholds.keys():
            if metric_field in metrics_switch:
                metrics.update(metrics_switch[metric_field]())
            else:
                raise Exception("Invalid metric")
        return metrics     

    def get_metrics_score(self, metrics_data):
        """ get model scores based on metric values """
        new_metrics_weights_thresholds = {}
        for metrics, weights_thresholds in self.metrics_weights_thresholds.items():
            if metrics in ["issue_first_reponse", "bug_issue_open_time", "pr_open_time", "pr_time_to_first_response"]:
                new_weights_thresholds = weights_thresholds.copy()
                new_weights_thresholds["weight"] = weights_thresholds["weight"] * 0.5
                new_metrics_weights_thresholds[metrics + "_avg"] = new_weights_thresholds
                new_metrics_weights_thresholds[metrics + "_mid"] = new_weights_thresholds
            else:
                new_metrics_weights_thresholds[metrics] = weights_thresholds
        if self.algorithm == "criticality_score":
            score = get_score_by_criticality_score(metrics_data, new_metrics_weights_thresholds)
            min_metrics_data = {key: None for key in new_metrics_weights_thresholds.keys()}
            min_score = round(get_score_by_criticality_score(min_metrics_data, new_metrics_weights_thresholds), 5)
            return normalize(score, min_score, 1 - min_score)
        else:
            raise Exception("Invalid algorithm param.")

    def metrics_decay(self, metrics_data, last_data):
        """ When there is no issue or pr, the issue or pr related metrics deteriorate over time. """
        if last_data is None:
            return metrics_data

        new_metrics_weights_thresholds = {}
        for metrics, weights_thresholds in self.metrics_weights_thresholds.items():
            if metrics in ["issue_first_reponse", "bug_issue_open_time", "pr_open_time", "pr_time_to_first_response"]:
                new_weights_thresholds = weights_thresholds.copy()
                new_weights_thresholds["weight"] = weights_thresholds["weight"] * 0.5
                new_metrics_weights_thresholds[metrics + "_avg"] = new_weights_thresholds
                new_metrics_weights_thresholds[metrics + "_mid"] = new_weights_thresholds
            else:
                new_metrics_weights_thresholds[metrics] = weights_thresholds

        decay_metrics_data = metrics_data.copy()
        increment_decay_dict = {}
        decrease_decay_dict = {}
        for metrics, weights_thresholds in new_metrics_weights_thresholds.items():
            threshold = weights_thresholds["threshold"]
            if metrics in INCREMENT_DECAY_METRICS:
                increment_decay_dict[metrics] = threshold
            if metrics in DECREASE_DECAY_METRICS:
                decrease_decay_dict[metrics] = threshold

        for key, value in increment_decay_dict.items():
            if metrics_data[key] is None and last_data.get(key) is not None:
                days = pendulum.parse(metrics_data['grimoire_creation_date']).diff(
                    pendulum.parse(last_data[key][1])).days
                decay_metrics_data[key] = round(increment_decay(last_data[key][0], value, days), 4)
        for key, value in decrease_decay_dict.items():
            if metrics_data[key] is None and last_data.get(key) is not None:
                days = pendulum.parse(metrics_data['grimoire_creation_date']).diff(
                    pendulum.parse(last_data[key][1])).days
                decay_metrics_data[key] = round(decrease_decay(last_data[key][0], value, days), 4)
        return decay_metrics_data