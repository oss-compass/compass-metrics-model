import math
import pendulum
import pandas as pd

from perceval.backend import uuid
from grimoirelab_toolkit.datetime import (datetime_to_utc,str_to_datetime)

BACKOFF_FACTOR = 0.2
MAX_RETRIES = 21
MAX_RETRIES_ON_REDIRECT = 5
MAX_RETRIES_ON_READ = 8
MAX_RETRIES_ON_CONNECT = 21
STATUS_FORCE_LIST = [408, 409, 429, 502, 503, 504]
METADATA_FILTER_RAW = 'metadata__filter_raw'
REPO_LABELS = 'repository_labels'

DECAY_COEFFICIENT = 0.0027

def get_uuid(*args):
    args_list = []
    for arg in args:
        if arg is None or arg == '':
            continue
        args_list.append(arg)
    return uuid(*args_list)

def get_date_list(begin_date, end_date, freq='W-MON'):
    '''Get date list from begin_date to end_date every Monday'''
    date_list = [x for x in list(pd.date_range(freq=freq, start=datetime_to_utc(
        str_to_datetime(begin_date)), end=datetime_to_utc(str_to_datetime(end_date))))]
    return date_list

def normalize(score, min_score, max_score):
    return (score-min_score)/(max_score-min_score)

def get_param_score(param, max_value, weight=1):
    """Return paramater score given its current value, max value and
    parameter weight."""
    return (math.log(1 + param) / math.log(1 + max(param, max_value))) * weight

def get_score_ahp(item, param_dict):
    total_weight = 0
    total_param_score = 0
    for key, value in param_dict.items():
        total_weight += value[0]
        param = 0
        if item[key] is None:
            if value[0] < 0:
                param = value[1]
        else:
           param = item[key]
        total_param_score += get_param_score(param,value[1] ,value[0])
    try:
        return round(total_param_score / total_weight, 5)
    except ZeroDivisionError:
        return 0.0

def get_activity_score(item, level="repo", w={}):
    param_dict = {}
    if level == "community" or level == "project":
        param_dict = {
            "contributor_count": [w['CONTRIBUTOR_COUNT_WEIGHT_ACTIVITY'], w['CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_ACTIVITY']],
            "commit_frequency": [w['COMMIT_FREQUENCY_WEIGHT_ACTIVITY'], w['COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY']],
            "updated_since": [w['UPDATED_SINCE_WEIGHT_ACTIVITY'], w['UPDATED_SINCE_MULTIPLE_THRESHOLD_ACTIVITY']],
            "org_count": [w['ORG_COUNT_WEIGHT_ACTIVITY'], w['ORG_COUNT_MULTIPLE_THRESHOLD_ACTIVITY']],
            # "created_since": [w['CREATED_SINCE_WEIGHT_ACTIVITY'], w['CREATED_SINCE_MULTIPLE_THRESHOLD_ACTIVITY']],
            "comment_frequency": [w['COMMENT_FREQUENCY_WEIGHT_ACTIVITY'], w['COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY']],
            "code_review_count": [w['CODE_REVIEW_COUNT_WEIGHT_ACTIVITY'], w['CODE_REVIEW_COUNT_MULTIPLE_THRESHOLD_ACTIVITY']],
            "updated_issues_count": [w['UPDATED_ISSUES_WEIGHT_ACTIVITY'], w['UPDATED_ISSUES_MULTIPLE_THRESHOLD_ACTIVITY']],
            "recent_releases_count": [w['RECENT_RELEASES_WEIGHT_ACTIVITY'], w['RECENT_RELEASES_MULTIPLE_THRESHOLD_ACTIVITY']]
        }
    if level == "repo":
        param_dict = {
            "contributor_count":[w['CONTRIBUTOR_COUNT_WEIGHT_ACTIVITY'], w['CONTRIBUTOR_COUNT_THRESHOLD_ACTIVITY']],
            "commit_frequency":[w['COMMIT_FREQUENCY_WEIGHT_ACTIVITY'], w['COMMIT_FREQUENCY_THRESHOLD_ACTIVITY']],
            "updated_since":[w['UPDATED_SINCE_WEIGHT_ACTIVITY'], w['UPDATED_SINCE_THRESHOLD_ACTIVITY']],
            "org_count":[w['ORG_COUNT_WEIGHT_ACTIVITY'], w['ORG_COUNT_THRESHOLD_ACTIVITY']],
            # "created_since":[w['CREATED_SINCE_WEIGHT_ACTIVITY'], w['CREATED_SINCE_THRESHOLD_ACTIVITY']],
            "comment_frequency":[w['COMMENT_FREQUENCY_WEIGHT_ACTIVITY'], w['COMMENT_FREQUENCY_THRESHOLD_ACTIVITY']],
            "code_review_count":[w['CODE_REVIEW_COUNT_WEIGHT_ACTIVITY'], w['CODE_REVIEW_COUNT_THRESHOLD_ACTIVITY']],
            "updated_issues_count":[w['UPDATED_ISSUES_WEIGHT_ACTIVITY'], w['UPDATED_ISSUES_THRESHOLD_ACTIVITY']],
            "recent_releases_count":[w['RECENT_RELEASES_WEIGHT_ACTIVITY'], w['RECENT_RELEASES_THRESHOLD_ACTIVITY']]
        }
    score = get_score_ahp(item, param_dict)
    return normalize(score, w['MIN_ACTIVITY_SCORE'], w['MAX_ACTIVITY_SCORE'])

