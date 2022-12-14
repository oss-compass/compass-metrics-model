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

######################### ACTIVITY #############################################

CONTRIBUTOR_COUNT_WEIGHT_ACTIVITY = 0.18009
COMMIT_FREQUENCY_WEIGHT_ACTIVITY = 0.18009
UPDATED_SINCE_WEIGHT_ACTIVITY = -0.12742
ORG_COUNT_WEIGHT_ACTIVITY = 0.11501
CREATED_SINCE_WEIGHT_ACTIVITY = 0.07768
COMMENT_FREQUENCY_WEIGHT_ACTIVITY = 0.07768
CODE_REVIEW_COUNT_WEIGHT_ACTIVITY = 0.04919
UPDATED_ISSUES_WEIGHT_ACTIVITY = 0.04919
RECENT_RELEASES_WEIGHT_ACTIVITY = 0.03177
MAINTAINER_COUT_WEIGHT_ACTIVITY = 0.2090
MEETING_WEIGHT_ACTIVITY = 0.02090
MEETING_ATTENDEE_COUNT_WEIGHT_ACTIVITY = 0.02090

CONTRIBUTOR_COUNT_THRESHOLD_ACTIVITY = 2000
COMMIT_FREQUENCY_THRESHOLD_ACTIVITY = 1000
UPDATED_SINCE_THRESHOLD_ACTIVITY = 0.25
ORG_COUNT_THRESHOLD_ACTIVITY = 10
CREATED_SINCE_THRESHOLD_ACTIVITY = 120
COMMENT_FREQUENCY_THRESHOLD_ACTIVITY = 5
CODE_REVIEW_COUNT_THRESHOLD_ACTIVITY = 8
UPDATED_ISSUES_THRESHOLD_ACTIVITY = 2500
RECENT_RELEASES_THRESHOLD_ACTIVITY = 12
MAINTAINER_COUT_THRESHOLD_ACTIVITY = 100
MEETING_THRESHOLD_ACTIVITY = 100
MEETING_ATTENDEE_COUNT_THRESHOLD_ACTIVITY = 10

CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_ACTIVITY = 2200
COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY = 1000
UPDATED_SINCE_MULTIPLE_THRESHOLD_ACTIVITY = 0.25
ORG_COUNT_MULTIPLE_THRESHOLD_ACTIVITY = 30
CREATED_SINCE_MULTIPLE_THRESHOLD_ACTIVITY = 240
COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY = 5
CODE_REVIEW_COUNT_MULTIPLE_THRESHOLD_ACTIVITY = 8
UPDATED_ISSUES_MULTIPLE_THRESHOLD_ACTIVITY = 2500
RECENT_RELEASES_MULTIPLE_THRESHOLD_ACTIVITY = 12

########################## COMMUNITY ########################################

ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY = -0.1437
BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY = -0.1288
COMMENT_FREQUENCY_WEIGHT_COMMUNITY = 0.1022
UPDATED_ISSUES_WEIGHT_COMMUNITY = 0.1972
PR_OPEN_TIME_WEIGHT_COMMUNITY = -0.1288
CODE_REVIEW_WEIGHT_COMMUNITY = 0.1022
CLOSED_PRS_WEIGHT_COMMUNITY = 0.1972

ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY = 15
BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY = 60
COMMENT_FREQUENCY_THRESHOLD_COMMUNITY = 5
UPDATED_ISSUES_THRESHOLD_COMMUNITY = 2500
PR_OPEN_TIME_THRESHOLD_COMMUNITY = 30
CODE_REVIEW_THRESHOLD_COMMUNITY = 8
CLOSED_PRS_THRESHOLD_COMMUNITY = 4500

ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY = 15
BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY = 60
COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_COMMUNITY = 5
UPDATED_ISSUES_MULTIPLE_THRESHOLD_COMMUNITY = 2500
PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY = 30
CODE_REVIEW_MULTIPLE_THRESHOLD_COMMUNITY = 8
CLOSED_PRS_MULTIPLE_THRESHOLD_COMMUNITY = 60000

########################## CODE ########################################

CONTRIBUTOR_COUNT_WEIGHT_CODE = 0.1999
COMMIT_FREQUENCY_WEIGHT_CODE = 0.1636
IS_MAINTAINED_WEIGHT_CODE = 0.1385
COMMIT_PR_LINKED_RATIO_WEIGHT_CODE = 0.1261
PR_ISSUE_LINKED_WEIGHT_CODE = 0.1132
CODE_REVIEW_RATIO_WEIGHT_CODE = 0.1011
CODE_MERGE_RATIO_WEIGHT_CODE = 0.1011
LOC_FREQUENCY_WEIGHT_CODE = 0.0564

