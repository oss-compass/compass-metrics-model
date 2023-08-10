from compass_model.base_metrics_model import BaseMetricsModel

ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY = -0.1437
BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY = -0.1288
COMMENT_FREQUENCY_WEIGHT_COMMUNITY = 0.1022
UPDATED_ISSUES_WEIGHT_COMMUNITY = 0.1972
PR_OPEN_TIME_WEIGHT_COMMUNITY = -0.1288
CODE_REVIEW_WEIGHT_COMMUNITY = 0.1022
CLOSE_PR_WEIGHT_COMMUNITY = 0.1972


class CommunityServiceAndSupportMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                json_file):
        model_name = 'Community Service And Support'
        metrics_weights_thresholds = {
            "issue_first_reponse": {
                "weight": ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY,
                "threshold": None
            },
            "bug_issue_open_time": {
                "weight": BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY,
                "threshold": None
            },
            "comment_frequency": {
                "weight": COMMENT_FREQUENCY_WEIGHT_COMMUNITY,
                "threshold": None
            },                
            "updated_issues_count": {
                "weight": UPDATED_ISSUES_WEIGHT_COMMUNITY,
                "threshold": None
            },
            "pr_open_time": {
                "weight": PR_OPEN_TIME_WEIGHT_COMMUNITY,
                "threshold": None
            },
            "code_review_count": {
                "weight": CODE_REVIEW_WEIGHT_COMMUNITY,
                "threshold": None
            },
            "close_pr_count": {
                "weight": CLOSE_PR_WEIGHT_COMMUNITY,
                "threshold": None
            }
        }
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)