def community_support(item, level="repo", w={}):
    param_dict = {}
    if level == "community" or level == "project":
        param_dict = {
            "issue_first_reponse_avg": [w['ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY'] * 0.5, w['ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY']],
            "issue_first_reponse_mid": [w['ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY'] * 0.5, w['ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY']],
            "bug_issue_open_time_avg": [w['BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY'] * 0.5, w['BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY']],
            "bug_issue_open_time_mid": [w['BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY'] * 0.5, w['BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY']],
            "comment_frequency": [w['COMMENT_FREQUENCY_WEIGHT_COMMUNITY'], w['COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_COMMUNITY']],
            "updated_issues_count": [w['UPDATED_ISSUES_WEIGHT_COMMUNITY'], w['UPDATED_ISSUES_MULTIPLE_THRESHOLD_COMMUNITY']],
            "pr_open_time_avg": [w['PR_OPEN_TIME_WEIGHT_COMMUNITY'] * 0.5, w['PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY']],
            "pr_open_time_mid": [w['PR_OPEN_TIME_WEIGHT_COMMUNITY'] * 0.5, w['PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY']],
            "code_review_count": [w['CODE_REVIEW_WEIGHT_COMMUNITY'], w['CODE_REVIEW_MULTIPLE_THRESHOLD_COMMUNITY']],
            "closed_prs_count": [w['CLOSED_PRS_WEIGHT_COMMUNITY'], w['CLOSED_PRS_MULTIPLE_THRESHOLD_COMMUNITY']]
        }
    if level == "repo":
        param_dict = {
            "issue_first_reponse_avg":[w['ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY']*0.5, w['ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY']],
            "issue_first_reponse_mid":[w['ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY']*0.5, w['ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY']],
            "bug_issue_open_time_avg":[w['BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY']*0.5, w['BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY']],
            "bug_issue_open_time_mid":[w['BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY']*0.5, w['BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY']],
            "comment_frequency":[w['COMMENT_FREQUENCY_WEIGHT_COMMUNITY'], w['COMMENT_FREQUENCY_THRESHOLD_COMMUNITY']],
            "updated_issues_count":[w['UPDATED_ISSUES_WEIGHT_COMMUNITY'], w['UPDATED_ISSUES_THRESHOLD_COMMUNITY']],
            "pr_open_time_avg":[w['PR_OPEN_TIME_WEIGHT_COMMUNITY']*0.5, w['PR_OPEN_TIME_THRESHOLD_COMMUNITY']],
            "pr_open_time_mid":[w['PR_OPEN_TIME_WEIGHT_COMMUNITY']*0.5, w['PR_OPEN_TIME_THRESHOLD_COMMUNITY']],
            "code_review_count":[w['CODE_REVIEW_WEIGHT_COMMUNITY'], w['CODE_REVIEW_THRESHOLD_COMMUNITY']],
            "closed_prs_count":[w['CLOSED_PRS_WEIGHT_COMMUNITY'], w['CLOSED_PRS_THRESHOLD_COMMUNITY']]
        }
    score = get_score_ahp(item, param_dict)
    return normalize(score, w['MIN_COMMUNITY_SCORE'], w['MAX_COMMUNITY_SCORE'])

