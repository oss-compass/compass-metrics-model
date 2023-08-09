from compass_model.base_metrics_model import BaseMetricsModel

ORG_CONTRIBUTOR_COUNT_WEIGHT_ORG_ACTIVITY = 0.2581
ORG_COMMIT_FREQUENCY_WEIGHT_ORG_ACTIVITY = 0.2581
ORG_COUNT_WEIGHT_ORG_ACTIVITY = 0.3226
ORG_CONTRIBUTION_LAST_WEIGHT_ORG_ACTIVITY = 0.1613

ORG_CONTRIBUTOR_COUNT_THRESHOLD_ORG_ACTIVITY = 300
ORG_COMMIT_FREQUENCY_THRESHOLD_ORG_ACTIVITY = 800
ORG_COUNT_THRESHOLD_ORG_ACTIVITY = 30
ORG_CONTRIBUTION_LAST_THRESHOLD_ORG_ACTIVITY = 160

ORG_CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_ORG_ACTIVITY = 350
ORG_COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ORG_ACTIVITY = 1000
ORG_COUNT_MULTIPLE_THRESHOLD_ORG_ACTIVITY = 30
ORG_CONTRIBUTION_LAST_MULTIPLE_THRESHOLD_ORG_ACTIVITY = 400


class OrganizationsActivityMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file):
        model_name = 'Organizations Activity'
        metrics_weights_thresholds = {}
        if level == "repo":
            metrics_weights_thresholds = {
                "org_contributor_count": {
                    "weight": ORG_CONTRIBUTOR_COUNT_WEIGHT_ORG_ACTIVITY,
                    "threshold": ORG_CONTRIBUTOR_COUNT_THRESHOLD_ORG_ACTIVITY
                },
                "org_commit_frequency": {
                    "weight": ORG_COMMIT_FREQUENCY_WEIGHT_ORG_ACTIVITY,
                    "threshold": ORG_COMMIT_FREQUENCY_THRESHOLD_ORG_ACTIVITY
                },
                "org_count": {
                    "weight": ORG_COUNT_WEIGHT_ORG_ACTIVITY,
                    "threshold": ORG_COUNT_THRESHOLD_ORG_ACTIVITY
                },
                "org_contribution_last": {
                    "weight": ORG_CONTRIBUTION_LAST_WEIGHT_ORG_ACTIVITY,
                    "threshold": ORG_CONTRIBUTION_LAST_THRESHOLD_ORG_ACTIVITY
                }
            }
        if level == "community":
            metrics_weights_thresholds = {
                "org_contributor_count": {
                    "weight": ORG_CONTRIBUTOR_COUNT_WEIGHT_ORG_ACTIVITY,
                    "threshold": ORG_CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_ORG_ACTIVITY
                },
                "org_commit_frequency": {
                    "weight": ORG_COMMIT_FREQUENCY_WEIGHT_ORG_ACTIVITY,
                    "threshold": ORG_COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_ORG_ACTIVITY
                },
                "org_count": {
                    "weight": ORG_COUNT_WEIGHT_ORG_ACTIVITY,
                    "threshold": ORG_COUNT_MULTIPLE_THRESHOLD_ORG_ACTIVITY
                },
                "org_contribution_last": {
                    "weight": ORG_CONTRIBUTION_LAST_WEIGHT_ORG_ACTIVITY,
                    "threshold": ORG_CONTRIBUTION_LAST_MULTIPLE_THRESHOLD_ORG_ACTIVITY
                }
            }
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)
