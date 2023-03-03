#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Yehui Wang, Chenqi Shan
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Yehui Wang <yehui.wang.mdh@gmail.com>
#     Chenqi Shan <chenqishan337@gmail.com>

from perceval.backend import uuid
from datetime import datetime, timedelta
from urllib.parse import urlparse
import json
import yaml
import pandas as pd
import logging
from grimoire_elk.enriched.utils import get_time_diff_days
from grimoirelab_toolkit.datetime import (datetime_utcnow,
                                          str_to_datetime)
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch import helpers
from elasticsearch.exceptions import NotFoundError
from grimoire_elk.elastic import ElasticSearch

from .utils import (get_uuid,
                    get_date_list,
                    get_activity_score,
                    community_support,
                    code_quality_guarantee,
                    organizations_activity,
                    community_decay,
                    activity_decay,
                    code_quality_decay)

import os
import inspect
import sys
current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
os.chdir(current_dir)
sys.path.append('../')

logger = logging.getLogger(__name__)

MAX_BULK_UPDATE_SIZE = 5000

# [Fixme] In fact, origin should not be distinguished by this form of string.
# Maybe pass parameters through configuration file is better.
def get_all_repo(file, source):
    '''Get all repo from json file'''
    all_repo_json = json.load(open(file))
    all_repo = []
    origin = 'gitee' if 'gitee' in source else 'github'
    for i in all_repo_json:
        for j in all_repo_json[i][origin]:
            all_repo.append(j)
    return all_repo

def newest_message(repo_url):
    query = {
        "query": {
            "match": {
                "tag": repo_url
            }
        },
        "sort": [
            {
                "metadata__updated_on": {"order": "desc"}
            }
        ]
    }
    return query

def check_times_has_overlap(dyna_start_time, dyna_end_time, fixed_start_time, fixed_end_time):
    return not (dyna_end_time < fixed_start_time or dyna_start_time > fixed_end_time)

def get_oldest_date(date1, date2):
    return date2 if date1 >= date2 else date1

def get_latest_date(date1, date2):
    return date1 if date1 >= date2 else date2

