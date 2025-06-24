from compass_model.base_metrics_model import BaseMetricsModel


class CriticalityScoreMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file):
        model_name = 'Criticality Score'
        metrics_weights_thresholds = {
            "created_since": { "weight": 0.09523, "threshold": 120 },
            "updated_since": { "weight": -0.09523, "threshold": 120 },
            "contributor_count_all": { "weight": 0.19047, "threshold": 5000 },
            "org_count_all": { "weight": 0.09523, "threshold": 10 },
            "commit_frequency_last_year": { "weight": 0.09523, "threshold": 1000 },
            "recent_releases_count": { "weight": 0.04761, "threshold": 26 },
            "closed_issues_count": { "weight": 0.04761, "threshold": 5000 },
            "updated_issues_count": { "weight": 0.04761, "threshold": 5000 },
            "comment_frequency": { "weight": 0.09523, "threshold": 15 },
            # "dependents_count": { "weight": 0.19047, "threshold": 500000 },
        }
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)