CONTRIBUTOR_COUNT_THRESHOLD_CODE = 1000
COMMIT_FREQUENCY_THRESHOLD_CODE = 1000
IS_MAINTAINED_THRESHOLD_CODE = 1
COMMIT_PR_LINKED_RATIO_THRESHOLD_CODE = 1
PR_ISSUE_LINKED_THRESHOLD_CODE = 0.2
CODE_REVIEW_RATIO_THRESHOLD_CODE = 1
CODE_MERGE_RATIO_THRESHOLD_CODE = 1
LOC_FREQUENCY_THRESHOLD_CODE = 300000

CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_CODE = 1000
COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_CODE = 1000
IS_MAINTAINED_MULTIPLE_THRESHOLD_CODE = 1
COMMIT_PR_LINKED_RATIO_MULTIPLE_THRESHOLD_CODE = 1
PR_ISSUE_LINKED_MULTIPLE_THRESHOLD_CODE = 0.2
CODE_REVIEW_RATIO_MULTIPLE_THRESHOLD_CODE = 1
CODE_MERGE_RATIO_MULTIPLE_THRESHOLD_CODE = 1
LOC_FREQUENCY_MULTIPLE_THRESHOLD_CODE = 300000

########################## ORG_ACTIVITY ########################################

CONTRIBUTOR_COUNT_WEIGHT_ORG_ACTIVITY = 0.2581
COMMIT_FREQUENCY_WEIGHT_ORG_ACTIVITY = 0.2581
ORG_COUNT_WEIGHT_ORG_ACTIVITY = 0.3226
CONTRIBUTION_LAST_WEIGHT_ORG_ACTIVITY = 0.1613

CONTRIBUTOR_COUNT_THRESHOLD_ORG_ACTIVITY = 300
COMMIT_FREQUENCY_THRESHOLD_ORG_ACTIVITY = 800
ORG_COUNT_THRESHOLD_ORG_ACTIVITY = 30
CONTRIBUTION_LAST_THRESHOLD_ORG_ACTIVITY = 200

CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_ORG_ACTIVITY = 350
COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ORG_ACTIVITY = 1000
ORG_COUNT_MULTIPLE_THRESHOLD_ORG_ACTIVITY = 30
CONTRIBUTION_LAST_MULTIPLE_THRESHOLD_ORG_ACTIVITY = 400

MIN_ACTIVITY_SCORE = -0.23786
MAX_ACTIVITY_SCORE = 1.23786
MIN_COMMUNITY_SCORE = -2.0319
MAX_COMMUNITY_SCORE = 3.03189

DECAY_COEFFICIENT = 0.001

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

