from compass_model.base_metrics_model import BaseMetricsModel

ACTIVITY_ORGANIZATION_CONTRIBUTOR_COUNT_WEIGHT = 0.2
ACTIVITY_ORGANIZATION_CONTRIBUTION_PER_PERSON_WEIGHT = 0.3
ACTIVITY_INDIVIDUAL_CONTRIBUTOR_COUNT_WEIGHT = 0.2
ACTIVITY_INDIVIDUAL_CONTRIBUTION_PER_PERSON_WEIGHT = 0.3

class RolePersonaMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                json_file, contributors_enriched_index):
        model_name = 'Role Persona'
        metrics_weights_thresholds = {
            "activity_organization_contributor_count": {
                "weight": ACTIVITY_ORGANIZATION_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_organization_contribution_per_person": {
                "weight": ACTIVITY_ORGANIZATION_CONTRIBUTION_PER_PERSON_WEIGHT,
                "threshold": None
            },
            "activity_individual_contributor_count": {
                "weight": ACTIVITY_INDIVIDUAL_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_individual_contribution_per_person": {
                "weight": ACTIVITY_INDIVIDUAL_CONTRIBUTION_PER_PERSON_WEIGHT,
                "threshold": None
            }
        }
        
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, contributors_enriched_index=contributors_enriched_index)