def add_release_message(es_client, out_index, repo_url, releases,):
    item_datas = []
    for item in releases:
        release_data = {
            "_index": out_index,
            "_id": uuid(str(item["id"])),
            "_source": {
                "uuid": uuid(str(item["id"])),
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
            helpers.bulk(client=es_client, actions=item_datas)
            item_datas = []
    helpers.bulk(client=es_client, actions=item_datas)


def get_release_index_mapping():
    mapping = {
    "mappings" : {
      "properties" : {
        "author_login" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "author_name" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "body" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "grimoire_creation_date" : {
          "type" : "date"
        },
        "id" : {
          "type" : "long"
        },
        "name" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "prerelease" : {
          "type" : "boolean"
        },
        "tag" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "tag_name" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "target_commitish" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
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


def create_release_index(es_client, all_repo, repo_index, release_index):
    es_exist = es_client.indices.exists(index=release_index)
    if not es_exist:
        res = es_client.indices.create(index=release_index, body=get_release_index_mapping())
    for repo_url in all_repo:
        query = newest_message(repo_url)
        query_hits = es_client.search(index=repo_index, body=query)["hits"]["hits"]
        if len(query_hits) > 0 and query_hits[0]["_source"].get("releases"):
            items = query_hits[0]["_source"]["releases"]
            add_release_message(es_client, release_index, repo_url, items)

def get_all_project(file):
    '''Get all projects from json file'''
    file_json = json.load(open(file))
    all_project = []
    for i in file_json:
        all_project.append(i)
    return all_project


def get_time_diff_months(start, end):
    ''' Number of months between two dates in UTC format  '''

    if start is None or end is None:
        return None

    if type(start) is not datetime:
        start = str_to_datetime(start).replace(tzinfo=None)
    if type(end) is not datetime:
        end = str_to_datetime(end).replace(tzinfo=None)

    seconds_month = float(60 * 60 * 24 * 30)
    diff_months = (end - start).total_seconds() / seconds_month
    diff_months = float('%.2f' % diff_months)

    return diff_months


def get_medium(L):
    L.sort()
    n = len(L)
    m = int(n/2)
    if n == 0:
        return None
    elif n % 2 == 0:
        return (L[m]+L[m-1])/2.0
    else:
        return L[m]


class MetricsModel:
    def __init__(self, json_file, from_date, end_date, out_index=None, community=None, level=None):
        """Metrics Model is designed for the integration of multiple CHAOSS metrics.
        :param json_file: the path of json file containing repository message.
        :param out_index: target index for Metrics Model.
        :param community: used to mark the repo belongs to which community.
        :param level: str representation of the metrics, choose from repo, project, community.
        """
        self.json_file = json_file
        self.out_index = out_index
        self.community = community
        self.level = level
        self.from_date = from_date
        self.end_date = end_date
        self.date_list = get_date_list(from_date, end_date)

    def metrics_model_metrics(self, elastic_url):
        is_https = urlparse(elastic_url).scheme == 'https'
        self.es_in = Elasticsearch(
            elastic_url, use_ssl=is_https, verify_certs=False, connection_class=RequestsHttpConnection)
        self.es_out = ElasticSearch(elastic_url, self.out_index)

        all_repo_json = json.load(open(self.json_file))
        if self.level == "community":
            software_artifact_repos_list = []
            governance_repos_list = []
            for project in all_repo_json:
                origin = 'gitee' if 'gitee' in self.issue_index else 'github'
                origin_software_artifact = origin + "-software-artifact"
                origin_governance = origin + "-governance"
                for key in all_repo_json[project].keys():
                    if key == origin_software_artifact:
                        for j in all_repo_json[project].get(key):
                            software_artifact_repos_list.append(j)
                    if key == origin_governance:
                        for j in all_repo_json[project].get(key):
                            governance_repos_list.append(j)
            all_repo_list = software_artifact_repos_list + governance_repos_list
            if len(all_repo_list) > 0:
                for repo in all_repo_list:
                    last_time = self.last_metrics_model_time(repo, self.model_name, "repo")
                    if last_time is None:
                        self.metrics_model_enrich(repos_list=[repo], label=repo, level="repo",
                                                  date_list=get_date_list(self.from_date, self.end_date))
                    if last_time is not None and last_time < self.end_date:
                        self.metrics_model_enrich(repos_list=[repo], label=repo, level="repo",
                                                  date_list=get_date_list(last_time, self.end_date))
            if len(software_artifact_repos_list) > 0:
                self.metrics_model_enrich(software_artifact_repos_list, self.community, "software-artifact")
            if len(governance_repos_list) > 0:
                self.metrics_model_enrich(governance_repos_list, self.community, "governance")
        if self.level == "project":
            for project in all_repo_json:
                software_artifact_repos_list = []
                governance_repos_list = []
                origin = 'gitee' if 'gitee' in self.issue_index else 'github'
                origin_software_artifact = origin + "-software-artifact"
                origin_governance = origin + "-governance"
                for key in all_repo_json[project].keys():
                    if key == origin_software_artifact:
                        for j in all_repo_json[project].get(key):
                            software_artifact_repos_list.append(j)
                    if key == origin_governance:
                        for j in all_repo_json[project].get(key):
                            governance_repos_list.append(j)
                all_repo_list = software_artifact_repos_list + governance_repos_list
                if len(all_repo_list) > 0:
                    for repo in all_repo_list:
                        last_time = self.last_metrics_model_time(repo, self.model_name, "repo")
                        if last_time is None:
                            self.metrics_model_enrich(repos_list=[repo], label=repo, level="repo",
                                                      date_list=get_date_list(self.from_date, self.end_date))
                        if last_time is not None and last_time < self.end_date:
                            self.metrics_model_enrich(repos_list=[repo], label=repo, level="repo",
                                                      date_list=get_date_list(last_time, self.end_date))
                if len(software_artifact_repos_list) > 0:
                    self.metrics_model_enrich(software_artifact_repos_list, project, "software-artifact")
                if len(governance_repos_list) > 0:
                    self.metrics_model_enrich(governance_repos_list, project, "governance")
        if self.level == "repo":
            for project in all_repo_json:
                origin = 'gitee' if 'gitee' in self.issue_index else 'github'
                origin_software_artifact = origin + "-software-artifact"
                origin_governance = origin + "-governance"
                for key in all_repo_json[project].keys():
                    if key == origin_software_artifact or key == origin_governance or key == origin:
                        for j in all_repo_json[project].get(key):
                            self.metrics_model_enrich([j], j)

    def metrics_model_enrich(repos_list, label, type=None, level=None, date_list=None):
        pass

    def get_last_metrics_model_query(self, repo_url, model_name, level):
        query = {
                "size": 1,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match_phrase": {
                                    "label": repo_url
                            }
                            },
                            {
                                "term": {
                                    "model_name.keyword": model_name
                            }
                            },
                            {
                                "term": {
                                    "level.keyword":level
                            }
                            }
                        ]
                    }
                },
                "sort": [
                    {
                        "grimoire_creation_date": {
                            "order": "desc",
                            "unmapped_type": "keyword"
                        }
                    }
                ]
        }
        return query

    def last_metrics_model_time(self, repo_url, model_name, level):
        query = self.get_last_metrics_model_query(repo_url, model_name, level)
        try:
            query_hits = self.es_in.search(index=self.out_index, body=query)["hits"]["hits"]
            return query_hits[0]["_source"]["grimoire_creation_date"] if query_hits.__len__() > 0 else None
        except NotFoundError:
            return None

    def created_since(self, date, repos_list):
        created_since_list = []
        for repo in repos_list:
            query_first_commit_since = self.get_updated_since_query(
                [repo], date_field='grimoire_creation_date', to_date=date, order="asc")
            first_commit_since = self.es_in.search(
                index=self.git_index, body=query_first_commit_since)['hits']['hits']
            if len(first_commit_since) > 0:
                creation_since = first_commit_since[0]['_source']["grimoire_creation_date"]
                created_since_list.append(
                    get_time_diff_months(creation_since, str(date)))
                # print(get_time_diff_months(creation_since, str(date)))
                # print(repo)
        if created_since_list:
            return sum(created_since_list)
        else:
            return None

    def get_uuid_count_query(self, option, repos_list, field, date_field="grimoire_creation_date", size=0, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
        query = {
            "size": size,
            "track_total_hits": "true",
            "aggs": {"count_of_uuid":
                     {option:
                      {"field": field}
                      }
                     },
            "query":
            {"bool": {
                "must": [
                    {"bool":
                     {"should":
                      [{"simple_query_string":
                        {"query": i + "*",
                         "fields":
                         ["tag"]}}for i in repos_list],
                         "minimum_should_match": 1,
                         "filter":
                         {"range":
                          {date_field:
                           {"gte": from_date.strftime("%Y-%m-%d"), "lt": to_date.strftime("%Y-%m-%d")}}}
                      }
                     }]}}
        }
        return query

    def get_uuid_count_contribute_query(self, repos_list, company=None, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
        query = {
            "size": 0,
            "aggs": {
                "count_of_contributors": {
                    "cardinality": {
                        "field": "author_name"
                    }
                }
            },
            "query":
            {"bool": {
                "must": [
                    {"bool":
                     {"should":
                      [{"simple_query_string":
                        {"query": i + "*",
                         "fields":
                         ["tag"]}}for i in repos_list],
                         "minimum_should_match": 1,
                         "filter":
                         {"range":
                          {"grimoire_creation_date":
                           {"gte": from_date.strftime("%Y-%m-%d"), "lt": to_date.strftime("%Y-%m-%d")}}}
                      }
                     }]}},
        }

        if company:
            query["query"]["bool"]["must"] = [{"bool": {
                "should": [
                    {
                        "simple_query_string": {
                            "query": company + "*",
                            "fields": [
                                "author_domain"
                            ]
                        }
                    }],
                "minimum_should_match": 1}}]
        return query

    def get_updated_since_query(self, repos_list, date_field="grimoire_creation_date", order="desc", to_date=datetime_utcnow()):
        query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match_phrase": {
                                "tag": repo + ".git"
                            }} for repo in repos_list],
                    "minimum_should_match": 1,
                    "filter": {
                        "range": {
                            date_field: {
                                "lt": to_date.strftime("%Y-%m-%d")
                            }
                        }
                    }
                }
            },
            "sort": [
                {
                    date_field: {"order": order}
                }
            ]
        }
        return query

    def get_issue_closed_uuid_count(self, option, repos_list, field, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
        query = {
            "size": 0,
            "track_total_hits": True,
            "aggs": {
                "count_of_uuid": {
                    option: {
                        "field": field
                    }
                }
            },
            "query": {
                "bool": {
                    "must": [{
                        "bool": {
                            "should": [{
                                "simple_query_string": {
                                    "query": i,
                                    "fields": ["tag"]
                                }}for i in repos_list],
                            "minimum_should_match": 1
                        }
                    }],
                    "must_not": [
                        {"term": {"state": "open"}},
                        {"term": {"state": "progressing"}}
                    ],
                    "filter": {
                        "range": {
                            "closed_at": {
                                "gte": from_date.strftime("%Y-%m-%d"),
                                "lt": to_date.strftime("%Y-%m-%d")
                            }
                        }
                    }
                }
            }
        }

        return query

    def get_pr_closed_uuid_count(self, option, repos_list, field, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
        query = {
            "size": 0,
            "track_total_hits": True,
            "aggs": {
                "count_of_uuid": {
                    option: {
                        "field": field
                    }
                }
            },
            "query": {
                "bool": {
                    "must": [{
                        "bool": {
                            "should": [{
                                "simple_query_string": {
                                    "query": i,
                                    "fields": ["tag"]
                                }}for i in repos_list],
                            "minimum_should_match": 1
                        }
                    },
                        {
                        "match_phrase": {
                            "pull_request": "true"
                        }
                    }
                    ],
                    "must_not": [
                        {"term": {"state": "open"}},
                        {"term": {"state": "progressing"}}
                    ],
                    "filter": {
                        "range": {
                            "closed_at": {
                                "gte": from_date.strftime("%Y-%m-%d"),
                                "lt": to_date.strftime("%Y-%m-%d")
                            }
                        }
                    }
                }
            }
        }

        return query

    def get_recent_releases_uuid_count(self, option, repos_list, field, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
        query = {
            "size": 0,
            "track_total_hits": True,
            "aggs": {
                "count_of_uuid": {
                    option: {
                        "field": field + '.keyword'
                    }
                }
            },
            "query": {
                "bool": {
                    "must": [{
                        "bool": {
                            "should": [{
                                "simple_query_string": {
                                    "query": i,
                                    "fields": ["tag.keyword"]
                                }}for i in repos_list],
                            "minimum_should_match": 1
                        }
                    }
                    ],
                    "filter": {
                        "range": {
                            "grimoire_creation_date": {
                                "gte": from_date.strftime("%Y-%m-%d"),
                                "lt": to_date.strftime("%Y-%m-%d")
                            }
                        }
                    }
                }
            }
        }

        return query

    # name list of author_name in a index
    def get_all_CX_contributors(self, repos_list, search_index, pr=False, issue=False, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
        query_CX_users = {
            "aggs": {
                "name": {
                    "terms": {
                        "field": "author_name",
                        "size": 100000
                    }, "aggs": {
                        "date": {
                            "top_hits": {
                                "sort": [{
                                    "grimoire_creation_date": {"order": "asc"}
                                }],
                                "size": 1
                            }
                        }
                    }
                }
            },
            "query": {
                "bool": {
                    "should": [
                        {
                            "simple_query_string": {
                                "query": i+"(*) OR " + i+"*",
                                "fields": [
                                    "tag"
                                ]
                            }
                        } for i in repos_list
                    ],
                    "minimum_should_match": 1,
                    "filter": {
                        "range": {
                            "grimoire_creation_date": {
                                "gte": from_date.strftime("%Y-%m-%d"), "lte": to_date.strftime("%Y-%m-%d")
                            }
                        }
                    }
                }
            },
            "size": 0,
            "from": 0
        }
        if pr:
            query_CX_users["query"]["bool"]["must"] = {
                "match_phrase": {
                    "pull_request": "true"
                }
            }
        if issue:
            query_CX_users["query"]["bool"]["must"] = {
                "match_phrase": {
                    "pull_request": "false"
                }
            }
        CX_contributors = self.es_in.search(index=search_index, body=query_CX_users)[
            "aggregations"]["name"]["buckets"]
        return [i["date"]["hits"]["hits"][0]["_source"] for i in CX_contributors]

    def get_all_CX_comments_contributors(self, repos_list, search_index, pr=False, issue=False, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
        query_CX_users = {
            "aggs": {
                "name": {
                    "terms": {
                        "field": "author_name",
                        "size": 100000
                    }, "aggs": {
                        "date": {
                            "top_hits": {
                                "sort": [{
                                    "grimoire_creation_date": {"order": "asc"}
                                }],
                                "size": 1
                            }
                        }
                    }
                }
            },
            "query": {
                "bool": {
                    "should": [
                        {
                            "simple_query_string": {
                                "query": i+"(*) OR " + i+"*",
                                "fields": [
                                    "tag"
                                ]
                            }
                        } for i in repos_list
                    ],
                    "minimum_should_match": 1,
                    "filter": {
                        "range": {
                            "grimoire_creation_date": {
                                "gte": from_date.strftime("%Y-%m-%d"), "lte": to_date.strftime("%Y-%m-%d")
                            }
                        }
                    }
                }
            },
            "size": 1,
            "from": 0
        }
        if pr:
            query_CX_users["query"]["bool"]["must"] = [
                {
                    "match_phrase": {
                        "item_type": "comment"
                    }
                }]
            # print(query_CX_users)
        if issue:
            query_CX_users["query"]["bool"]["must"] = [
                {
                    "match_phrase": {
                        "item_type": "comment"
                    }
                }, {
                    "match_phrase": {
                        "issue_pull_request": "false"
                    }
                }]
        CX_contributors = self.es_in.search(index=search_index, body=query_CX_users)[
            "aggregations"]["name"]["buckets"]
        all_contributors = [i["date"]["hits"]["hits"]
                            [0]["_source"] for i in CX_contributors]
        return all_contributors

    def query_commit_contributor_list(self, index, repo, from_date, to_date, page_size=100, search_after=[]):
        query = {
            "size": page_size,
            "query": {
                "bool": {
                "must": [
                    {
                    "match_phrase": {
                        "repo_name.keyword": repo
                    }    
                    }
                ],
                "filter": [
                    {
                    "range": {
                        "code_commit_date_list": {
                            "gte": from_date.strftime("%Y-%m-%d"),
                            "lte": to_date.strftime("%Y-%m-%d")
                        }
                    }
                    }
                ]
                }
            },
            "sort": [
                {
                    "_id": {
                        "order": "asc"
                    }
                }
            ]  
        }
        if len(search_after) > 0:
            query['search_after'] = search_after
        results = self.es_in.search(index=index, body=query)["hits"]["hits"]
        return results
    
    def get_commit_contributor_list(self, date, repos_list):
        result_list = []
        for repo in repos_list:
            search_after = []
            while True:
                contributor_list = self.query_commit_contributor_list(self.contributors_index, repo, date - timedelta(days=90), date, 500, search_after)
                if len(contributor_list) == 0:
                    break
                search_after = contributor_list[len(contributor_list) - 1]["sort"]
                result_list = result_list +[contributor["_source"] for contributor in contributor_list]
        return result_list   

    def org_count(self, date, contributor_list):
        org_name_set = set()
        from_date = (date - timedelta(days=90)).strftime("%Y-%m-%d")
        to_date = date.strftime("%Y-%m-%d")

        for contributor in contributor_list:
            for org in contributor["org_change_date_list"]:
                if  org.get("org_name") is not None and check_times_has_overlap(org["first_date"], org["last_date"], from_date, to_date):
                    org_name_set.add(org.get("org_name"))
        return len(org_name_set)


class ActivityMetricsModel(MetricsModel):
    def __init__(self, issue_index, repo_index=None, pr_index=None, json_file=None, git_index=None, out_index=None, git_branch=None, from_date=None, end_date=None, community=None, level=None, release_index=None, opensearch_config_file=None,issue_comments_index=None, pr_comments_index=None,contributors_index=None):
        super().__init__(json_file, from_date, end_date, out_index, community, level)
        self.issue_index = issue_index
        self.repo_index = repo_index
        self.git_index = git_index
        self.pr_index = pr_index
        self.release_index = release_index
        self.git_branch = git_branch
        self.issue_comments_index = issue_comments_index
        self.pr_comments_index = pr_comments_index
        self.contributors_index = contributors_index
        self.model_name = 'Activity'

    def contributor_count(self, date, repos_list):
        query_author_uuid_data = self.get_uuid_count_contribute_query(
            repos_list, company=None, from_date=(date - timedelta(days=90)), to_date=date)
        author_uuid_count = self.es_in.search(index=(self.git_index, self.issue_index, self.pr_index, self.issue_comments_index,self.pr_comments_index), body=query_author_uuid_data)[
            'aggregations']["count_of_contributors"]['value']
        return author_uuid_count

    def commit_frequency(self, date, repos_list):
        query_commit_frequency = self.get_uuid_count_query(
            "cardinality", repos_list, "hash", "grimoire_creation_date", size=0, from_date=date - timedelta(days=90), to_date=date)
        commit_frequency = self.es_in.search(index=self.git_index, body=query_commit_frequency)[
            'aggregations']["count_of_uuid"]['value']
        return commit_frequency/12.85

    def updated_since(self, date, repos_list):
        updated_since_list = []
        for repo in repos_list:
            query_updated_since = self.get_updated_since_query(
                [repo], date_field='metadata__updated_on', to_date=date)
            updated_since = self.es_in.search(
                index=self.git_index, body=query_updated_since)['hits']['hits']
            if updated_since:
                updated_since_list.append(get_time_diff_months(
                    updated_since[0]['_source']["metadata__updated_on"], str(date)))
        if updated_since_list:
            return sum(updated_since_list) / len(updated_since_list)
        else:
            return 0

    def closed_issue_count(self, date, repos_list):
        query_issue_closed = self.get_issue_closed_uuid_count(
            "cardinality", repos_list, "uuid", from_date=(date-timedelta(days=90)), to_date=date)
        query_issue_closed["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
        issue_closed = self.es_in.search(index=self.issue_index, body=query_issue_closed)[
            'aggregations']["count_of_uuid"]['value']
        return issue_closed

    def updated_issue_count(self, date, repos_list):
        query_issue_updated_since = self.get_uuid_count_query(
            "cardinality", repos_list, "uuid", date_field='metadata__updated_on', size=0, from_date=(date-timedelta(days=90)), to_date=date)
        query_issue_updated_since["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
        updated_issues_count = self.es_in.search(index=self.issue_index, body=query_issue_updated_since)[
            'aggregations']["count_of_uuid"]['value']
        return updated_issues_count

    def comment_frequency(self, date, repos_list):
        query_issue_comments_count = self.get_uuid_count_query(
            "sum", repos_list, "num_of_comments_without_bot", date_field='grimoire_creation_date', size=0, from_date=(date-timedelta(days=90)), to_date=date)
        query_issue_comments_count["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
        issue = self.es_in.search(
            index=self.issue_index, body=query_issue_comments_count)
        try:
            return float(issue['aggregations']["count_of_uuid"]['value']/issue["hits"]["total"]["value"])
        except ZeroDivisionError:
            return None

    def code_review_count(self, date, repos_list):
        query_pr_comments_count = self.get_uuid_count_query(
            "sum", repos_list, "num_review_comments_without_bot", size=0, from_date=(date-timedelta(days=90)), to_date=date)
        query_pr_comments_count["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true" }})
        prs = self.es_in.search(index=self.pr_index,body=query_pr_comments_count)
        try:
            return prs['aggregations']["count_of_uuid"]['value']/prs["hits"]["total"]["value"]
        except ZeroDivisionError:
            return None

    def recent_releases_count(self, date, repos_list):
        try:
            query_recent_releases_count = self.get_recent_releases_uuid_count(
                "cardinality", repos_list, "uuid", from_date=(date-timedelta(days=365)), to_date=date)
            releases_count = self.es_in.search(index=self.release_index, body=query_recent_releases_count)[
                'aggregations']["count_of_uuid"]['value']
            return releases_count
        except NotFoundError:
            return 0

    def active_C1_pr_create_contributor(self, date, repos_list):
        C1_pr_contributors = self.get_all_CX_contributors(
            repos_list, (self.pr_index), pr=True, from_date=date-timedelta(days=90), to_date=date)
        return len(C1_pr_contributors)

    def active_C1_pr_comments_contributor(self, date, repos_list):
        C1_pr_comments_contributors = self.get_all_CX_comments_contributors(repos_list, (self.pr_comments_index), pr=True, from_date=date-timedelta(days=90), to_date=date)
        return len(C1_pr_comments_contributors)

    def active_C1_issue_create_contributor(self, date, repos_list):
        C1_issue_contributors = self.get_all_CX_contributors(
            repos_list, (self.issue_index), issue=True, from_date=date-timedelta(days=90), to_date=date)
        return len(C1_issue_contributors)

    def active_C1_issue_comments_contributor(self, date, repos_list):
        C1_issue_comments_contributors = self.get_all_CX_comments_contributors(repos_list, (self.issue_comments_index), issue=True, from_date=date-timedelta(days=90), to_date=date)
        return len(C1_issue_comments_contributors)

    def active_C2_contributor_count(self, date, repos_list):
        query_author_uuid_data = self.get_uuid_count_contribute_query(
            repos_list, company=None, from_date=(date - timedelta(days=90)), to_date=date)
        author_uuid_count = self.es_in.search(index=(self.git_index), body=query_author_uuid_data)[
            'aggregations']["count_of_contributors"]['value']
        return author_uuid_count

    def metrics_model_enrich(self, repos_list, label, type=None, level=None, date_list=None):
        level = level if level is not None else self.level
        date_list = date_list if date_list is not None else self.date_list
        item_datas = []
        last_metrics_data = {}
        create_release_index(self.es_in, repos_list, self.repo_index, self.release_index)
        for date in date_list:
            logger.info(str(date)+"--"+self.model_name+"--"+label)
            created_since = self.created_since(date, repos_list)
            if created_since is None:
                continue
            comment_frequency = self.comment_frequency(date, repos_list)
            code_review_count = self.code_review_count(date, repos_list)
            commit_frequency_message = self.commit_frequency(date, repos_list)
            contributor_list = self.get_commit_contributor_list(date, repos_list)
            org_count = self.org_count(date, contributor_list)
            metrics_data = {
                'uuid': get_uuid(str(date), self.community, level, label, self.model_name, type),
                'level': level,
                'type': type,
                'label': label,
                'model_name': self.model_name,
                'contributor_count': int(self.contributor_count(date, repos_list)),
                'active_C2_contributor_count': self.active_C2_contributor_count(date, repos_list),
                'active_C1_pr_create_contributor': self.active_C1_pr_create_contributor(date, repos_list),
                'active_C1_pr_comments_contributor': self.active_C1_pr_comments_contributor(date, repos_list),
                'active_C1_issue_create_contributor': self.active_C1_issue_create_contributor(date, repos_list),
                'active_C1_issue_comments_contributor': self.active_C1_issue_comments_contributor(date, repos_list),
                'commit_frequency': commit_frequency_message,
                'org_count': org_count,
                # 'created_since': round(self.created_since(date, repos_list), 4),
                'comment_frequency': float(round(comment_frequency, 4)) if comment_frequency is not None else None,
                'code_review_count': round(code_review_count, 4) if code_review_count is not None else None,
                'updated_since': float(round(self.updated_since(date, repos_list), 4)),
                'closed_issues_count': self.closed_issue_count(date, repos_list),
                'updated_issues_count': self.updated_issue_count(date, repos_list),
                'recent_releases_count': self.recent_releases_count(date, repos_list),
                'grimoire_creation_date': date.isoformat(),
                'metadata__enriched_on': datetime_utcnow().isoformat()
            }
            self.cache_last_metrics_data(metrics_data, last_metrics_data)
            score = get_activity_score(activity_decay(metrics_data, last_metrics_data, level), level)
            metrics_data["activity_score"] = score
            item_datas.append(metrics_data)
            if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                self.es_out.bulk_upload(item_datas, "uuid")
                item_datas = []
        self.es_out.bulk_upload(item_datas, "uuid")

    def cache_last_metrics_data(self, item, last_metrics_data):
        for i in ["comment_frequency",  "code_review_count"]:
            if item[i] != None:
                data = [item[i],item['grimoire_creation_date']]
                last_metrics_data[i] = data


class CommunitySupportMetricsModel(MetricsModel):
    def __init__(self, issue_index=None, pr_index=None, git_index=None,  json_file=None, out_index=None, from_date=None, end_date=None, community=None, level=None):
        super().__init__(json_file, from_date, end_date, out_index, community, level)
        self.issue_index = issue_index
        self.model_name = 'Community Support and Service'
        self.pr_index = pr_index
        self.git_index = git_index

    def issue_first_reponse(self, date, repos_list):
        query_issue_first_reponse_avg = self.get_uuid_count_query(
            "avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0, from_date=date-timedelta(days=90), to_date=date)
        query_issue_first_reponse_avg["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
        issue_first_reponse = self.es_in.search(index=self.issue_index, body=query_issue_first_reponse_avg)
        if issue_first_reponse["hits"]["total"]["value"] == 0:
            return None, None
        issue_first_reponse_avg = issue_first_reponse['aggregations']["count_of_uuid"]['value']
        query_issue_first_reponse_mid = self.get_uuid_count_query(
            "percentiles", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0, from_date=date-timedelta(days=90), to_date=date)
        query_issue_first_reponse_mid["aggs"]["count_of_uuid"]["percentiles"]["percents"] = [
            50]
        query_issue_first_reponse_mid["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
        issue_first_reponse_mid = self.es_in.search(index=self.issue_index, body=query_issue_first_reponse_mid)[
            'aggregations']["count_of_uuid"]['values']['50.0']
        return issue_first_reponse_avg, issue_first_reponse_mid

    def issue_open_time(self, date, repos_list):
        query_issue_opens = self.get_uuid_count_query("avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=10000, from_date=date-timedelta(days=90), to_date=date)
        query_issue_opens["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
        issue_opens_items = self.es_in.search(index=self.issue_index, body=query_issue_opens)['hits']['hits']
        if len(issue_opens_items) == 0:
            return None, None
        issue_open_time_repo = []
        for item in issue_opens_items:
            if 'state' in item['_source']:
                if item['_source']['closed_at']:
                    if item['_source']['state'] in ['closed', 'rejected'] and str_to_datetime(item['_source']['closed_at']) < date:
                        issue_open_time_repo.append(get_time_diff_days(
                            item['_source']['created_at'], item['_source']['closed_at']))
                else:
                    issue_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], str(date)))
        if len(issue_open_time_repo) == 0:
            return None, None
        issue_open_time_repo_avg = sum(issue_open_time_repo)/len(issue_open_time_repo)
        issue_open_time_repo_mid = get_medium(issue_open_time_repo)
        return issue_open_time_repo_avg, issue_open_time_repo_mid

    def bug_issue_open_time(self, date, repos_list):
        query_issue_opens = self.get_uuid_count_query("avg", repos_list, "time_to_first_attention_without_bot",
                                                      "grimoire_creation_date", size=10000, from_date=date-timedelta(days=90), to_date=date)
        query_issue_opens["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
        bug_query = {
            "bool": {
                "should": [{
                    "script": {
                        "script": "if (doc.containsKey('labels') && doc['labels'].size()>0) { for (int i = 0; i < doc['labels'].length; ++i){ if(doc['labels'][i].toLowerCase().indexOf('bug')!=-1|| doc['labels'][i].toLowerCase().indexOf('缺陷')!=-1){return true;}}}"
                    }
                },
                    {
                    "script": {
                        "script": "if (doc.containsKey('issue_type') && doc['issue_type'].size()>0) { for (int i = 0; i < doc['issue_type'].length; ++i){ if(doc['issue_type'][i].toLowerCase().indexOf('bug')!=-1 || doc['issue_type'][i].toLowerCase().indexOf('缺陷')!=-1){return true;}}}"
                    }
                }],
                "minimum_should_match": 1
            }
        }
        query_issue_opens["query"]["bool"]["must"].append(bug_query)
        issue_opens_items = self.es_in.search(
            index=self.issue_index, body=query_issue_opens)['hits']['hits']
        if len(issue_opens_items) == 0:
            return None, None
        issue_open_time_repo = []
        for item in issue_opens_items:
            if 'state' in item['_source']:
                if item['_source']['closed_at'] and item['_source']['state'] in ['closed', 'rejected'] and str_to_datetime(item['_source']['closed_at']) < date:
                        issue_open_time_repo.append(get_time_diff_days(
                            item['_source']['created_at'], item['_source']['closed_at']))
                else:
                    issue_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], str(date)))
        issue_open_time_repo_avg = sum(issue_open_time_repo)/len(issue_open_time_repo)
        issue_open_time_repo_mid = get_medium(issue_open_time_repo)
        return issue_open_time_repo_avg, issue_open_time_repo_mid

    def pr_open_time(self, date, repos_list):
        query_pr_opens = self.get_uuid_count_query("avg", repos_list, "time_to_first_attention_without_bot",
                                                   "grimoire_creation_date", size=10000, from_date=date-timedelta(days=90), to_date=date)
        query_pr_opens["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true" }})
        pr_opens_items = self.es_in.search(
            index=self.pr_index, body=query_pr_opens)['hits']['hits']
        if len(pr_opens_items) == 0:
            return None, None
        pr_open_time_repo = []
        for item in pr_opens_items:
            if 'state' in item['_source']:
                if item['_source']['state'] == 'merged' and item['_source']['merged_at'] and str_to_datetime(item['_source']['merged_at']) < date:
                    pr_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], item['_source']['merged_at']))
                if item['_source']['state'] == 'closed' and str_to_datetime(item['_source']['closed_at'] or item['_source']['updated_at']) < date:
                    pr_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], item['_source']['closed_at'] or item['_source']['updated_at']))
                else:
                    pr_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], str(date)))
        if len(pr_open_time_repo) == 0:
            return None, None
        pr_open_time_repo_avg = float(sum(pr_open_time_repo)/len(pr_open_time_repo))
        pr_open_time_repo_mid = get_medium(pr_open_time_repo)
        return pr_open_time_repo_avg, pr_open_time_repo_mid

    def pr_first_response_time(self, date, repos_list):
        query_pr_first_reponse_avg = self.get_uuid_count_query(
            "avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0, from_date=date-timedelta(days=90), to_date=date)
        query_pr_first_reponse_avg["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true" }})
        pr_first_reponse = self.es_in.search(index=self.pr_index, body=query_pr_first_reponse_avg)
        if pr_first_reponse["hits"]["total"]["value"] == 0:
            return None, None
        pr_first_reponse_avg = pr_first_reponse['aggregations']["count_of_uuid"]['value']
        query_pr_first_reponse_mid = self.get_uuid_count_query(
            "percentiles", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0, from_date=date-timedelta(days=90), to_date=date)
        query_pr_first_reponse_mid["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true" }})
        query_pr_first_reponse_mid["aggs"]["count_of_uuid"]["percentiles"]["percents"] = [
            50]
        pr_first_reponse_mid = self.es_in.search(index=self.pr_index, body=query_pr_first_reponse_mid)[
            'aggregations']["count_of_uuid"]['values']['50.0']
        return pr_first_reponse_avg, pr_first_reponse_mid

    def comment_frequency(self, date, repos_list):
        query_issue_comments_count = self.get_uuid_count_query(
            "sum", repos_list, "num_of_comments_without_bot", date_field='grimoire_creation_date', size=0, from_date=(date-timedelta(days=90)), to_date=date)
        query_issue_comments_count["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
        issue = self.es_in.search(
            index=self.issue_index, body=query_issue_comments_count)
        try:
            return float(issue['aggregations']["count_of_uuid"]['value']/issue["hits"]["total"]["value"])
        except ZeroDivisionError:
            return None

    def updated_issue_count(self, date, repos_list):
        query_issue_updated_since = self.get_uuid_count_query(
            "cardinality", repos_list, "uuid", date_field='metadata__updated_on', size=0, from_date=(date-timedelta(days=90)), to_date=date)
        query_issue_updated_since["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "false" }})
        updated_issues_count = self.es_in.search(index=self.issue_index, body=query_issue_updated_since)[
            'aggregations']["count_of_uuid"]['value']
        return updated_issues_count

    def code_review_count(self, date, repos_list):
        query_pr_comments_count = self.get_uuid_count_query(
            "avg", repos_list, "num_review_comments_without_bot", size=0, from_date=(date-timedelta(days=90)), to_date=date)
        query_pr_comments_count["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true" }})
        prs = self.es_in.search(index=self.pr_index, body=query_pr_comments_count)
        if prs["hits"]["total"]["value"] == 0:
            return  None
        else:
            return prs['aggregations']["count_of_uuid"]['value']

    def closed_pr_count(self, date, repos_list):
        query_pr_closed = self.get_pr_closed_uuid_count(
            "cardinality", repos_list, "uuid", from_date=(date-timedelta(days=90)), to_date=date)
        pr_closed = self.es_in.search(index=self.pr_index, body=query_pr_closed)[
            'aggregations']["count_of_uuid"]['value']
        return pr_closed

    def metrics_model_enrich(self, repos_list, label, type=None, level=None, date_list=None):
        level = level if level != None else self.level
        date_list = date_list if date_list != None else self.date_list
        item_datas = []
        last_metrics_data = {}
        for date in date_list:
            logger.info(str(date)+"--"+self.model_name+"--"+label)
            created_since = self.created_since(date, repos_list)
            if created_since is None:
                continue
            issue_first = self.issue_first_reponse(date, repos_list)
            bug_issue_open_time = self.bug_issue_open_time(date, repos_list)
            issue_open_time = self.issue_open_time(date, repos_list)
            pr_open_time = self.pr_open_time(date, repos_list)
            pr_first_response_time = self.pr_first_response_time(date, repos_list)
            comment_frequency = self.comment_frequency(date, repos_list)
            code_review_count = self.code_review_count(date, repos_list)
            metrics_data = {
                'uuid': get_uuid(str(date), self.community, level, label, self.model_name, type),
                'level': level,
                'type': type,
                'label': label,
                'model_name': self.model_name,
                'issue_first_reponse_avg': round(issue_first[0], 4) if issue_first[0] is not None else None,
                'issue_first_reponse_mid': round(issue_first[1], 4) if issue_first[1] is not None else None,
                'issue_open_time_avg': round(issue_open_time[0], 4) if issue_open_time[0] is not None else None,
                'issue_open_time_mid': round(issue_open_time[1], 4) if issue_open_time[1] is not None else None,
                'bug_issue_open_time_avg': round(bug_issue_open_time[0], 4) if bug_issue_open_time[0] is not None else None,
                'bug_issue_open_time_mid': round(bug_issue_open_time[1], 4) if bug_issue_open_time[1] is not None else None,
                'pr_open_time_avg': round(pr_open_time[0], 4) if pr_open_time[0] is not None else None,
                'pr_open_time_mid': round(pr_open_time[1], 4) if pr_open_time[1] is not None else None,
                'pr_first_response_time_avg': round(pr_first_response_time[0], 4) if pr_first_response_time[0] is not None else None,
                'pr_first_response_time_mid': round(pr_first_response_time[1], 4) if pr_first_response_time[1] is not None else None,
                'comment_frequency': float(round(comment_frequency, 4)) if comment_frequency is not None else None,
                'code_review_count': float(code_review_count) if code_review_count is not None else None,
                'updated_issues_count': self.updated_issue_count(date, repos_list),
                'closed_prs_count': self.closed_pr_count(date, repos_list),
                'grimoire_creation_date': date.isoformat(),
                'metadata__enriched_on': datetime_utcnow().isoformat()
            }
            self.cache_last_metrics_data(metrics_data, last_metrics_data)
            score = community_support(community_decay(metrics_data, last_metrics_data, level), level)
            metrics_data["community_support_score"] = score
            item_datas.append(metrics_data)
            if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                self.es_out.bulk_upload(item_datas, "uuid")
                item_datas = []
        self.es_out.bulk_upload(item_datas, "uuid")

    def cache_last_metrics_data(self, item, last_metrics_data):
        for i in ["issue_first_reponse_avg",  "issue_first_reponse_mid",
                    "bug_issue_open_time_avg", "bug_issue_open_time_mid",
                    "pr_open_time_avg","pr_open_time_mid",
                    "pr_first_response_time_avg", "pr_first_response_time_mid",
                    "comment_frequency", "code_review_count"]:
            if item[i] != None:
                data = [item[i],item['grimoire_creation_date']]
                last_metrics_data[i] = data


