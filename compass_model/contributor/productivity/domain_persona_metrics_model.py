from compass_model.base_metrics_model import BaseMetricsModel

ACTIVITY_OBSERVATION_CONTRIBUTOR_COUNT_WEIGHT = 0.2
ACTIVITY_CODE_CONTRIBUTOR_COUNT_WEIGHT = 0.4
ACTIVITY_ISSUE_CONTRIBUTOR_COUNT_WEIGHT = 0.4

class DomainPersonaMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                json_file):
        model_name = 'Role Persona'
        metrics_weights_thresholds = {
            "activity_observation_contributor_count": {
                "weight": ACTIVITY_OBSERVATION_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_code_contributor_count": {
                "weight": ACTIVITY_CODE_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_issue_contributor_count": {
                "weight": ACTIVITY_ISSUE_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            }
        }
        
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)
