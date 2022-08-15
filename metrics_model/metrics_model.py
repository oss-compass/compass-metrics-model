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
import json
import yaml
import pandas as pd
import ssl,certifi
from grimoire_elk.enriched.utils import get_time_diff_days
from grimoirelab_toolkit.datetime import (datetime_utcnow,
                                          str_to_datetime,
                                          datetime_to_utc)
from elasticsearch import Elasticsearch, RequestsHttpConnection
from grimoire_elk.elastic import ElasticSearch
from utils import get_activity_score, community_support
import os,inspect
import sys
current_dir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
os.chdir(current_dir)
sys.path.append('../')
from tools.release_index import get_opensearch_client,newest_message,opensearch_search,add_release_message

MAX_BULK_UPDATE_SIZE = 100

def get_date_list(begin_date, end_date, freq='W-MON'):
    '''Get date list from begin_date to end_date every Monday'''
    date_list = [x for x in list(pd.date_range(freq=freq, start=datetime_to_utc(
        str_to_datetime(begin_date)), end=datetime_to_utc(str_to_datetime(end_date))))]
    return date_list


def get_all_repo(file, source):
    '''Get all repo from json file'''
    all_repo_json = json.load(open(file))
    all_repo = []
    for i in all_repo_json:
        for j in all_repo_json[i][source]:
            all_repo.append(j)
    return all_repo

def create_release_index(all_repo, release_index):
    opensearch_conn_infos = json.load(open("../tools/opensearch_message.json"))
    opensearch_client = get_opensearch_client(opensearch_conn_infos)
    for repo_url in all_repo:
        query = newest_message(repo_url)
        query_hits = opensearch_search(opensearch_client, "gitee_repo-enriched", query)["hits"]["hits"]
        if len(query_hits) > 0 :
            items = query_hits[0]["_source"]["releases"]
            add_release_message(opensearch_client, release_index, repo_url, items)


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
    elif n%2 == 0:
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
        self.date_list = get_date_list(from_date, end_date)
    
    def metrics_model_metrics(self, elastic_url):
        self.es_in = Elasticsearch(elastic_url, use_ssl=True,verify_certs=False, connection_class=RequestsHttpConnection)
        self.es_out = ElasticSearch(elastic_url, self.out_index)
        
        if self.level == "community":
            all_repos_list = self.all_repo
            label = "community"
            self.metrics_model_enrich(all_repos_list, self.community)
        if  self.level == "project":
            all_repo_json = json.load(open(self.json_file))
            for project in all_repo_json:
                repos_list = []
                for j in all_repo_json[project][self.issue_index.split('_')[0]]:
                    repos_list.append(j)
                self.metrics_model_enrich(repos_list, project)
        if  self.level == "repo":
            all_repo_json = json.load(open(self.json_file))
            for project in all_repo_json:
                for j in all_repo_json[project][self.issue_index.split('_')[0]]:
                    self.metrics_model_enrich([j], j)
    
    
    def metrics_model_enrich(repos_list, label):
        pass

    def created_since(self, date, repos_list):
        created_since_list = []
        for repo in repos_list:
            query_first_commit_since = self.get_updated_since_query([repo], date_field='grimoire_creation_date', to_date=date, order="asc")
            first_commit_since = self.es_in.search(index=self.git_index, body=query_first_commit_since)['hits']['hits']
            if len(first_commit_since) > 0:
                creation_since = first_commit_since[0]['_source']["grimoire_creation_date"]
                created_since_list.append(get_time_diff_months(creation_since, str(date)))
                # print(get_time_diff_months(creation_since, str(date)))
                # print(repo)
        if created_since_list:
            return sum(created_since_list) / len(created_since_list)
        else:
            return 0

    def get_uuid_count_query(self, option, repos_list, field, date_field="grimoire_creation_date", size = 0, from_date=str_to_datetime("1970-01-01"), to_date= datetime_utcnow()):
        query = {
            "size": size,
            "track_total_hits": "true",
            "aggs": {"count_of_uuid":
                     {option:
                      {"field": field}
                      }
                     },
            "query":
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
             }
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
            "query": {
                "bool": {
                    "should": [{
                        "simple_query_string": {
                            "query": i+'*',
                            "fields": ["tag"]
                        }
                    } for i in repos_list],
                    "minimum_should_match": 1,
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
                    } ],
                "minimum_should_match": 1}}]
        return query


    def get_updated_since_query(self, repos_list, date_field="grimoire_creation_date",order="desc", to_date=datetime_utcnow()):
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
    

    def get_issue_closed_uuid_count(self, option, repos_list, field, from_date=str_to_datetime("1970-01-01"), to_date= datetime_utcnow()):
        query = {
            "size": 0,
            "track_total_hits":True,
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
                    {"term":{"state": "open"}},
                    {"term":{"state": "progressing"}}
                ]           
                ,
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

    def get_recent_releases_uuid_count(self, option, repos_list, field, from_date=str_to_datetime("1970-01-01"), to_date= datetime_utcnow()):
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