class CodeQualityGuaranteeMetricsModel(MetricsModel):
    def __init__(self, issue_index=None, pr_index=None, repo_index=None, json_file=None, git_index=None, out_index=None, git_branch=None, from_date=None, end_date=None, community=None, level=None, company=None, pr_comments_index=None):
        super().__init__(json_file, from_date, end_date, out_index, community, level)
        self.issue_index = issue_index
        self.repo_index = repo_index
        self.git_index = git_index
        self.git_branch = git_branch
        self.model_name = 'Code_Quality_Guarantee'
        self.pr_index = pr_index
        self.company = None if company == None or company == 'None' else company
        self.pr_comments_index = pr_comments_index
        self.commit_message_dict = {}

    def get_pr_message_count(self, repos_list, field, date_field="grimoire_creation_date", size=0, filter_field=None, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
        query = {
            "size": size,
            "track_total_hits": True,
            "aggs": {
                "count_of_uuid": {
                    "cardinality": {
                        "field": field
                    }
                }
            },
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [{
                                    "simple_query_string": {
                                        "query": i,
                                        "fields": ["tag"]
                                    }}for i in repos_list],
                                "minimum_should_match": 1
                            }
                        },
                        {
                            "match_phrase": {
                                "pull_request": "true"
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range":
                            {
                                filter_field: {
                                    "gte": 1
                                }
                            }},
                        {
                            "range":
                            {
                                date_field: {
                                    "gte": from_date.strftime("%Y-%m-%d"),
                                    "lt": to_date.strftime("%Y-%m-%d")
                                }
                            }
                        }
                    ]
                }
            }
        }
        return query



    def get_pr_linked_issue_count(self, repo, from_date=str_to_datetime("1970-01-01"), to_date=datetime_utcnow()):
        query = {
            "size": 0,
            "track_total_hits": True,
            "aggs": {
                "count_of_uuid": {
                    "cardinality": {
                        "script": "if(doc.containsKey('pull_id')) {return doc['pull_id']} else {return doc['id']}"
                    }
                }
            },
            "query": {
                "bool": {
                    "should": [
                        {
                            "range": {
                                "linked_issues_count": {
                                    "gte": 1
                                }
                            }
                        },
                        {
                            "script": {
                                "script": "if (doc.containsKey('body') && doc['body'].size()>0 &&doc['body'].value.indexOf('"+repo+"/issue') != -1){return true}"
                            }
                        }
                    ],
                    "minimum_should_match": 1,
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {
                                        "simple_query_string": {
                                            "query": repo,
                                            "fields": [
                                                "tag"
                                            ]
                                        }
                                    }
                                ],
                                "minimum_should_match": 1
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                "grimoire_creation_date": {
                                    "gte": from_date.strftime("%Y-%m-%d"),
                                    "lt": to_date.strftime("%Y-%m-%d")
                                }
                            }
                        }
                    ]
                }
            }
        }
        return query


    def contributor_count(self, date, repos_list):
        query_author_uuid_data = self.get_uuid_count_contribute_query(
            repos_list, company=None, from_date=(date - timedelta(days=90)), to_date=date)
        author_uuid_count = self.es_in.search(index=(self.git_index, self.pr_comments_index), body=query_author_uuid_data)[
            'aggregations']["count_of_contributors"]['value']
        return author_uuid_count

    def commit_frequency(self, date, repos_list):
        query_commit_frequency = self.get_uuid_count_query(
            "cardinality", repos_list, "hash", "grimoire_creation_date", size=0, from_date=date - timedelta(days=90), to_date=date)
        commit_frequency = self.es_in.search(index=self.git_index, body=query_commit_frequency)[
            'aggregations']["count_of_uuid"]['value']
        query_commit_frequency_commpany = 0
        if self.company:
            query_commit_frequency["query"]["bool"]["must"].append({ "match": { "author_org_name": self.company } })
            query_commit_frequency_commpany = self.es_in.search(index=self.git_index, body=query_commit_frequency)[
                'aggregations']["count_of_uuid"]['value']
        return commit_frequency/12.85, query_commit_frequency_commpany/12.85

    def is_maintained(self, date, repos_list, level):
        is_maintained_list = []
        if level == "repo":
            date_list_maintained = get_date_list(begin_date=str(
                date-timedelta(days=90)), end_date=str(date), freq='7D')
            for day in date_list_maintained:
                query_git_commit_i = self.get_uuid_count_query(
                    "cardinality", repos_list, "hash", size=0, from_date=day-timedelta(days=7), to_date=day)
                commit_frequency_i = self.es_in.search(index=self.git_index, body=query_git_commit_i)[
                    'aggregations']["count_of_uuid"]['value']
                if commit_frequency_i > 0:
                    is_maintained_list.append("True")
                else:
                    is_maintained_list.append("False")

        elif level in ["project", "community"]:
            for repo in repos_list:
                query_git_commit_i = self.get_uuid_count_query("cardinality",[repo+'.git'], "hash",from_date=date-timedelta(days=30), to_date=date)
                commit_frequency_i = self.es_in.search(index=self.git_index, body=query_git_commit_i)['aggregations']["count_of_uuid"]['value']
                if commit_frequency_i > 0:
                    is_maintained_list.append("True")
                else:
                    is_maintained_list.append("False")
        try:
            return is_maintained_list.count("True") / len(is_maintained_list)
        except ZeroDivisionError:
            return 0

    def LOC_frequency(self, date, repos_list, field='lines_changed'):
        query_LOC_frequency = self.get_uuid_count_query(
            'sum', repos_list, field, 'grimoire_creation_date', size=0, from_date=date-timedelta(days=90), to_date=date)
        LOC_frequency = self.es_in.search(index=self.git_index, body=query_LOC_frequency)[
            'aggregations']['count_of_uuid']['value']
        return LOC_frequency/12.85

    def code_review_ratio(self, date, repos_list):
        query_pr_count = self.get_uuid_count_query(
            "cardinality", repos_list, "uuid", size=0, from_date=(date-timedelta(days=90)), to_date=date)
        pr_count = self.es_in.search(index=self.pr_index, body=query_pr_count)[
            'aggregations']["count_of_uuid"]['value']
        query_pr_body = self.get_pr_message_count(repos_list, "uuid", "grimoire_creation_date", size=0,
                                                  filter_field="num_review_comments_without_bot", from_date=(date-timedelta(days=90)), to_date=date)
        prs = self.es_in.search(index=self.pr_index, body=query_pr_body)[
            'aggregations']["count_of_uuid"]['value']
        try:
            return prs/pr_count, pr_count
        except ZeroDivisionError:
            return None, 0


    def git_pr_linked_ratio(self, date, repos_list):
        commit_frequency = self.get_uuid_count_query("cardinality", repos_list, "hash", "grimoire_creation_date", size=10000, from_date=date - timedelta(days=90), to_date=date)
        commits_without_merge_pr = {
            "bool": {
                "should": [{"script": {
                    "script": "if (doc.containsKey('message') && doc['message'].size()>0 &&doc['message'].value.indexOf('Merge pull request') == -1){return true}"
                }
                }],
                "minimum_should_match": 1}
        }
        commit_frequency["query"]["bool"]["must"].append(commits_without_merge_pr)
        commit_message = self.es_in.search(index=self.git_index, body=commit_frequency)
        commit_count = commit_message['aggregations']["count_of_uuid"]['value']
        commit_pr_cout = 0
        commit_all_message = [commit_message_i['_source']['hash']  for commit_message_i in commit_message['hits']['hits']]

        for commit_message_i in set(commit_all_message):
            commit_hash = commit_message_i
            if commit_hash in self.commit_message_dict:
                commit_pr_cout += self.commit_message_dict[commit_hash]
            else:
                pr_message = self.get_uuid_count_query("cardinality", repos_list, "uuid", "grimoire_creation_date", size=0)
                commit_hash_query = { "bool": {"should": [ {"match_phrase": {"commits_data": commit_hash} }],
                                        "minimum_should_match": 1
                                    }
                                }
                pr_message["query"]["bool"]["must"].append(commit_hash_query)
                prs = self.es_in.search(index=self.pr_index, body=pr_message)
                if prs['aggregations']["count_of_uuid"]['value']>0:
                    self.commit_message_dict[commit_hash] = 1
                    commit_pr_cout += 1
                else:
                    self.commit_message_dict[commit_hash] = 0
        if commit_count>0:
            return len(commit_all_message), commit_pr_cout, commit_pr_cout/len(commit_all_message)
        else:
            return 0, None, None


    def code_merge_ratio(self, date, repos_list):
        query_pr_body = self.get_uuid_count_query( "cardinality", repos_list, "uuid", "grimoire_creation_date", size=0, from_date=(date-timedelta(days=90)), to_date=date)
        query_pr_body["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true" }})
        query_pr_body["query"]["bool"]["must"].append({"match_phrase": {"merged": "true" }})
        pr_merged_count = self.es_in.search(index=self.pr_index, body=query_pr_body)[
            'aggregations']["count_of_uuid"]['value']
        query_pr_body["query"]["bool"]["must"].append({
                            "script": {
                                "script": "if(doc['merged_by_data_name'].size() > 0 && doc['author_name'].size() > 0 && doc['merged_by_data_name'].value !=  doc['author_name'].value){return true}"
                            }
                        })
        prs = self.es_in.search(index=self.pr_index, body=query_pr_body)[
            'aggregations']["count_of_uuid"]['value']
        try:
            return prs/pr_merged_count, pr_merged_count
        except ZeroDivisionError:
            return None, 0

    def pr_issue_linked(self, date, repos_list):
        pr_linked_issue = 0
        for repo in repos_list:
            query_pr_linked_issue = self.get_pr_linked_issue_count(
                repo, from_date=date-timedelta(days=90), to_date=date)
            pr_linked_issue += self.es_in.search(index=(self.pr_index, self.pr_comments_index), body=query_pr_linked_issue)[
                'aggregations']["count_of_uuid"]['value']
        query_pr_count = self.get_uuid_count_query(
            "cardinality", repos_list, "uuid", size=0, from_date=(date-timedelta(days=90)), to_date=date)
        query_pr_count["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true" }})
        pr_count = self.es_in.search(index=self.pr_index,
                                    body=query_pr_count)[
            'aggregations']["count_of_uuid"]['value']
        try:
            return pr_linked_issue/pr_count
        except ZeroDivisionError:
            return None
    def active_C1_pr_create_contributor(self, date, repos_list):
        C1_pr_contributors = self.get_all_CX_contributors(
            repos_list, (self.pr_index), pr=True, from_date=date-timedelta(days=90), to_date=date)
        return len(C1_pr_contributors)

    def active_C1_pr_comments_contributor(self, date, repos_list):
        C1_pr_comments_contributors = self.get_all_CX_comments_contributors(repos_list, (self.pr_comments_index), pr=True, from_date=date-timedelta(days=90), to_date=date)
        return len(C1_pr_comments_contributors)

    def active_C2_contributor_count(self, date, repos_list):
        query_author_uuid_data = self.get_uuid_count_contribute_query(
            repos_list, company=None, from_date=(date - timedelta(days=90)), to_date=date)
        author_uuid_count = self.es_in.search(index=(self.git_index), body=query_author_uuid_data)[
            'aggregations']["count_of_contributors"]['value']
        return author_uuid_count

    def metrics_model_enrich(self, repos_list, label, type=None, level=None, date_list=None):
        level = level if level != None else self.level
        date_list = date_list if date_list != None else self.date_list
        item_datas = []
        last_metrics_data = {}
        self.commit_message_dict = {}
        for date in date_list:
            logger.info(str(date)+"--"+self.model_name+"--"+label)
            created_since = self.created_since(date, repos_list)
            if created_since is None:
                continue
            commit_frequency_message = self.commit_frequency(date, repos_list)
            LOC_frequency = self.LOC_frequency(date, repos_list)
            lines_added_frequency = self.LOC_frequency(date, repos_list, 'lines_added')
            lines_removed_frequency = self.LOC_frequency(date, repos_list, 'lines_removed')
            git_pr_linked_ratio = self.git_pr_linked_ratio(date, repos_list)
            code_review_ratio, pr_count = self.code_review_ratio(date, repos_list)
            code_merge_ratio, pr_merged_count = self.code_merge_ratio(date, repos_list)
            metrics_data = {
                'uuid': get_uuid(str(date), self.community, level, label, self.model_name, type),
                'level': level,
                'type': type,
                'label': label,
                'model_name': self.model_name,
                'contributor_count': self.contributor_count(date, repos_list),
                'active_C2_contributor_count': self.active_C2_contributor_count(date, repos_list),
                'active_C1_pr_create_contributor': self.active_C1_pr_create_contributor(date, repos_list),
                'active_C1_pr_comments_contributor': self.active_C1_pr_comments_contributor(date, repos_list),
                'commit_frequency': commit_frequency_message[0],
                'commit_frequency_inside': commit_frequency_message[1],
                'is_maintained': round(self.is_maintained(date, repos_list, level), 4),
                'LOC_frequency': LOC_frequency,
                'lines_added_frequency': lines_added_frequency,
                'lines_removed_frequency': lines_removed_frequency,
                'pr_issue_linked_ratio': self.pr_issue_linked(date, repos_list),
                'code_review_ratio': code_review_ratio,
                'code_merge_ratio': code_merge_ratio,
                'pr_count': pr_count,
                'pr_merged_count': pr_merged_count,
                'pr_commit_count': git_pr_linked_ratio[0],
                'pr_commit_linked_count': git_pr_linked_ratio[1],
                'git_pr_linked_ratio': git_pr_linked_ratio[2],
                'grimoire_creation_date': date.isoformat(),
                'metadata__enriched_on': datetime_utcnow().isoformat()
            }
            self.cache_last_metrics_data(metrics_data, last_metrics_data)
            score = code_quality_guarantee(code_quality_decay(metrics_data, last_metrics_data, level), level)
            metrics_data["code_quality_guarantee"] = score
            item_datas.append(metrics_data)
            if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                self.es_out.bulk_upload(item_datas, "uuid")
                item_datas = []
        self.es_out.bulk_upload(item_datas, "uuid")

    def cache_last_metrics_data(self, item, last_metrics_data):
        for i in ["code_merge_ratio",  "code_review_ratio", "pr_issue_linked_ratio", "git_pr_linked_ratio"]:
            if item[i] != None:
                data = [item[i],item['grimoire_creation_date']]
                last_metrics_data[i] = data

