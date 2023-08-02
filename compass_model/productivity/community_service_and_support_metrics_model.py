from compass_model.base_metrics_model import BaseMetricsModel

ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY: -0.1437
BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY: -0.1288
COMMENT_FREQUENCY_WEIGHT_COMMUNITY: 0.1022
UPDATED_ISSUES_WEIGHT_COMMUNITY: 0.1972
PR_OPEN_TIME_WEIGHT_COMMUNITY: -0.1288
CODE_REVIEW_WEIGHT_COMMUNITY: 0.1022
CLOSED_PRS_WEIGHT_COMMUNITY: 0.1972

ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY: 15
BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY: 60
COMMENT_FREQUENCY_THRESHOLD_COMMUNITY: 5
UPDATED_ISSUES_THRESHOLD_COMMUNITY: 2500
PR_OPEN_TIME_THRESHOLD_COMMUNITY: 30
CODE_REVIEW_THRESHOLD_COMMUNITY: 8
CLOSED_PRS_THRESHOLD_COMMUNITY: 4500

ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY: 15
BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY: 60
COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_COMMUNITY: 5
UPDATED_ISSUES_MULTIPLE_THRESHOLD_COMMUNITY: 2500
PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY: 30
CODE_REVIEW_MULTIPLE_THRESHOLD_COMMUNITY: 8
CLOSED_PRS_MULTIPLE_THRESHOLD_COMMUNITY: 60000


class CommunityServiceAndSupportMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                json_file):
        model_name = 'CommunityServiceAndSupport'
        metrics_weights_thresholds = {}

        if level == "repo":
            metrics_weights_thresholds = {
                "issue_first_reponse": {
                    "weight": ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY,
                    "threshold": ISSUE_FIRST_RESPONSE_THRESHOLD_COMMUNITY
                },
                "bug_issue_open_time": {
                    "weight": BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY,
                    "threshold": BUG_ISSUE_OPEN_TIME_THRESHOLD_COMMUNITY
                },
                "comment_frequency": {
                    "weight": COMMENT_FREQUENCY_WEIGHT_COMMUNITY,
                    "threshold": COMMENT_FREQUENCY_THRESHOLD_COMMUNITY
                },                
                "updated_issue_count": {
                    "weight": UPDATED_ISSUES_WEIGHT_COMMUNITY,
                    "threshold": UPDATED_ISSUES_THRESHOLD_COMMUNITY
                },
                "pr_open_time": {
                    "weight": PR_OPEN_TIME_WEIGHT_COMMUNITY,
                    "threshold": PR_OPEN_TIME_THRESHOLD_COMMUNITY
                },
                "code_review_count": {
                    "weight": CODE_REVIEW_WEIGHT_COMMUNITY,
                    "threshold": CODE_REVIEW_THRESHOLD_COMMUNITY
                },

                "closed_prs_count": {
                    "weight": CLOSED_PRS_WEIGHT_COMMUNITY,
                    "threshold": CLOSED_PRS_THRESHOLD_COMMUNITY
                },
            }
        if level == "community":
            metrics_weights_thresholds = {
                "issue_first_reponse": {
                    "weight": ISSUE_FIRST_RESPONSE_WEIGHT_COMMUNITY,
                    "threshold": ISSUE_FIRST_RESPONSE_MULTIPLE_THRESHOLD_COMMUNITY
                },
                "bug_issue_open_time": {
                    "weight": BUG_ISSUE_OPEN_TIME_WEIGHT_COMMUNITY,
                    "threshold": BUG_ISSUE_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY
                },
                "comment_frequency": {
                    "weight": COMMENT_FREQUENCY_WEIGHT_COMMUNITY,
                    "threshold": COMMENT_FREQUENCY_MULTIPLE_THRESHOLD_COMMUNITY
                },                
                "updated_issue_count": {
                    "weight": UPDATED_ISSUES_WEIGHT_COMMUNITY,
                    "threshold": UPDATED_ISSUES_MULTIPLE_THRESHOLD_COMMUNITY
                },
                "pr_open_time": {
                    "weight": PR_OPEN_TIME_WEIGHT_COMMUNITY,
                    "threshold": PR_OPEN_TIME_MULTIPLE_THRESHOLD_COMMUNITY
                },
                "code_review_count": {
                    "weight": CODE_REVIEW_WEIGHT_COMMUNITY,
                    "threshold": CODE_REVIEW_MULTIPLE_THRESHOLD_COMMUNITY
                },

                "closed_prs_count": {
                    "weight": CLOSED_PRS_WEIGHT_COMMUNITY,
                    "threshold": CLOSED_PRS_MULTIPLE_THRESHOLD_COMMUNITY
                },
            }
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds)

