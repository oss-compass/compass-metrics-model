from compass_model.base_metrics_model import BaseMetricsModel

ACTIVITY_CASUAL_CONTRIBUTOR_COUNT_WEIGHT = 0.08
ACTIVITY_CASUAL_CONTRIBUTION_PER_PERSON_WEIGHT = 0.12
ACTIVITY_REGULAR_CONTRIBUTOR_COUNT_WEIGHT = 0.12
ACTIVITY_REGULAR_CONTRIBUTION_PER_PERSON_WEIGHT = 0.18
ACTIVITY_CORE_CONTRIBUTOR_COUNT_WEIGHT = 0.2
ACTIVITY_CORE_CONTRIBUTION_PER_PERSON_WEIGHT = 0.3

class MilestonePersonaMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                json_file, contributors_enriched_index):
        model_name = 'Milestone Persona'
        metrics_weights_thresholds = {
            "activity_casual_contributor_count": {
                "weight": ACTIVITY_CASUAL_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_casual_contribution_per_person": {
                "weight": ACTIVITY_CASUAL_CONTRIBUTION_PER_PERSON_WEIGHT,
                "threshold": None
            },
            "activity_regular_contributor_count": {
                "weight": ACTIVITY_REGULAR_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_regular_contribution_per_person": {
                "weight": ACTIVITY_REGULAR_CONTRIBUTION_PER_PERSON_WEIGHT,
                "threshold": None
            },
            "activity_core_contributor_count": {
                "weight": ACTIVITY_CORE_CONTRIBUTOR_COUNT_WEIGHT,
                "threshold": None
            },
            "activity_core_contribution_per_person": {
                "weight": ACTIVITY_CORE_CONTRIBUTION_PER_PERSON_WEIGHT,
                "threshold": None
            }
        }
        
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, contributors_enriched_index=contributors_enriched_index)
