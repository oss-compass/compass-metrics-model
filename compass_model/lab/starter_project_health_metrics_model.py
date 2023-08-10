from compass_model.base_metrics_model import BaseMetricsModel

PR_TIME_TO_FIRST_RESPONSE_WEIGHT_STARTER_PROJECT = -0.2
CHANGE_REQUEST_CLOSURE_RATIO_WEIGHT_STARTER_PROJECT = 0.1
CHANGE_REQUEST_CLOSURE_RATIO_RECENTLY_PERIOD_WEIGHT_STARTER_PROJECT = 0.1
PR_OPEN_TIME_WEIGHT_STARTER_PROJECT = -0.2
BUS_FACTOR_WEIGHT_STARTER_PROJECT = 0.2
RELEASE_FREQUENCY_WEIGHT_STARTER_PROJECT = 0.2


class StarterProjectHealthMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file):
        model_name = 'Starter Project Health'
        metrics_weights_thresholds = {
            "pr_time_to_first_response": {
                "weight": PR_TIME_TO_FIRST_RESPONSE_WEIGHT_STARTER_PROJECT,
                "threshold": None
            },
            "change_request_closure_ratio": {
                "weight": CHANGE_REQUEST_CLOSURE_RATIO_WEIGHT_STARTER_PROJECT,
                "threshold": None
            },
            "change_request_closure_ratio_recently_period": {
                "weight": CHANGE_REQUEST_CLOSURE_RATIO_RECENTLY_PERIOD_WEIGHT_STARTER_PROJECT,
                "threshold": None
            },
            "pr_open_time": {
                "weight": PR_OPEN_TIME_WEIGHT_STARTER_PROJECT,
                "threshold": None
            },
            "bus_factor": {
                "weight": BUS_FACTOR_WEIGHT_STARTER_PROJECT,
                "threshold": None
            },
            "recent_releases_count": {
                "weight": RELEASE_FREQUENCY_WEIGHT_STARTER_PROJECT,
                "threshold": None
            } 
        }
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)
