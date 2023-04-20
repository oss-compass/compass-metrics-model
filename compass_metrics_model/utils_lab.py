import pendulum
from .utils import (increment_decay, decrease_decay, get_score_ahp, normalize)

######################### Starter Project Health #############################################

PR_TIME_TO_FIRST_RESPONSE_WEIGHT_STARTER_PROJECT = -0.2
CHANGE_REQUEST_CLOSURE_RATIO_WEIGHT_STARTER_PROJECT = 0.2
PR_TIME_TO_CLOSE_WEIGHT_STARTER_PROJECT = -0.2
BUS_FACTOR_WEIGHT_STARTER_PROJECT = 0.2
RELEASE_FREQUENCY_WEIGHT_STARTER_PROJECT = 0.2

PR_TIME_TO_FIRST_RESPONSE_THRESHOLD_STARTER_PROJECT = 15
CHANGE_REQUEST_CLOSURE_RATIO_THRESHOLD_STARTER_PROJECT = 1
PR_TIME_TO_CLOSE_THRESHOLD_STARTER_PROJECT = 30
BUS_FACTOR_THRESHOLD_STARTER_PROJECT = 5
RELEASE_FREQUENCY_THRESHOLD_STARTER_PROJECT = 12

PR_TIME_TO_FIRST_RESPONSE_MULTIPLE_THRESHOLD_STARTER_PROJECT = 15
CHANGE_REQUEST_CLOSURE_RATIO_MULTIPLE_THRESHOLD_STARTER_PROJECT = 1
PR_TIME_TO_CLOSE_MULTIPLE_THRESHOLD_STARTER_PROJECT = 30
BUS_FACTOR_MULTIPLE_THRESHOLD_STARTER_PROJECT = 5
RELEASE_FREQUENCY_MULTIPLE_THRESHOLD_STARTER_PROJECT = 12

MIN_STARTER_PROJECT_SCORE = -2.0
MAX_STARTER_PROJECT_SCORE = 3.0

def starter_project_health(item, level="repo"):
    param_dict = {}
    if level == "community" or level == "project":
        param_dict = {
            "pr_time_to_first_response_avg": [PR_TIME_TO_FIRST_RESPONSE_WEIGHT_STARTER_PROJECT * 0.5,
                                              PR_TIME_TO_FIRST_RESPONSE_MULTIPLE_THRESHOLD_STARTER_PROJECT],
            "pr_time_to_first_response_mid": [PR_TIME_TO_FIRST_RESPONSE_WEIGHT_STARTER_PROJECT * 0.5,
                                              PR_TIME_TO_FIRST_RESPONSE_MULTIPLE_THRESHOLD_STARTER_PROJECT],
            "change_request_closure_ratio_all_period": [
                CHANGE_REQUEST_CLOSURE_RATIO_WEIGHT_STARTER_PROJECT * 0.5,
                CHANGE_REQUEST_CLOSURE_RATIO_MULTIPLE_THRESHOLD_STARTER_PROJECT],
            "change_request_closure_ratio_same_period": [
                CHANGE_REQUEST_CLOSURE_RATIO_WEIGHT_STARTER_PROJECT * 0.5,
                CHANGE_REQUEST_CLOSURE_RATIO_MULTIPLE_THRESHOLD_STARTER_PROJECT],
            "pr_time_to_close_avg": [PR_TIME_TO_CLOSE_WEIGHT_STARTER_PROJECT * 0.5,
                                     PR_TIME_TO_CLOSE_MULTIPLE_THRESHOLD_STARTER_PROJECT],
            "pr_time_to_close_mid": [PR_TIME_TO_CLOSE_WEIGHT_STARTER_PROJECT * 0.5,
                                     PR_TIME_TO_CLOSE_MULTIPLE_THRESHOLD_STARTER_PROJECT],
            "bus_factor": [BUS_FACTOR_WEIGHT_STARTER_PROJECT, BUS_FACTOR_MULTIPLE_THRESHOLD_STARTER_PROJECT],
            "release_frequency": [RELEASE_FREQUENCY_WEIGHT_STARTER_PROJECT,
                                  RELEASE_FREQUENCY_MULTIPLE_THRESHOLD_STARTER_PROJECT]
        }
    if level == "repo":
        param_dict = {
            "pr_time_to_first_response_avg": [PR_TIME_TO_FIRST_RESPONSE_WEIGHT_STARTER_PROJECT * 0.5,
                                              PR_TIME_TO_FIRST_RESPONSE_THRESHOLD_STARTER_PROJECT],
            "pr_time_to_first_response_mid": [PR_TIME_TO_FIRST_RESPONSE_WEIGHT_STARTER_PROJECT * 0.5,
                                              PR_TIME_TO_FIRST_RESPONSE_THRESHOLD_STARTER_PROJECT],
            "change_request_closure_ratio_all_period": [
                CHANGE_REQUEST_CLOSURE_RATIO_WEIGHT_STARTER_PROJECT * 0.5,
                CHANGE_REQUEST_CLOSURE_RATIO_THRESHOLD_STARTER_PROJECT],
            "change_request_closure_ratio_same_period": [CHANGE_REQUEST_CLOSURE_RATIO_WEIGHT_STARTER_PROJECT * 0.5,
                                             CHANGE_REQUEST_CLOSURE_RATIO_THRESHOLD_STARTER_PROJECT],
            "pr_time_to_close_avg": [PR_TIME_TO_CLOSE_WEIGHT_STARTER_PROJECT * 0.5,
                                     PR_TIME_TO_CLOSE_THRESHOLD_STARTER_PROJECT],
            "pr_time_to_close_mid": [PR_TIME_TO_CLOSE_WEIGHT_STARTER_PROJECT * 0.5,
                                     PR_TIME_TO_CLOSE_THRESHOLD_STARTER_PROJECT],
            "bus_factor": [BUS_FACTOR_WEIGHT_STARTER_PROJECT, BUS_FACTOR_THRESHOLD_STARTER_PROJECT],
            "release_frequency": [RELEASE_FREQUENCY_WEIGHT_STARTER_PROJECT, RELEASE_FREQUENCY_THRESHOLD_STARTER_PROJECT]
        }
    score = get_score_ahp(item, param_dict)
    return normalize(score, MIN_STARTER_PROJECT_SCORE, MAX_STARTER_PROJECT_SCORE)