def code_quality_guarantee(item, level="repo", w={}):
    param_dict = {}
    if level == "community" or level == "project":
        param_dict = {
            "contributor_count": [w['CONTRIBUTOR_COUNT_WEIGHT_CODE'], w['CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_CODE']],
            "commit_frequency": [w['COMMIT_FREQUENCY_WEIGHT_CODE'], w['COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_CODE']],
            "is_maintained": [w['IS_MAINTAINED_WEIGHT_CODE'], w['IS_MAINTAINED_MULTIPLE_THRESHOLD_CODE']],
            "git_pr_linked_ratio": [w['COMMIT_PR_LINKED_RATIO_WEIGHT_CODE'], w['COMMIT_PR_LINKED_RATIO_MULTIPLE_THRESHOLD_CODE']],
            "pr_issue_linked_ratio": [w['PR_ISSUE_LINKED_WEIGHT_CODE'], w['PR_ISSUE_LINKED_MULTIPLE_THRESHOLD_CODE']],
            "code_review_ratio": [w['CODE_REVIEW_RATIO_WEIGHT_CODE'], w['CODE_REVIEW_RATIO_MULTIPLE_THRESHOLD_CODE']],
            "code_merge_ratio": [w['CODE_MERGE_RATIO_WEIGHT_CODE'], w['CODE_MERGE_RATIO_MULTIPLE_THRESHOLD_CODE']],
            "w['LOC_']frequency": [w['LOC_FREQUENCY_WEIGHT_CODE'], w['LOC_FREQUENCY_MULTIPLE_THRESHOLD_CODE']],
        }
    if level == "repo":
        param_dict = {
            "contributor_count":[w['CONTRIBUTOR_COUNT_WEIGHT_CODE'], w['CONTRIBUTOR_COUNT_THRESHOLD_CODE']],
            "commit_frequency":[w['COMMIT_FREQUENCY_WEIGHT_CODE'], w['COMMIT_FREQUENCY_THRESHOLD_CODE']],
            "is_maintained":[w['IS_MAINTAINED_WEIGHT_CODE'], w['IS_MAINTAINED_THRESHOLD_CODE']],
            "git_pr_linked_ratio":[w['COMMIT_PR_LINKED_RATIO_WEIGHT_CODE'], w['COMMIT_PR_LINKED_RATIO_THRESHOLD_CODE']],
            "pr_issue_linked_ratio":[w['PR_ISSUE_LINKED_WEIGHT_CODE'], w['PR_ISSUE_LINKED_THRESHOLD_CODE']],
            "code_review_ratio":[w['CODE_REVIEW_RATIO_WEIGHT_CODE'], w['CODE_REVIEW_RATIO_THRESHOLD_CODE']],
            "code_merge_ratio":[w['CODE_MERGE_RATIO_WEIGHT_CODE'], w['CODE_MERGE_RATIO_THRESHOLD_CODE']],
            "LOC_frequency":[w['LOC_FREQUENCY_WEIGHT_CODE'], w['LOC_FREQUENCY_THRESHOLD_CODE']],
        }
    return get_score_ahp(item, param_dict)

def organizations_activity(item, level="repo", w={}):
    param_dict = {}
    if level == "community" or level == "project":
        param_dict = {
            "contributor_count":[w['CONTRIBUTOR_COUNT_WEIGHT_ORG_ACTIVITY'], w['CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_ORG_ACTIVITY']],
            "commit_frequency":[w['COMMIT_FREQUENCY_WEIGHT_ORG_ACTIVITY'], w['COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ORG_ACTIVITY']],
            "org_count":[w['ORG_COUNT_WEIGHT_ORG_ACTIVITY'], w['ORG_COUNT_THRESHOLD_ORG_ACTIVITY']],
            "contribution_last":[w['CONTRIBUTION_LAST_WEIGHT_ORG_ACTIVITY'], w['CONTRIBUTION_LAST_MULTIPLE_THRESHOLD_ORG_ACTIVITY']],
        }
    if level == "repo":
        param_dict = {
            "contributor_count":[w['CONTRIBUTOR_COUNT_WEIGHT_ORG_ACTIVITY'], w['CONTRIBUTOR_COUNT_THRESHOLD_ORG_ACTIVITY']],
            "commit_frequency":[w['COMMIT_FREQUENCY_WEIGHT_ORG_ACTIVITY'], w['COMMIT_FREQUENCY_THRESHOLD_ORG_ACTIVITY']],
            "org_count":[w['ORG_COUNT_WEIGHT_ORG_ACTIVITY'], w['ORG_COUNT_THRESHOLD_ORG_ACTIVITY']],
            "contribution_last":[w['CONTRIBUTION_LAST_WEIGHT_ORG_ACTIVITY'], w['CONTRIBUTION_LAST_THRESHOLD_ORG_ACTIVITY']],
        }
    return get_score_ahp(item, param_dict)

def increment_decay(last_data, threshold, days):
    return min(last_data + DECAY_COEFFICIENT * threshold * days, threshold)

def decrease_decay(last_data, threshold, days):
    return max(last_data - DECAY_COEFFICIENT * threshold * days, 0)