def get_activity_score(item, level="repo"):
    param_dict = {}
    if level == "community" or level == "project":
        param_dict = {
            "contributor_count": [CONTRIBUTOR_COUNT_WEIGHT_ACTIVITY, CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_ACTIVITY],
            "commit_frequency": [COMMIT_FREQUENCY_WEIGHT_ACTIVITY, COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY],
            "updated_since": [UPDATED_SINCE_WEIGHT_ACTIVITY, UPDATED_SINCE_MULTIPLE_THRESHOLD_ACTIVITY],
            "org_count": [ORG_COUNT_WEIGHT_ACTIVITY, ORG_COUNT_MULTIPLE_THRESHOLD_ACTIVITY],
            "created_since": [CREATED_SINCE_WEIGHT_ACTIVITY, CREATED_SINCE_MULTIPLE_THRESHOLD_ACTIVITY],
            "comment_frequency": [COMMENT_FREQUENCY_WEIGHT_ACTIVITY, COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY],
            "code_review_count": [CODE_REVIEW_COUNT_WEIGHT_ACTIVITY, CODE_REVIEW_COUNT_MULTIPLE_THRESHOLD_ACTIVITY],
            "updated_issues_count": [UPDATED_ISSUES_WEIGHT_ACTIVITY, UPDATED_ISSUES_MULTIPLE_THRESHOLD_ACTIVITY],
            "recent_releases_count": [RECENT_RELEASES_WEIGHT_ACTIVITY, RECENT_RELEASES_MULTIPLE_THRESHOLD_ACTIVITY]
        }
    if level == "repo":
        param_dict = {
            "contributor_count":[CONTRIBUTOR_COUNT_WEIGHT_ACTIVITY, CONTRIBUTOR_COUNT_THRESHOLD_ACTIVITY],
            "commit_frequency":[COMMIT_FREQUENCY_WEIGHT_ACTIVITY, COMMIT_FREQUENCY_THRESHOLD_ACTIVITY],
            "updated_since":[UPDATED_SINCE_WEIGHT_ACTIVITY, UPDATED_SINCE_THRESHOLD_ACTIVITY],
            "org_count":[ORG_COUNT_WEIGHT_ACTIVITY, ORG_COUNT_THRESHOLD_ACTIVITY],
            "created_since":[CREATED_SINCE_WEIGHT_ACTIVITY, CREATED_SINCE_THRESHOLD_ACTIVITY],
            "comment_frequency":[COMMENT_FREQUENCY_WEIGHT_ACTIVITY, COMMENT_FREQUENCY_THRESHOLD_ACTIVITY],
            "code_review_count":[CODE_REVIEW_COUNT_WEIGHT_ACTIVITY, CODE_REVIEW_COUNT_THRESHOLD_ACTIVITY],
            "updated_issues_count":[UPDATED_ISSUES_WEIGHT_ACTIVITY, UPDATED_ISSUES_THRESHOLD_ACTIVITY],
            "recent_releases_count":[RECENT_RELEASES_WEIGHT_ACTIVITY, RECENT_RELEASES_THRESHOLD_ACTIVITY]
        }
    score = get_score_ahp(item, param_dict)
    return normalize(score, MIN_ACTIVITY_SCORE, MAX_ACTIVITY_SCORE)

def community_support(item, level="repo"):
    param_dict = {}
    if level == "community" or level == "project":
        param_dict = {
            "issue_first_reponse_avg": [ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY * 0.5, ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY],
            "issue_first_reponse_mid": [ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY * 0.5, ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY],
            "bug_issue_open_time_avg": [BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY * 0.5, BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY],
            "bug_issue_open_time_mid": [BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY * 0.5, BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY],
            "comment_frequency": [COMMENT_FREQUENCY_WEIGHT_COMMUNITY, COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_COMMUNITY],
            "updated_issues_count": [UPDATED_ISSUES_WEIGHT_COMMUNITY, UPDATED_ISSUES_MULTIPLE_THRESHOLD_COMMUNITY],
            "pr_open_time_avg": [PR_OPEN_TIME_WEIGHT_COMMUNITY * 0.5, PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY],
            "pr_open_time_mid": [PR_OPEN_TIME_WEIGHT_COMMUNITY * 0.5, PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY],
            "code_review_count": [CODE_REVIEW_WEIGHT_COMMUNITY, CODE_REVIEW_MULTIPLE_THRESHOLD_COMMUNITY],
            "closed_prs_count": [CLOSED_PRS_WEIGHT_COMMUNITY, CLOSED_PRS_MULTIPLE_THRESHOLD_COMMUNITY]
        }
    if level == "repo":
        param_dict = {
            "issue_first_reponse_avg":[ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY*0.5, ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY],
            "issue_first_reponse_mid":[ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY*0.5, ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY],
            "bug_issue_open_time_avg":[BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY*0.5, BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY],
            "bug_issue_open_time_mid":[BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY*0.5, BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY],
            "comment_frequency":[COMMENT_FREQUENCY_WEIGHT_COMMUNITY, COMMENT_FREQUENCY_THRESHOLD_COMMUNITY],
            "updated_issues_count":[UPDATED_ISSUES_WEIGHT_COMMUNITY, UPDATED_ISSUES_THRESHOLD_COMMUNITY],
            "pr_open_time_avg":[PR_OPEN_TIME_WEIGHT_COMMUNITY*0.5, PR_OPEN_TIME_THRESHOLD_COMMUNITY],
            "pr_open_time_mid":[PR_OPEN_TIME_WEIGHT_COMMUNITY*0.5, PR_OPEN_TIME_THRESHOLD_COMMUNITY],
            "code_review_count":[CODE_REVIEW_WEIGHT_COMMUNITY, CODE_REVIEW_THRESHOLD_COMMUNITY],
            "closed_prs_count":[CLOSED_PRS_WEIGHT_COMMUNITY, CLOSED_PRS_THRESHOLD_COMMUNITY]
        }
    score = get_score_ahp(item, param_dict)
    return normalize(score, MIN_COMMUNITY_SCORE, MAX_COMMUNITY_SCORE)