def starter_project_health_decay(item, last_data, level="repo"):
    if last_data == None:
        return item
    decay_item = item.copy()
    increment_decay_dict = {}
    decrease_decay_dict = {}
    if level == "community" or level == "project":
        increment_decay_dict = {
            "pr_time_to_first_response_avg": PR_TIME_TO_FIRST_RESPONSE_MULTIPLE_THRESHOLD_STARTER_PROJECT,
            "pr_time_to_first_response_mid": PR_TIME_TO_FIRST_RESPONSE_MULTIPLE_THRESHOLD_STARTER_PROJECT,
            "pr_time_to_close_avg": PR_TIME_TO_CLOSE_MULTIPLE_THRESHOLD_STARTER_PROJECT,
            "pr_time_to_close_mid": PR_TIME_TO_CLOSE_MULTIPLE_THRESHOLD_STARTER_PROJECT
        }
        decrease_decay_dict = {
            "change_request_closure_ratio_all_period": CHANGE_REQUEST_CLOSURE_RATIO_MULTIPLE_THRESHOLD_STARTER_PROJECT,
            "change_request_closure_ratio_same_period": CHANGE_REQUEST_CLOSURE_RATIO_MULTIPLE_THRESHOLD_STARTER_PROJECT
        }
    if level == "repo":
        increment_decay_dict = {
            "pr_time_to_first_response_avg": PR_TIME_TO_FIRST_RESPONSE_THRESHOLD_STARTER_PROJECT,
            "pr_time_to_first_response_mid": PR_TIME_TO_FIRST_RESPONSE_THRESHOLD_STARTER_PROJECT,
            "pr_time_to_close_avg": PR_TIME_TO_CLOSE_THRESHOLD_STARTER_PROJECT,
            "pr_time_to_close_mid": PR_TIME_TO_CLOSE_THRESHOLD_STARTER_PROJECT
        }
        decrease_decay_dict = {
            "change_request_closure_ratio_all_period": CHANGE_REQUEST_CLOSURE_RATIO_THRESHOLD_STARTER_PROJECT,
            "change_request_closure_ratio_same_period": CHANGE_REQUEST_CLOSURE_RATIO_THRESHOLD_STARTER_PROJECT
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