def community_decay(item, last_data, level="repo", w={}):
    if last_data == None:
        return item
    decay_item = item.copy()
    increment_decay_dict = {}
    decrease_decay_dict = {}
    if level == "community" or level == "project":
        increment_decay_dict = {
            "issue_first_reponse_avg": w['ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY'],
            "issue_first_reponse_mid": w['ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY'],
            "bug_issue_open_time_avg": w['BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY'],
            "bug_issue_open_time_mid": w['BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY'],
            "pr_open_time_avg": w['PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY'],
            "pr_open_time_mid": w['PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY']
        }
        decrease_decay_dict = {
            "comment_frequency": w['COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_COMMUNITY'],
            "code_review_count": w['CODE_REVIEW_MULTIPLE_THRESHOLD_COMMUNITY']
        }
    if level == "repo":
        increment_decay_dict = {
            "issue_first_reponse_avg": w['ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY'],
            "issue_first_reponse_mid": w['ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY'],
            "bug_issue_open_time_avg": w['BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY'],
            "bug_issue_open_time_mid": w['BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY'],
            "pr_open_time_avg": w['PR_OPEN_TIME_THRESHOLD_COMMUNITY'],
            "pr_open_time_mid": w['PR_OPEN_TIME_THRESHOLD_COMMUNITY']
        }
        decrease_decay_dict = {
            "comment_frequency": w['COMMENT_FREQUENCY_THRESHOLD_COMMUNITY'],
            "code_review_count": w['CODE_REVIEW_THRESHOLD_COMMUNITY']
        }
    for key, value in increment_decay_dict.items():
        if item[key] == None and last_data.get(key) != None:
            days = pendulum.parse(item['grimoire_creation_date']).diff(pendulum.parse(last_data[key][1])).days
            decay_item[key] = round(increment_decay(last_data[key][0], value, days), 4)
    for key, value in decrease_decay_dict.items():
        if item[key] == None and last_data.get(key) != None:
            days = pendulum.parse(item['grimoire_creation_date']).diff(pendulum.parse(last_data[key][1])).days
            decay_item[key] = round(decrease_decay(last_data[key][0], value, days), 4)
    return decay_item

def activity_decay(item, last_data, level="repo", w={}):
    if last_data == None:
        return item
    decay_item = item.copy()
    decrease_decay_dict = {}
    if level == "community" or level == "project":
        decrease_decay_dict = {
            "comment_frequency": w['COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY'],
            "code_review_count": w['CODE_REVIEW_COUNT_MULTIPLE_THRESHOLD_ACTIVITY']
        }
    if level == "repo":
        decrease_decay_dict = {
            "comment_frequency": w['COMMIT_FREQUENCY_THRESHOLD_ACTIVITY'],
            "code_review_count": w['CODE_REVIEW_COUNT_THRESHOLD_ACTIVITY']
        }
    for key, value in decrease_decay_dict.items():
        if item[key] == None and last_data.get(key) != None:
            days = pendulum.parse(item['grimoire_creation_date']).diff(pendulum.parse(last_data[key][1])).days
            decay_item[key] = round(decrease_decay(last_data[key][0], value, days), 4)
    return decay_item

def code_quality_decay(item, last_data, level="repo", w={}):
    if last_data == None:
        return item
    decay_item = item.copy()
    decrease_decay_dict = {}
    if level == "community" or level == "project":
        decrease_decay_dict = {
            "code_merge_ratio": w['CODE_MERGE_RATIO_MULTIPLE_THRESHOLD_CODE'],
            "code_review_ratio": w['CODE_REVIEW_RATIO_MULTIPLE_THRESHOLD_CODE'],
            "pr_issue_linked_ratio": w['PR_ISSUE_LINKED_MULTIPLE_THRESHOLD_CODE'],
            "git_pr_linked_ratio": w['COMMIT_PR_LINKED_RATIO_MULTIPLE_THRESHOLD_CODE']
        }
    if level == "repo":
        decrease_decay_dict = {
            "code_merge_ratio": w['CODE_MERGE_RATIO_THRESHOLD_CODE'],
            "code_review_ratio": w['CODE_REVIEW_RATIO_THRESHOLD_CODE'],
            "pr_issue_linked_ratio": w['PR_ISSUE_LINKED_THRESHOLD_CODE'],
            "git_pr_linked_ratio": w['COMMIT_PR_LINKED_RATIO_THRESHOLD_CODE']
        }
    for key, value in decrease_decay_dict.items():
        if item[key] == None and last_data.get(key) != None:
            days = pendulum.parse(item['grimoire_creation_date']).diff(pendulum.parse(last_data[key][1])).days
            decay_item[key] = round(decrease_decay(last_data[key][0], value, days), 4)
    return decay_item
