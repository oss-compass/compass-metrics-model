from compass_model.base_metrics_model import BaseMetricsModel

ACTIVITY_OBSERVATION_CONTRIBUTOR_COUNT_WEIGHT = 0.08
ACTIVITY_OBSERVATION_CONTRIBUTION_PER_PERSON_WEIGHT = 0.12
ACTIVITY_CODE_CONTRIBUTOR_COUNT_WEIGHT = 0.16
ACTIVITY_CODE_CONTRIBUTION_PER_PERSON_WEIGHT = 0.24
ACTIVITY_ISSUE_CONTRIBUTOR_COUNT_WEIGHT = 0.16
ACTIVITY_ISSUE_CONTRIBUTION_PER_PERSON_WEIGHT = 0.24

class DomainPersonaMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                json_file, contributors_enriched_index):
        model_name = 'Domain Persona'
        metrics_weights_thresholds = {
            "activity_observation_contributor_count": {
                "weight": ACTIVITY_OBSERVATION_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_observation_contribution_per_person": {
                "weight": ACTIVITY_OBSERVATION_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_code_contributor_count": {
                "weight": ACTIVITY_CODE_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_code_contribution_per_person": {
                "weight": ACTIVITY_CODE_CONTRIBUTION_PER_PERSON_WEIGHT,
                "threshold": None
            },
            "activity_issue_contributor_count": {
                "weight": ACTIVITY_ISSUE_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_issue_contribution_per_person": {
                "weight": ACTIVITY_ISSUE_CONTRIBUTION_PER_PERSON_WEIGHT,
                "threshold": None
            }
        }
        
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, contributors_enriched_index=contributors_enriched_index)
