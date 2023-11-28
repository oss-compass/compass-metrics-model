from compass_model.base_metrics_model import BaseMetricsModel

ACTIVITY_ORGANIZATION_CONTRIBUTOR_COUNT_WEIGHT = 0.5
ACTIVITY_INDIVIDUAL_CONTRIBUTOR_COUNT_WEIGHT = 0.5

class RolePersonaMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                json_file):
        model_name = 'Role Persona'
        metrics_weights_thresholds = {
            "activity_organization_contributor_count": {
                "weight": ACTIVITY_ORGANIZATION_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_individual_contributor_count": {
                "weight": ACTIVITY_INDIVIDUAL_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            }
        }
        
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)
