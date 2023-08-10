from compass_model.base_metrics_model import BaseMetricsModel

CONTRIBUTOR_COUNT_WEIGHT_ACTIVITY = 0.18009
COMMIT_FREQUENCY_WEIGHT_ACTIVITY = 0.18009
UPDATED_SINCE_WEIGHT_ACTIVITY = -0.12742
ORG_COUNT_WEIGHT_ACTIVITY = 0.11501
# CREATED_SINCE_WEIGHT_ACTIVITY = 0.07768
COMMENT_FREQUENCY_WEIGHT_ACTIVITY = 0.07768
CODE_REVIEW_COUNT_WEIGHT_ACTIVITY = 0.04919
UPDATED_ISSUES_WEIGHT_ACTIVITY = 0.04919
RECENT_RELEASES_WEIGHT_ACTIVITY = 0.03177
MAINTAINER_COUT_WEIGHT_ACTIVITY = 0.2090
MEETING_WEIGHT_ACTIVITY = 0.02090
MEETING_ATTENDEE_COUNT_WEIGHT_ACTIVITY = 0.02090


class ActivityMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file):
        model_name = 'Activity'
        metrics_weights_thresholds = {
            "contributor_count": {
                "weight": CONTRIBUTOR_COUNT_WEIGHT_ACTIVITY,
                "threshold": None
            },
            "commit_frequency": {
                "weight": COMMIT_FREQUENCY_WEIGHT_ACTIVITY,
                "threshold": None
            },
            "updated_since": {
                "weight": UPDATED_SINCE_WEIGHT_ACTIVITY,
                "threshold": None
            },
            "org_count": {
                "weight": ORG_COUNT_WEIGHT_ACTIVITY,
                "threshold": None
            },
            # "created_since": {
            #     "weight": CREATED_SINCE_WEIGHT_ACTIVITY,
            #     "threshold": None
            # },
            "comment_frequency": {
                "weight": COMMENT_FREQUENCY_WEIGHT_ACTIVITY,
                "threshold": None
            },
            "code_review_count": {
                "weight": CODE_REVIEW_COUNT_WEIGHT_ACTIVITY,
                "threshold": None
            },
            "updated_issues_count": {
                "weight": UPDATED_ISSUES_WEIGHT_ACTIVITY,
                "threshold": None
            },
            "recent_releases_count": {
                "weight": RECENT_RELEASES_WEIGHT_ACTIVITY,
                "threshold": None
            }
        }
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)