def code_quality_guarantee(item, level="repo"):
    param_dict = {}
    if level == "community" or level == "project":
        param_dict = {
            "contributor_count": [CONTRIBUTOR_COUNT_WEIGHT_CODE, CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_CODE],
            "commit_frequency": [COMMIT_FREQUENCY_WEIGHT_CODE, COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_CODE],
            "is_maintained": [IS_MAINTAINED_WEIGHT_CODE, IS_MAINTAINED_MULTIPLE_THRESHOLD_CODE],
            "git_pr_linked_ratio": [COMMIT_PR_LINKED_RATIO_WEIGHT_CODE, COMMIT_PR_LINKED_RATIO_MULTIPLE_THRESHOLD_CODE],
            "pr_issue_linked_ratio": [PR_ISSUE_LINKED_WEIGHT_CODE, PR_ISSUE_LINKED_MULTIPLE_THRESHOLD_CODE],
            "code_review_ratio": [CODE_REVIEW_RATIO_WEIGHT_CODE, CODE_REVIEW_RATIO_MULTIPLE_THRESHOLD_CODE],
            "code_merge_ratio": [CODE_MERGE_RATIO_WEIGHT_CODE, CODE_MERGE_RATIO_MULTIPLE_THRESHOLD_CODE],
            "LOC_frequency": [LOC_FREQUENCY_WEIGHT_CODE, LOC_FREQUENCY_MULTIPLE_THRESHOLD_CODE],
        }
    if level == "repo":
        param_dict = {
            "contributor_count":[CONTRIBUTOR_COUNT_WEIGHT_CODE, CONTRIBUTOR_COUNT_THRESHOLD_CODE],
            "commit_frequency":[COMMIT_FREQUENCY_WEIGHT_CODE, COMMIT_FREQUENCY_THRESHOLD_CODE],
            "is_maintained":[IS_MAINTAINED_WEIGHT_CODE, IS_MAINTAINED_THRESHOLD_CODE],
            "git_pr_linked_ratio":[COMMIT_PR_LINKED_RATIO_WEIGHT_CODE, COMMIT_PR_LINKED_RATIO_THRESHOLD_CODE],
            "pr_issue_linked_ratio":[PR_ISSUE_LINKED_WEIGHT_CODE, PR_ISSUE_LINKED_THRESHOLD_CODE],
            "code_review_ratio":[CODE_REVIEW_RATIO_WEIGHT_CODE, CODE_REVIEW_RATIO_THRESHOLD_CODE],
            "code_merge_ratio":[CODE_MERGE_RATIO_WEIGHT_CODE, CODE_MERGE_RATIO_THRESHOLD_CODE],
            "LOC_frequency":[LOC_FREQUENCY_WEIGHT_CODE, LOC_FREQUENCY_THRESHOLD_CODE],
        }
    return get_score_ahp(item, param_dict)

def organizations_activity(item, level="repo"):
    param_dict = {}
    if level == "community" or level == "project":
        param_dict = {
            "contributor_count":[CONTRIBUTOR_COUNT_WEIGHT_ORG_ACTIVITY, CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_ORG_ACTIVITY],
            "commit_frequency":[COMMIT_FREQUENCY_WEIGHT_ORG_ACTIVITY, COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ORG_ACTIVITY],
            "org_count":[ORG_COUNT_WEIGHT_ORG_ACTIVITY, ORG_COUNT_THRESHOLD_ORG_ACTIVITY],
            "contribution_last":[CONTRIBUTION_LAST_WEIGHT_ORG_ACTIVITY, CONTRIBUTION_LAST_MULTIPLE_THRESHOLD_ORG_ACTIVITY],
        }
    if level == "repo":
        param_dict = {
            "contributor_count":[CONTRIBUTOR_COUNT_WEIGHT_ORG_ACTIVITY, CONTRIBUTOR_COUNT_THRESHOLD_ORG_ACTIVITY],
            "commit_frequency":[COMMIT_FREQUENCY_WEIGHT_ORG_ACTIVITY, COMMIT_FREQUENCY_THRESHOLD_ORG_ACTIVITY],
            "org_count":[ORG_COUNT_WEIGHT_ORG_ACTIVITY, ORG_COUNT_THRESHOLD_ORG_ACTIVITY],
            "contribution_last":[CONTRIBUTION_LAST_WEIGHT_ORG_ACTIVITY, CONTRIBUTION_LAST_THRESHOLD_ORG_ACTIVITY],
        }
    return get_score_ahp(item, param_dict)

