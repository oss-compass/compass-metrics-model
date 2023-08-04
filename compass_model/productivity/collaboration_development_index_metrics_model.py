from compass_model.base_metrics_model import BaseMetricsModel

CONTRIBUTOR_COUNT_WEIGHT_CODE = 0.1999
COMMIT_FREQUENCY_WEIGHT_CODE = 0.1636
IS_MAINTAINED_WEIGHT_CODE = 0.1385
COMMIT_PR_LINKED_RATIO_WEIGHT_CODE = 0.1261
PR_ISSUE_LINKED_WEIGHT_CODE = 0.1132
CODE_REVIEW_RATIO_WEIGHT_CODE = 0.1011
CODE_MERGE_RATIO_WEIGHT_CODE = 0.1011
LOC_FREQUENCY_WEIGHT_CODE = 0.0564

CONTRIBUTOR_COUNT_THRESHOLD_CODE = 1000
COMMIT_FREQUENCY_THRESHOLD_CODE = 1000
IS_MAINTAINED_THRESHOLD_CODE = 1
COMMIT_PR_LINKED_RATIO_THRESHOLD_CODE = 1
PR_ISSUE_LINKED_THRESHOLD_CODE = 0.2
CODE_REVIEW_RATIO_THRESHOLD_CODE = 1
CODE_MERGE_RATIO_THRESHOLD_CODE = 1
LOC_FREQUENCY_THRESHOLD_CODE = 300000

CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_CODE = 1000
COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_CODE = 1000
IS_MAINTAINED_MULTIPLE_THRESHOLD_CODE = 1
COMMIT_PR_LINKED_RATIO_MULTIPLE_THRESHOLD_CODE = 1
PR_ISSUE_LINKED_MULTIPLE_THRESHOLD_CODE = 0.2
CODE_REVIEW_RATIO_MULTIPLE_THRESHOLD_CODE = 1
CODE_MERGE_RATIO_MULTIPLE_THRESHOLD_CODE = 1
LOC_FREQUENCY_MULTIPLE_THRESHOLD_CODE = 300000


class CollaborationDevelopmentIndexMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                json_file):
        model_name = 'CollaborationDevelopmentIndex'
        metrics_weights_thresholds = {}

        if level == "repo":
            metrics_weights_thresholds = {
                "contributor_count": {
                    "weight": CONTRIBUTOR_COUNT_WEIGHT_CODE,
                    "threshold": CONTRIBUTOR_COUNT_THRESHOLD_CODE
                },
                "commit_frequency": {
                    "weight": COMMIT_FREQUENCY_WEIGHT_CODE,
                    "threshold": COMMIT_FREQUENCY_THRESHOLD_CODE
                },
                "is_maintained": {
                    "weight": IS_MAINTAINED_WEIGHT_CODE,
                    "threshold": IS_MAINTAINED_THRESHOLD_CODE
                },                
                "git_pr_linked_ratio": {
                    "weight": COMMIT_PR_LINKED_RATIO_WEIGHT_CODE,
                    "threshold": COMMIT_PR_LINKED_RATIO_THRESHOLD_CODE
                },
                "pr_issue_linked_ratio": {
                    "weight": PR_ISSUE_LINKED_WEIGHT_CODE,
                    "threshold": PR_ISSUE_LINKED_THRESHOLD_CODE
                },
                "code_review_ratio": {
                    "weight": CODE_REVIEW_RATIO_WEIGHT_CODE,
                    "threshold": CODE_REVIEW_RATIO_THRESHOLD_CODE
                },
                "code_merge_ratio": {
                    "weight": CODE_MERGE_RATIO_WEIGHT_CODE,
                    "threshold": CODE_MERGE_RATIO_THRESHOLD_CODE
                },
                "LOC_frequency": {
                    "weight": LOC_FREQUENCY_WEIGHT_CODE,
                    "threshold": LOC_FREQUENCY_THRESHOLD_CODE
                },
            }
        if level == "community":
            metrics_weights_thresholds = {
                "contributor_count": {
                    "weight": CONTRIBUTOR_COUNT_WEIGHT_CODE,
                    "threshold": CONTRIBUTOR_COUNT_MULTIPLE_THRESHOLD_CODE
                },
                "commit_frequency": {
                    "weight": COMMIT_FREQUENCY_WEIGHT_CODE,
                    "threshold": COMMIT_FREQUENCY_MULTIPLE_THRESHOLD_CODE
                },
                "is_maintained": {
                    "weight": IS_MAINTAINED_WEIGHT_CODE,
                    "threshold": IS_MAINTAINED_MULTIPLE_THRESHOLD_CODE
                },                
                "git_pr_linked_ratio": {
                    "weight": COMMIT_PR_LINKED_RATIO_WEIGHT_CODE,
                    "threshold": COMMIT_PR_LINKED_RATIO_MULTIPLE_THRESHOLD_CODE
                },
                "pr_issue_linked_ratio": {
                    "weight": PR_ISSUE_LINKED_WEIGHT_CODE,
                    "threshold": PR_ISSUE_LINKED_MULTIPLE_THRESHOLD_CODE
                },
                "code_review_ratio": {
                    "weight": CODE_REVIEW_RATIO_WEIGHT_CODE,
                    "threshold": CODE_REVIEW_RATIO_MULTIPLE_THRESHOLD_CODE
                },
                "code_merge_ratio": {
                    "weight": CODE_MERGE_RATIO_WEIGHT_CODE,
                    "threshold": CODE_MERGE_RATIO_MULTIPLE_THRESHOLD_CODE
                },
                "LOC_frequency": {
                    "weight": LOC_FREQUENCY_WEIGHT_CODE,
                    "threshold": LOC_FREQUENCY_MULTIPLE_THRESHOLD_CODE
                },
            }
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)