class OrganizationsActivityMetricsModel(MetricsModel):
    def __init__(self, issue_index, repo_index=None, pr_index=None, json_file=None, git_index=None, out_index=None, git_branch=None, from_date=None, end_date=None, community=None, level=None, company=None, issue_comments_index=None, pr_comments_index=None, contributors_index=None):
        super().__init__(json_file, from_date, end_date, out_index, community, level)
        self.issue_index = issue_index
        self.repo_index = repo_index
        self.git_index = git_index
        self.pr_index = pr_index
        self.git_branch = git_branch
        self.issue_comments_index = issue_comments_index
        self.pr_comments_index = pr_comments_index
        self.contributors_index = contributors_index
        self.company = None if company == None or company == 'None' else company
        self.model_name = 'Organizations Activity'
        self.org_name_dict = {}

    def add_org_name(self, contributor_list):
        for contributor in contributor_list:
            for org in contributor["org_change_date_list"]:
                org_name = org.get("org_name") if org.get("org_name") else org.get("domain")
                is_org = True if org.get("org_name") else False
                self.org_name_dict[org_name] = is_org
           
    def contributor_count(self, date, contributor_list):
        contributor_count = 0
        contributor_identity = set()
        org_contributor_count_dict = {}  # {"Huawei": 10}
        org_contributor_identity_dict = {} # {"Huawei": {author_name1,author_name2}}

        from_date = (date - timedelta(days=90)).strftime("%Y-%m-%d")
        to_date = date.strftime("%Y-%m-%d")

        for contributor in contributor_list:
            for org in contributor["org_change_date_list"]:
                if org.get("org_name") is not None and check_times_has_overlap(org["first_date"], org["last_date"], from_date, to_date) \
                        and len(contributor_identity & set(contributor["id_identity_list"])) == 0:
                    contributor_count += 1
                    contributor_identity.update(contributor["id_identity_list"])
                    break

            for org in contributor["org_change_date_list"]:
                if check_times_has_overlap(org["first_date"], org["last_date"], from_date, to_date):
                    org_name = org.get("org_name") if org.get("org_name") else org.get("domain")
                    org_contributor_identity = org_contributor_identity_dict.get(org_name, set())
                    if len(org_contributor_identity & set(contributor["id_identity_list"])) == 0:
                        org_contributor_count_dict[org_name] = org_contributor_count_dict.get(org_name, 0) + 1
                        org_contributor_identity.update(contributor["id_identity_list"])
                        org_contributor_identity_dict[org_name] = org_contributor_identity
                    continue
            
        return contributor_count, org_contributor_count_dict
            
    def commit_frequency(self, date, contributor_list):
        total_count = 0
        commit_count = 0
        org_commit_count_dict = {}  # {"Huawei": 10}
        org_commit_percentage_dict = {}  # {"Huawei": [10, 0.3, 0.5]}

        from_date = (date - timedelta(days=90)).strftime("%Y-%m-%d")
        to_date = date.strftime("%Y-%m-%d")

        for contributor in contributor_list:
            for commit_date in contributor["code_commit_date_list"]:
                if from_date <= commit_date and commit_date <= to_date:
                    total_count += 1

            for org in contributor["org_change_date_list"]:
                if org.get("org_name") is not None and check_times_has_overlap(org["first_date"], org["last_date"], from_date, to_date):
                    for commit_date in contributor["code_commit_date_list"]:
                        if get_latest_date(from_date, org["first_date"]) <= commit_date and commit_date <= get_oldest_date(org["last_date"], to_date):
                            commit_count += 1
            
            for org in contributor["org_change_date_list"]:
                if check_times_has_overlap(org["first_date"], org["last_date"], from_date, to_date):
                    org_name = org.get("org_name") if org.get("org_name") else org.get("domain")
                    count = org_commit_count_dict.get(org_name, 0)
                    for commit_date in contributor["code_commit_date_list"]:
                        if get_latest_date(from_date, org["first_date"]) <= commit_date and commit_date <= get_oldest_date(org["last_date"], to_date):
                            count += 1
                    org_commit_count_dict[org_name] = count

        if total_count == 0:
            return 0 ,{}
        for org_name, count in org_commit_count_dict.items():
            if self.org_name_dict[org_name]:
                org_commit_percentage_dict[org_name] = [count, count/total_count, 0 if commit_count == 0 else count/commit_count]
            else:
                org_commit_percentage_dict[org_name] = [count, count/total_count, 0 if (total_count - commit_count) == 0 else count/(total_count - commit_count)]
        return commit_count/12.85, org_commit_percentage_dict

    def contribution_last(self, date, contributor_list):
        contribution_last = 0
        contributor_dict = {} #{"repo_name":[contributor1,contributor2]}
        for contributor in contributor_list:
            repo_contributor_list = contributor_dict.get(contributor["repo_name"], [])
            repo_contributor_list.append(contributor)
            contributor_dict[contributor["repo_name"]] = repo_contributor_list
        
        date_list = get_date_list(begin_date=str(
                date-timedelta(days=90)), end_date=str(date), freq='7D')
        for repo, repo_contributor_list in contributor_dict.items():  
            for day in date_list:
                org_name_set = set()
                from_date = (day - timedelta(days=7)).strftime("%Y-%m-%d")
                to_date = day.strftime("%Y-%m-%d")
                for contributor in repo_contributor_list:
                    for org in contributor["org_change_date_list"]:
                        if org.get("org_name") is not None and check_times_has_overlap(org["first_date"], org["last_date"], from_date, to_date):
                            for commit_date in contributor["code_commit_date_list"]:
                                if get_latest_date(from_date, org["first_date"]) <= commit_date and commit_date <= get_oldest_date(org["last_date"], to_date):
                                    org_name_set.add(org.get("org_name"))
                                    break
                contribution_last += len(org_name_set)
        return contribution_last
        
    def metrics_model_enrich(self, repos_list, label, type=None, level=None, date_list=None):
        level = level if level != None else self.level
        date_list = date_list if date_list != None else self.date_list
        item_datas = []
        self.org_name_dict = {}
        for date in date_list:
            logger.info(str(date)+"--"+self.model_name+"--"+label)
            created_since = self.created_since(date, repos_list)
            if created_since is None:
                continue
            contributor_list = self.get_commit_contributor_list(date, repos_list)
            if len(contributor_list) == 0:
                continue
            self.add_org_name(contributor_list)
            contributor_count, org_contributor_count_dict = self.contributor_count(date, contributor_list)
            commit_frequency, org_commit_percentage_dict = self.commit_frequency(date, contributor_list)
            org_count = self.org_count(date, contributor_list)
            contribution_last = self.contribution_last(date, contributor_list)
            for org_name in self.org_name_dict.keys():
                if org_name not in org_commit_percentage_dict.keys():
                    continue
                metrics_data = {
                    'uuid': get_uuid(str(date), org_name, self.community, level, label, self.model_name, type),
                    'level': level,
                    'type': type,
                    'label': label,
                    'model_name': self.model_name,
                    'org_name': org_name,
                    'is_org': self.org_name_dict[org_name],
                    'contributor_count': contributor_count,
                    'contributor_org_count': org_contributor_count_dict.get(org_name),
                    'commit_frequency': round(commit_frequency, 4),
                    'commit_frequency_org': round(org_commit_percentage_dict[org_name][0], 4),
                    'commit_frequency_org_percentage': round(org_commit_percentage_dict[org_name][1], 4),
                    'commit_frequency_percentage': round(org_commit_percentage_dict[org_name][2], 4),
                    'org_count': org_count,
                    'contribution_last': contribution_last,
                    'grimoire_creation_date': date.isoformat(),
                    'metadata__enriched_on': datetime_utcnow().isoformat()
                }
                score = organizations_activity(metrics_data, level)
                metrics_data["organizations_activity"] = score
                item_datas.append(metrics_data)
                if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                    self.es_out.bulk_upload(item_datas, "uuid")
                    item_datas = []
        self.es_out.bulk_upload(item_datas, "uuid")