def increment_decay(last_data, threshold, days):
    return min(last_data + DECAY_COEFFICIENT * threshold * days, threshold)

def decrease_decay(last_data, threshold, days):
    return max(last_data - DECAY_COEFFICIENT * threshold * days, 0)

def community_decay(item, last_data, level="repo"):
    if last_data == None:
        return item
    decay_item = item.copy()
    increment_decay_dict = {}
    decrease_decay_dict = {}
    if level == "community" or level == "project":
        increment_decay_dict = {
            "issue_first_reponse_avg": ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY,
            "issue_first_reponse_mid": ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY,
            "bug_issue_open_time_avg": BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY,
            "bug_issue_open_time_mid": BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY,
            "pr_open_time_avg": PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY,
            "pr_open_time_mid": PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY
        }
        decrease_decay_dict = {
            "comment_frequency": COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_COMMUNITY,
            "code_review_count": CODE_REVIEW_MULTIPLE_THRESHOLD_COMMUNITY
        }
    if level == "repo":
        increment_decay_dict = {
            "issue_first_reponse_avg":ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY,
            "issue_first_reponse_mid":ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY,
            "bug_issue_open_time_avg":BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY,
            "bug_issue_open_time_mid":BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY,
            "pr_open_time_avg":PR_OPEN_TIME_THRESHOLD_COMMUNITY,
            "pr_open_time_mid":PR_OPEN_TIME_THRESHOLD_COMMUNITY
            }
        decrease_decay_dict = {
            "comment_frequency":COMMENT_FREQUENCY_THRESHOLD_COMMUNITY,
            "code_review_count":CODE_REVIEW_THRESHOLD_COMMUNITY
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

def activity_decay(item, last_data, level="repo"):
    if last_data == None:
        return item
    decay_item = item.copy()
    increment_decay_dict = {}
    if level == "community" or level == "project":
        increment_decay_dict = {
            "comment_frequency": COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY,
            "code_review_count": CODE_REVIEW_COUNT_MULTIPLE_THRESHOLD_ACTIVITY
        }
    if level == "repo":
        increment_decay_dict = {
            "comment_frequency":COMMIT_FREQUENCY_THRESHOLD_ACTIVITY,
            "code_review_count":CODE_REVIEW_COUNT_THRESHOLD_ACTIVITY
            }
    for key, value in increment_decay_dict.items():
        if item[key] == None and last_data.get(key) != None:
            days = pendulum.parse(item['grimoire_creation_date']).diff(pendulum.parse(last_data[key][1])).days
            decay_item[key] = round(increment_decay(last_data[key][0], value, days), 4)        
    return decay_item

def code_quality_decay(item, last_data, level="repo"):
    if last_data == None:
        return item
    decay_item = item.copy()
    increment_decay_dict = {}
    if level == "community" or level == "project":
        increment_decay_dict = {
            "code_merge_ratio": CODE_MERGE_RATIO_MULTIPLE_THRESHOLD_CODE,
            "code_review_ratio": CODE_REVIEW_RATIO_MULTIPLE_THRESHOLD_CODE,
            "pr_issue_linked_ratio": PR_ISSUE_LINKED_MULTIPLE_THRESHOLD_CODE,
            "git_pr_linked_ratio": COMMIT_PR_LINKED_RATIO_MULTIPLE_THRESHOLD_CODE
        }
    if level == "repo":
        increment_decay_dict = {
            "code_merge_ratio": CODE_MERGE_RATIO_THRESHOLD_CODE,
            "code_review_ratio":CODE_REVIEW_RATIO_THRESHOLD_CODE,
            "pr_issue_linked_ratio":PR_ISSUE_LINKED_THRESHOLD_CODE,
            "git_pr_linked_ratio":COMMIT_PR_LINKED_RATIO_THRESHOLD_CODE
            }
    for key, value in increment_decay_dict.items():
        if item[key] == None and last_data.get(key) != None:
            days = pendulum.parse(item['grimoire_creation_date']).diff(pendulum.parse(last_data[key][1])).days
            decay_item[key] = round(increment_decay(last_data[key][0], value, days), 4)        
    return decay_item