class ActivityMetricsModel(MetricsModel):
    def __init__(self, issue_index, repo_index=None, pr_index=None, release_index=None, json_file=None, git_index=None, out_index=None, git_branch=None, from_date=None, end_date=None, community=None, level=None):
        super().__init__(json_file, from_date, end_date, out_index, community, level)
        self.issue_index = issue_index
        self.repo_index = repo_index
        self.git_index = git_index
        self.pr_index = pr_index
        self.release_index = release_index
        self.git_branch = git_branch
        self.all_project = get_all_project(self.json_file)
        self.all_repo = get_all_repo(self.json_file, self.issue_index.split('_')[0])
        self.model_name = 'Activity'
        create_release_index(self.all_repo, release_index)

    def contributor_count(self, date, repos_list):
        query_author_uuid_data = self.get_uuid_count_contribute_query(repos_list, company=None, from_date=(date - timedelta(days=90)), to_date=date)
        author_uuid_count = self.es_in.search(index=(self.git_index, self.issue_index, self.pr_index), body=query_author_uuid_data)['aggregations']["count_of_contributors"]['value']
        return author_uuid_count


    def commit_frequency(self, date, repos_list):
        query_commit_frequency = self.get_uuid_count_query("cardinality", repos_list, "hash","grimoire_creation_date", size = 0, from_date=date - timedelta(days=90), to_date=date)
        commit_frequency = self.es_in.search(index=self.git_index, body=query_commit_frequency)[
            'aggregations']["count_of_uuid"]['value']
        return commit_frequency/12.85
    
    def updated_since(self, date, repos_list):
        updated_since_list = []
        for repo in repos_list:
            query_updated_since = self.get_updated_since_query([repo], date_field='metadata__updated_on', to_date=date)
            updated_since = self.es_in.search(index=self.git_index, body=query_updated_since)['hits']['hits']
            if updated_since:
                updated_since_list.append(get_time_diff_months(updated_since[0]['_source']["metadata__updated_on"], str(date)))
        if updated_since_list:
            return sum(updated_since_list) / len(updated_since_list)
        else:
            return 0

    def closed_issue_count(self, date, repos_list):
        query_issue_closed = self.get_issue_closed_uuid_count("cardinality", repos_list, "uuid", from_date=(date-timedelta(days=90)), to_date=date)
        issue_closed = self.es_in.search(index=self.issue_index, body=query_issue_closed)['aggregations']["count_of_uuid"]['value']
        return issue_closed
     
    def updated_issue_count(self, date, repos_list):
        query_issue_updated_since = self.get_uuid_count_query("cardinality", repos_list, "uuid", date_field='metadata__updated_on', size=0, from_date=(date-timedelta(days=90)),to_date=date)
        updated_issues_count = self.es_in.search(index=self.issue_index, body=query_issue_updated_since)['aggregations']["count_of_uuid"]['value']
        return updated_issues_count

    def comment_frequency(self, date, repos_list):
        query_issue_comments_count = self.get_uuid_count_query("sum", repos_list, "num_of_comments_without_bot", date_field='grimoire_creation_date', size=0, from_date=(date-timedelta(days=90)), to_date=date)
        issue = self.es_in.search(index=self.issue_index, body=query_issue_comments_count)           
        try:                                               
            return float(issue['aggregations']["count_of_uuid"]['value']/issue["hits"]["total"]["value"])
        except ZeroDivisionError:
            return 0

    def code_review_count(self, date, repos_list):
        query_pr_comments_count = self.get_uuid_count_query("sum", repos_list, "num_review_comments_without_bot", size=0, from_date=(date-timedelta(days=90)), to_date=date)
        prs = self.es_in.search(index=self.pr_index, body=query_pr_comments_count)           
        try:                                               
            return prs['aggregations']["count_of_uuid"]['value']/prs["hits"]["total"]["value"]
        except ZeroDivisionError:
            return 0
    
    def recent_releases_count(self, date, repos_list):
        query_recent_releases_count = self.get_recent_releases_uuid_count("cardinality", repos_list, "uuid", from_date=(date-timedelta(days=365)), to_date=date)
        releases_count = self.es_in.search(index=self.release_index, body=query_recent_releases_count)['aggregations']["count_of_uuid"]['value']
        return releases_count

    def metrics_model_enrich(self,repos_list, label):
        item_datas = []

        for date in self.date_list:
            print(date)
            created_since = self.created_since(date, repos_list)
            if created_since < 0:
                continue
            metrics_data = {
                'uuid': uuid(str(date), self.community, self.level, label, self.model_name),
                'level':self.level,
                'label':label,
                'model_name': self.model_name,
                'contributor_count': int(self.contributor_count(date, repos_list)),
                'commit_frequency': round(self.commit_frequency(date, repos_list), 4),
                'created_since': round(self.created_since(date, repos_list), 4),
                'comment_frequency': float(round(self.comment_frequency(date, repos_list), 4)),
                'code_review_count': round(self.code_review_count(date, repos_list), 4),
                'updated_since': float(round(self.updated_since(date, repos_list), 4)),
                'closed_issues_count': self.closed_issue_count(date, repos_list),
                'updated_issues_count':self.updated_issue_count(date, repos_list),
                'recent_releases_count':self.recent_releases_count(date, repos_list),
                'grimoire_creation_date': date.isoformat(),
                'metadata__enriched_on': datetime_utcnow().isoformat()
            }
            score = get_activity_score(metrics_data)
            metrics_data["activity_score"] = score
            item_datas.append(metrics_data)
            if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                self.es_out.bulk_upload(item_datas, "uuid")
                item_datas = []
        self.es_out.bulk_upload(item_datas, "uuid")
        item_datas = []


