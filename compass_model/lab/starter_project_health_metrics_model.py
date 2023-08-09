from compass_model.base_metrics_model import BaseMetricsModel

PR_TIME_TO_FIRST_RESPONSE_WEIGHT_STARTER_PROJECT = -0.2
CHANGE_REQUEST_CLOSURE_RATIO_WEIGHT_STARTER_PROJECT = 0.1
CHANGE_REQUEST_CLOSURE_RATIO_RECENTLY_PERIOD_WEIGHT_STARTER_PROJECT = 0.1
PR_OPEN_TIME_WEIGHT_STARTER_PROJECT = -0.2
BUS_FACTOR_WEIGHT_STARTER_PROJECT = 0.2
RELEASE_FREQUENCY_WEIGHT_STARTER_PROJECT = 0.2

PR_TIME_TO_FIRST_RESPONSE_THRESHOLD_STARTER_PROJECT = 15
CHANGE_REQUEST_CLOSURE_RATIO_THRESHOLD_STARTER_PROJECT = 1
CHANGE_REQUEST_CLOSURE_RATIO_RECENTLY_PERIOD_THRESHOLD_STARTER_PROJECT = 1
PR_OPEN_TIME_THRESHOLD_STARTER_PROJECT = 30
BUS_FACTOR_THRESHOLD_STARTER_PROJECT = 5
RELEASE_FREQUENCY_THRESHOLD_STARTER_PROJECT = 12

PR_TIME_TO_FIRST_RESPONSE_MULTIPLE_THRESHOLD_STARTER_PROJECT = 15
CHANGE_REQUEST_CLOSURE_RATIO_MULTIPLE_THRESHOLD_STARTER_PROJECT = 1
CHANGE_REQUEST_CLOSURE_RATIO_RECENTLY_PERIOD_MULTIPLE_THRESHOLD_STARTER_PROJECT = 1
PR_OPEN_TIME_MULTIPLE_THRESHOLD_STARTER_PROJECT = 30
BUS_FACTOR_MULTIPLE_THRESHOLD_STARTER_PROJECT = 5
RELEASE_FREQUENCY_MULTIPLE_THRESHOLD_STARTER_PROJECT = 12


class StarterProjectHealthMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file):
        model_name = 'Starter Project Health'
        metrics_weights_thresholds = {}
        if level == "repo":
            metrics_weights_thresholds = {
                "pr_time_to_first_response": {
                    "weight": PR_TIME_TO_FIRST_RESPONSE_WEIGHT_STARTER_PROJECT,
                    "threshold": PR_TIME_TO_FIRST_RESPONSE_THRESHOLD_STARTER_PROJECT
                },
                "change_request_closure_ratio": {
                    "weight": CHANGE_REQUEST_CLOSURE_RATIO_WEIGHT_STARTER_PROJECT,
                    "threshold": CHANGE_REQUEST_CLOSURE_RATIO_THRESHOLD_STARTER_PROJECT
                },
                "change_request_closure_ratio_recently_period": {
                    "weight": CHANGE_REQUEST_CLOSURE_RATIO_RECENTLY_PERIOD_WEIGHT_STARTER_PROJECT,
                    "threshold": CHANGE_REQUEST_CLOSURE_RATIO_RECENTLY_PERIOD_THRESHOLD_STARTER_PROJECT
                },
                "pr_open_time": {
                    "weight": PR_OPEN_TIME_WEIGHT_STARTER_PROJECT,
                    "threshold": PR_OPEN_TIME_THRESHOLD_STARTER_PROJECT
                },
                "bus_factor": {
                    "weight": BUS_FACTOR_WEIGHT_STARTER_PROJECT,
                    "threshold": BUS_FACTOR_THRESHOLD_STARTER_PROJECT
                },
                "recent_releases_count": {
                    "weight": RELEASE_FREQUENCY_WEIGHT_STARTER_PROJECT,
                    "threshold": RELEASE_FREQUENCY_THRESHOLD_STARTER_PROJECT
                } 
            }
        if level == "community":
            metrics_weights_thresholds = {
                "pr_time_to_first_response": {
                    "weight": PR_TIME_TO_FIRST_RESPONSE_WEIGHT_STARTER_PROJECT,
                    "threshold": PR_TIME_TO_FIRST_RESPONSE_MULTIPLE_THRESHOLD_STARTER_PROJECT
                },
                "change_request_closure_ratio": {
                    "weight": CHANGE_REQUEST_CLOSURE_RATIO_WEIGHT_STARTER_PROJECT,
                    "threshold": CHANGE_REQUEST_CLOSURE_RATIO_MULTIPLE_THRESHOLD_STARTER_PROJECT
                },
                "change_request_closure_ratio_recently_period": {
                    "weight": CHANGE_REQUEST_CLOSURE_RATIO_RECENTLY_PERIOD_WEIGHT_STARTER_PROJECT,
                    "threshold": CHANGE_REQUEST_CLOSURE_RATIO_RECENTLY_PERIOD_MULTIPLE_THRESHOLD_STARTER_PROJECT
                },
                "pr_open_time": {
                    "weight": PR_OPEN_TIME_WEIGHT_STARTER_PROJECT,
                    "threshold": PR_OPEN_TIME_MULTIPLE_THRESHOLD_STARTER_PROJECT
                },
                "bus_factor": {
                    "weight": BUS_FACTOR_WEIGHT_STARTER_PROJECT,
                    "threshold": BUS_FACTOR_MULTIPLE_THRESHOLD_STARTER_PROJECT
                },
                "recent_releases_count": {
                    "weight": RELEASE_FREQUENCY_WEIGHT_STARTER_PROJECT,
                    "threshold": RELEASE_FREQUENCY_MULTIPLE_THRESHOLD_STARTER_PROJECT
                } 
            }
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)
