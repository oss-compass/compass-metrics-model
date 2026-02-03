"""
贡献活跃度指标模型 (Contribution Activity Metrics Model)

衡量开发者贡献的活跃程度，包括：
- 代码提交次数
- 新增代码行数
- PR 评论数量
- Issue 建立数量
- Issue 评论数量
- 版本迭代次数
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 权重常量
COMMIT_COUNT_WEIGHT = 0.1667
LINES_ADDED_WEIGHT = 0.1667
PR_COMMENT_COUNT_WEIGHT = 0.1667
ISSUE_NEW_COUNT_WEIGHT = 0.1667
ISSUE_COMMENT_COUNT_WEIGHT = 0.1667
RELEASE_COUNT_WEIGHT = 0.1665
WEIGHT = 0.1665


class ContributionActivityMetricsModel(BaseMetricsModel):
    """
    贡献活跃度指标模型

    评估开发者贡献的活跃程度
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Contribution Activity'
        metrics_weights_thresholds = {
            "commit_count_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "lines_changed_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "pr_comment_count_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "issue_new_count_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "issue_comment_activity_by_period": {
                "weight": WEIGHT,
                "threshold": None
            }
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, custom_fields=custom_fields)