class CommunitySupportMetricsModel(MetricsModel):
    def __init__(self, issue_index=None, pr_index=None, git_index=None,  json_file=None, out_index=None, from_date=None, end_date=None, community=None, level=None):
        super().__init__(json_file, from_date, end_date, out_index, community, level)
        self.issue_index = issue_index
        self.all_project = get_all_project(self.json_file)
        self.all_repo = get_all_repo(
            self.json_file, self.issue_index.split('_')[0])
        self.model_name = 'Community Support and Service'
        self.pr_index = pr_index
        self.git_index = git_index


    def issue_first_reponse(self, date, repos_list):
        query_issue_first_reponse_avg = self.get_uuid_count_query(
            "avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0, from_date=date-timedelta(days=90), to_date=date)
        issue_first_reponse_avg = self.es_in.search(index=self.issue_index, body=query_issue_first_reponse_avg)[
            'aggregations']["count_of_uuid"]['value']
        query_issue_first_reponse_mid = self.get_uuid_count_query(
            "percentiles", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0, from_date=date-timedelta(days=90), to_date=date)
        query_issue_first_reponse_mid["aggs"]["count_of_uuid"]["percentiles"]["percents"] = [
            50]
        issue_first_reponse_mid = self.es_in.search(index=self.issue_index, body=query_issue_first_reponse_mid)[
            'aggregations']["count_of_uuid"]['values']['50.0']
        return issue_first_reponse_avg, issue_first_reponse_mid if issue_first_reponse_avg else 0,0

    def issue_open_time(self, date, repos_list):
        query_issue_opens = self.get_uuid_count_query("avg", repos_list, "time_to_first_attention_without_bot",
                                                      "grimoire_creation_date", size=10000, from_date=date-timedelta(days=90), to_date=date)
        issue_opens_items = self.es_in.search(
            index=self.issue_index, body=query_issue_opens)['hits']['hits']
        issue_open_time_repo = []
        for item in issue_opens_items:
            if 'state' in item['_source']:
                if item['_source']['closed_at']:
                    if item['_source']['state'] in ['closed', 'rejected'] and str_to_datetime(item['_source']['closed_at']) < date:
                        issue_open_time_repo.append(get_time_diff_days(
                            item['_source']['created_at'], item['_source']['closed_at']))
                    # else:
                    #     issue_open_time_repo.append(get_time_diff_days(
                    #         item['_source']['created_at'], str(date)))
                else:
                    issue_open_time_repo.append(get_time_diff_days(
                            item['_source']['created_at'], str(date)))
        try:
            issue_open_time_repo_avg = sum(
                issue_open_time_repo)/len(issue_open_time_repo)
        except ZeroDivisionError:
            issue_open_time_repo_avg = 0

        issue_open_time_repo_mid = get_medium(issue_open_time_repo)
        return issue_open_time_repo_avg, issue_open_time_repo_mid

    def pr_open_time(self, date, repos_list):
        query_pr_opens = self.get_uuid_count_query("avg", repos_list, "time_to_first_attention_without_bot",
                                                   "grimoire_creation_date", size=10000, from_date=date-timedelta(days=90), to_date=date)
        pr_opens_items = self.es_in.search(
            index=self.pr_index, body=query_pr_opens)['hits']['hits']
        pr_open_time_repo = []
        for item in pr_opens_items:
            if 'state' in item['_source']:
                if item['_source']['state'] == 'merged' and item['_source']['merged_at'] and str_to_datetime(item['_source']['merged_at']) < date:
                    pr_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], item['_source']['merged_at']))
                if item['_source']['state'] == 'closed' and str_to_datetime(item['_source']['closed_at']) < date:
                    pr_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], item['_source']['closed_at']))
                else:
                    pr_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], str(date)))
        try:
            pr_open_time_repo_avg = float(sum(pr_open_time_repo)/len(pr_open_time_repo))
        except ZeroDivisionError:
            pr_open_time_repo_avg = 0
        pr_open_time_repo_mid = get_medium(pr_open_time_repo)
        return pr_open_time_repo_avg, pr_open_time_repo_mid

    def comment_frequency(self, date, repos_list):
        query_issue_comments_count = self.get_uuid_count_query(
            "sum", repos_list, "num_of_comments_without_bot", date_field='grimoire_creation_date', size=0, from_date=(date-timedelta(days=90)), to_date=date)
        issue = self.es_in.search(
            index=self.issue_index, body=query_issue_comments_count)
        try:
            return float(issue['aggregations']["count_of_uuid"]['value']/issue["hits"]["total"]["value"])
        except ZeroDivisionError:
            return 0
     
    def updated_issue_count(self, date, repos_list):
        query_issue_updated_since = self.get_uuid_count_query(
            "cardinality", repos_list, "uuid", date_field='metadata__updated_on', size=0, from_date=(date-timedelta(days=90)), to_date=date)
        updated_issues_count = self.es_in.search(index=self.issue_index, body=query_issue_updated_since)[
            'aggregations']["count_of_uuid"]['value']
        return updated_issues_count

    def code_review_count(self, date, repos_list):
        query_pr_comments_count = self.get_uuid_count_query(
            "avg", repos_list, "num_review_comments_without_bot", size=0, from_date=(date-timedelta(days=90)), to_date=date)
        prs = self.es_in.search(index=self.pr_index,
                                body=query_pr_comments_count)[
            'aggregations']["count_of_uuid"]['value']
        return prs if prs else 0.0   
    
    def closed_pr_count(self, date, repos_list):
        query_pr_closed = self.get_pr_closed_uuid_count(
            "cardinality", repos_list, "uuid", from_date=(date-timedelta(days=90)), to_date=date)
        pr_closed = self.es_in.search(index=self.pr_index, body=query_pr_closed)[
            'aggregations']["count_of_uuid"]['value']
        return pr_closed
        
    def metrics_model_enrich(self, repos_list, label):
        item_datas = []
        for date in self.date_list:
            print(date)
            created_since = self.created_since(date, repos_list)
            if created_since < 0:
                continue
            issue_first = self.issue_first_reponse(date, repos_list)
            issue_open_time = self.issue_open_time(date, repos_list)
            pr_open_time = self.pr_open_time(date, repos_list)
            metrics_data = {
                'uuid': uuid(str(date), self.community, self.level, label, self.model_name),
                'level': self.level,
                'label': label,
                'model_name': self.model_name,
                'issue_first_reponse_avg': round(issue_first[0],4) if issue_first[0] else 0.0,
                'issue_first_reponse_mid': round(issue_first[1],4) if issue_first[1] else 0.0,
                'issue_open_time_avg': round(issue_open_time[0],4) if issue_open_time[0] else 0.0,
                'issue_open_time_mid': round(issue_open_time[1],4) if issue_open_time[1] else 0.0,
                'pr_open_time_avg': round(pr_open_time[0],4) if pr_open_time[0] else 0.0,
                'pr_open_time_mid': round(pr_open_time[1],4) if pr_open_time[1] else 0.0,
                'comment_frequency': float(round(self.comment_frequency(date, repos_list), 4)),
                'code_review_count': float(self.code_review_count(date, repos_list)),
                'updated_issues_count': self.updated_issue_count(date, repos_list),
                'closed_prs_count': self.closed_pr_count(date, repos_list),
                'grimoire_creation_date': date.isoformat(),
                'metadata__enriched_on': datetime_utcnow().isoformat()
            }
            score = community_support(metrics_data)
            metrics_data["community_support_score"] = score
            item_datas.append(metrics_data)
            if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                self.es_out.bulk_upload(item_datas, "uuid")
                item_datas = []
        self.es_out.bulk_upload(item_datas, "uuid")
        item_datas = []

if __name__ == '__main__':
    CONF = yaml.safe_load(open('../conf.yaml'))
    elastic_url = CONF['url']
    params = CONF['params']
    kwargs = {}
    
    for item in ['issue_index', 'pr_index','release_index','json_file', 'git_index',  'from_date', 'end_date', 'out_index', 'community', 'level']:
        kwargs[item] = params[item]
    model_activity = ActivityMetricsModel(**kwargs)
    model_activity.metrics_model_metrics(elastic_url)
    
    # for item in ['issue_index', 'pr_index', 'json_file', 'git_index', 'from_date', 'end_date', 'out_index', 'community', 'level']:
    #     kwargs[item] = params[item]
    # model_community = CommunitySupportMetricsModel(**kwargs)
    # model_community.metrics_model_metrics()
