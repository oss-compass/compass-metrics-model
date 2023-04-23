import logging
from datetime import datetime, timedelta
from elasticsearch.exceptions import NotFoundError
from grimoirelab_toolkit.datetime import (datetime_utcnow,
                                          str_to_datetime)
from grimoire_elk.enriched.utils import get_time_diff_days
from .metrics_model import (MetricsModel,
                            MAX_BULK_UPDATE_SIZE,
                            check_times_has_overlap,
                            create_release_index,
                            get_medium)
from .utils import (get_uuid, get_date_list)
from .utils_lab import (starter_project_health, starter_project_health_decay)

logger = logging.getLogger(__name__)


class StarterProjectHealthMetricsModel(MetricsModel):
    def __init__(self, issue_index=None, pr_index=None, repo_index=None, json_file=None, git_index=None, out_index=None,
                from_date=None, end_date=None, community=None, level=None, contributors_index=None, release_index=None):
        super().__init__(json_file, from_date, end_date, out_index, community, level)
        self.model_name = 'Starter Project Health'
        self.issue_index = issue_index
        self.pr_index = pr_index
        self.git_index = git_index
        self.contributors_index = contributors_index
        self.release_index = release_index
        self.repo_index = repo_index

    def pr_first_response_time(self, date, repos_list):
        query_pr_first_reponse_avg = self.get_uuid_count_query(
            "avg", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0,
            from_date=date-timedelta(days=90), to_date=date)
        query_pr_first_reponse_avg["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
        pr_first_reponse = self.es_in.search(index=self.pr_index, body=query_pr_first_reponse_avg)
        pr_first_reponse_avg = pr_first_reponse['aggregations']["count_of_uuid"]['value']
        if pr_first_reponse_avg is None:
            return None, None
        query_pr_first_reponse_mid = self.get_uuid_count_query(
            "percentiles", repos_list, "time_to_first_attention_without_bot", "grimoire_creation_date", size=0,
            from_date=date-timedelta(days=90), to_date=date)
        query_pr_first_reponse_mid["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
        query_pr_first_reponse_mid["aggs"]["count_of_uuid"]["percentiles"]["percents"] = [
            50]
        pr_first_reponse_mid = self.es_in.search(index=self.pr_index, body=query_pr_first_reponse_mid)[
            'aggregations']["count_of_uuid"]['values']['50.0']
        return round(pr_first_reponse_avg, 4), round(pr_first_reponse_mid, 4)

    def change_request_closure_ratio(self, from_date, to_date, repos_list):
        pr_total_dsl = self.get_uuid_count_query(
            "cardinality", repos_list, "uuid", size=0, from_date=from_date, to_date=to_date)
        pr_total_dsl["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
        pr_total_dsl["aggs"]["count_of_uuid"]["cardinality"]["precision_threshold"] = 100000
        pr_total_count = self.es_in.search(index=self.pr_index, body=pr_total_dsl)[
            'aggregations']["count_of_uuid"]['value']

        pr_closed_dsl = pr_total_dsl
        pr_closed_dsl["query"]["bool"]["must"][0]["bool"]["filter"].append({
                                        "range": {
                                            "closed_at": {
                                                "gte": from_date.strftime("%Y-%m-%d"),
                                                "lt": to_date.strftime("%Y-%m-%d")
                                            }
                                        }
                                    })
        pr_closed_count = self.es_in.search(index=self.pr_index, body=pr_closed_dsl)[
            'aggregations']["count_of_uuid"]['value']
        try:
            return round(pr_closed_count / pr_total_count, 4)
        except ZeroDivisionError:
            return None

    def pr_open_time(self, date, repos_list):
        query_pr_opens = self.get_uuid_count_query("avg", repos_list, "time_to_first_attention_without_bot",
                                                   "grimoire_creation_date", size=10000,
                                                   from_date=date-timedelta(days=90), to_date=date)
        query_pr_opens["query"]["bool"]["must"].append({"match_phrase": {"pull_request": "true"}})
        pr_opens_items = self.es_in.search(
            index=self.pr_index, body=query_pr_opens)['hits']['hits']
        if len(pr_opens_items) == 0:
            return None, None
        pr_open_time_repo = []
        for item in pr_opens_items:
            if 'state' in item['_source']:
                if item['_source']['state'] == 'merged' and item['_source']['merged_at'] and \
                        str_to_datetime(item['_source']['merged_at']) < date:
                    pr_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], item['_source']['merged_at']))
                if item['_source']['state'] == 'closed' and \
                        str_to_datetime(item['_source']['closed_at'] or item['_source']['updated_at']) < date:
                    pr_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], item['_source']['closed_at'] or item['_source']['updated_at']))
                else:
                    pr_open_time_repo.append(get_time_diff_days(
                        item['_source']['created_at'], str(date)))
        if len(pr_open_time_repo) == 0:
            return None, None
        pr_open_time_repo_avg = float(sum(pr_open_time_repo)/len(pr_open_time_repo))
        pr_open_time_repo_mid = get_medium(pr_open_time_repo)
        return round(pr_open_time_repo_avg, 4), round(pr_open_time_repo_mid, 4)

    def bus_factor(self, date, commit_contributor_list):
        if len(commit_contributor_list) == 0:
            return None
        bus_factor = 0
        author_name_dict = {}  # {"author_name:" commit_count}
        from_date = (date - timedelta(days=90)).strftime("%Y-%m-%d")
        to_date = date.strftime("%Y-%m-%d")
        for item in commit_contributor_list:
            if item["is_bot"]:
                continue
            name = item["id_git_author_name_list"][0]
            count = author_name_dict.get(name, 0)
            for commit_date in item["code_commit_date_list"]:
                if commit_date >= to_date:
                    break
                if from_date <= commit_date and commit_date < to_date:
                    count += 1
            author_name_dict[name] = count
        commit_count_list = [commit_count for commit_count in author_name_dict.values()]
        commit_count_list.sort(reverse=True)
        commit_count_threshold = sum(commit_count_list) * 0.5
        front_commit_count = 0
        for index, commit_count in enumerate(commit_count_list):
            front_commit_count += commit_count
            if commit_count_threshold < front_commit_count:
                bus_factor = index + 1
                break
        return bus_factor

    def recent_releases_count(self, date, repos_list):
        try:
            query_recent_releases_count = self.get_recent_releases_uuid_count(
                "cardinality", repos_list, "uuid", from_date=(date-timedelta(days=365)), to_date=date)
            releases_count = self.es_in.search(index=self.release_index, body=query_recent_releases_count)[
                'aggregations']["count_of_uuid"]['value']
            return releases_count
        except NotFoundError:
            return 0

    def cache_last_metrics_data(self, item, last_metrics_data):
        for i in ["pr_time_to_first_response_avg",
                  "pr_time_to_first_response_mid",
                  "change_request_closure_ratio_all_period",
                  "change_request_closure_ratio_same_period",
                  "pr_time_to_close_avg",
                  "pr_time_to_close_mid"]:
            if item[i] is not None:
                data = [item[i], item['grimoire_creation_date']]
                last_metrics_data[i] = data

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
            pr_time_to_first_response_avg, pr_time_to_first_response_mid = self.pr_first_response_time(date, repos_list)
            pr_time_to_close_avg, pr_time_to_close_mid = self.pr_open_time(date, repos_list)
            commit_contributor_list = self.get_contributor_list(date - timedelta(days=90), date, repos_list, "code_commit_date_list")
            metrics_data = {
                'uuid': get_uuid(str(date), self.community, level, label, self.model_name, type),
                'level': level,
                'type': type,
                'label': label,
                'model_name': self.model_name,
                'pr_time_to_first_response_avg': pr_time_to_first_response_avg,
                'pr_time_to_first_response_mid': pr_time_to_first_response_mid,
                'change_request_closure_ratio_all_period': self.change_request_closure_ratio(str_to_datetime("1970-01-01"), date, repos_list),
                'change_request_closure_ratio_same_period': self.change_request_closure_ratio(date - timedelta(days=90), date, repos_list),
                'pr_time_to_close_avg': pr_time_to_close_avg,
                'pr_time_to_close_mid': pr_time_to_close_mid,
                'bus_factor': self.bus_factor(date, commit_contributor_list),
                'release_frequency': self.recent_releases_count(date, repos_list),
                'grimoire_creation_date': date.isoformat(),
                'metadata__enriched_on': datetime_utcnow().isoformat()
            }
            self.cache_last_metrics_data(metrics_data, last_metrics_data)
            score = starter_project_health(starter_project_health_decay(metrics_data, last_metrics_data, level), level)
            metrics_data["starter_project_health"] = score
            item_datas.append(metrics_data)
            if len(item_datas) > MAX_BULK_UPDATE_SIZE:
                self.es_out.bulk_upload(item_datas, "uuid")
                item_datas = []
        self.es_out.bulk_upload(item_datas, "uuid")