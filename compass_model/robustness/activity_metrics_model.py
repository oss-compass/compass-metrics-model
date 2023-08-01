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

CONTRIBUTOR_COUNT_THRESHOLD_ACTIVITY = 2000
COMMIT_FREQUENCY_THRESHOLD_ACTIVITY = 1000
UPDATED_SINCE_THRESHOLD_ACTIVITY = 0.25
ORG_COUNT_THRESHOLD_ACTIVITY = 10
# CREATED_SINCE_THRESHOLD_ACTIVITY = 120
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
# CREATED_SINCE_MULTIPLE_THRESHOLD_ACTIVITY = 240
COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY = 5
CODE_REVIEW_COUNT_MULTIPLE_THRESHOLD_ACTIVITY = 8
UPDATED_ISSUES_MULTIPLE_THRESHOLD_ACTIVITY = 2500
RECENT_RELEASES_MULTIPLE_THRESHOLD_ACTIVITY = 12


class ActivityMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file):
        model_name = 'Activity'
        metrics_weights_thresholds = {}
        if level == "repo":
            metrics_weights_thresholds = {
                # "contributor_count": {
                #     "weight": CONTRIBUTOR_COUNT_WEIGHT_ACTIVITY,
                #     "threshold": CONTRIBUTOR_COUNT_THRESHOLD_ACTIVITY
                # },
                # "commit_frequency": {
                #     "weight": COMMIT_FREQUENCY_WEIGHT_ACTIVITY,
                #     "threshold": COMMIT_FREQUENCY_THRESHOLD_ACTIVITY
                # },
                "updated_since": {
                    "weight": UPDATED_SINCE_WEIGHT_ACTIVITY,
                    "threshold": UPDATED_SINCE_THRESHOLD_ACTIVITY
                },
                # "org_count": {
                #     "weight": ORG_COUNT_WEIGHT_ACTIVITY,
                #     "threshold": ORG_COUNT_THRESHOLD_ACTIVITY
                # },
                # "created_since": {
                #     "weight": CREATED_SINCE_WEIGHT_ACTIVITY,
                #     "threshold": REATED_SINCE_THRESHOLD_ACTIVITY
                # },
                # "comment_frequency": {
                #     "weight": COMMENT_FREQUENCY_WEIGHT_ACTIVITY,
                #     "threshold": COMMENT_FREQUENCY_THRESHOLD_ACTIVITY
                # },
                # "code_review_count": {
                #     "weight": CODE_REVIEW_COUNT_WEIGHT_ACTIVITY,
                #     "threshold": CODE_REVIEW_COUNT_THRESHOLD_ACTIVITY
                # },
                # "updated_issues_count": {
                #     "weight": UPDATED_ISSUES_WEIGHT_ACTIVITY,
                #     "threshold": UPDATED_ISSUES_THRESHOLD_ACTIVITY
                # },
                "recent_releases_count": {
                    "weight": RECENT_RELEASES_WEIGHT_ACTIVITY,
                    "threshold": RECENT_RELEASES_THRESHOLD_ACTIVITY
                }
            }
        if level == "community":
            metrics_weights_thresholds = {
                "contributor_count": {
                    "weight": CONTRIBUTOR_COUNT_WEIGHT_ACTIVITY,
                    "threshold": CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_ACTIVITY
                },
                "commit_frequency": {
                    "weight": COMMIT_FREQUENCY_WEIGHT_ACTIVITY,
                    "threshold": COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY
                },
                "updated_since": {
                    "weight": UPDATED_SINCE_WEIGHT_ACTIVITY,
                    "threshold": UPDATED_SINCE_MULTIPLE_THRESHOLD_ACTIVITY
                },
                "org_count": {
                    "weight": ORG_COUNT_WEIGHT_ACTIVITY,
                    "threshold": ORG_COUNT_MULTIPLE_THRESHOLD_ACTIVITY
                },
                # "created_since": {
                #     "weight": CREATED_SINCE_WEIGHT_ACTIVITY,
                #     "threshold": REATED_SINCE_MULTIPLE_THRESHOLD_ACTIVITY
                # },
                "comment_frequency": {
                    "weight": COMMENT_FREQUENCY_WEIGHT_ACTIVITY,
                    "threshold": COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_ACTIVITY
                },
                "code_review_count": {
                    "weight": CODE_REVIEW_COUNT_WEIGHT_ACTIVITY,
                    "threshold": CODE_REVIEW_COUNT_MULTIPLE_THRESHOLD_ACTIVITY
                },
                "updated_issues_count": {
                    "weight": UPDATED_ISSUES_WEIGHT_ACTIVITY,
                    "threshold": UPDATED_ISSUES_MULTIPLE_THRESHOLD_ACTIVITY
                },
                "recent_releases_count": {
                    "weight": RECENT_RELEASES_WEIGHT_ACTIVITY,
                    "threshold": RECENT_RELEASES_MULTIPLE_THRESHOLD_ACTIVITY
                },
            }
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)
