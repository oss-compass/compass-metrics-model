from compass_model.base_metrics_model import BaseMetricsModel

CODE_CONTRIBUTOR_COUNT_WEIGHT_CODE = 0.1999
COMMIT_FREQUENCY_WEIGHT_CODE = 0.1636
IS_MAINTAINED_WEIGHT_CODE = 0.1385
COMMIT_PR_LINKED_RATIO_WEIGHT_CODE = 0.1261
PR_ISSUE_LINKED_WEIGHT_CODE = 0.1132
CODE_REVIEW_RATIO_WEIGHT_CODE = 0.1011
CODE_MERGE_RATIO_WEIGHT_CODE = 0.1011
LOC_FREQUENCY_WEIGHT_CODE = 0.0564


class CollaborationDevelopmentIndexMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                json_file):
        model_name = 'Collaboration Development Index'
        metrics_weights_thresholds = {
            "code_contributor_count": {
                "weight": CODE_CONTRIBUTOR_COUNT_WEIGHT_CODE,
                "threshold": None
            },
            "commit_frequency": {
                "weight": COMMIT_FREQUENCY_WEIGHT_CODE,
                "threshold": None
            },
            "is_maintained": {
                "weight": IS_MAINTAINED_WEIGHT_CODE,
                "threshold": None
            },                
            "commit_pr_linked_ratio": {
                "weight": COMMIT_PR_LINKED_RATIO_WEIGHT_CODE,
                "threshold": None
            },
            "pr_issue_linked_ratio": {
                "weight": PR_ISSUE_LINKED_WEIGHT_CODE,
                "threshold": None
            },
            "code_review_ratio": {
                "weight": CODE_REVIEW_RATIO_WEIGHT_CODE,
                "threshold": None
            },
            "code_merge_ratio": {
                "weight": CODE_MERGE_RATIO_WEIGHT_CODE,
                "threshold": None
            },
            "lines_of_code_frequency": {
                "weight": LOC_FREQUENCY_WEIGHT_CODE,
                "threshold": None
            },
        }
        
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)
