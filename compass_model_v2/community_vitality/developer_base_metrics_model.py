"""
开发者基数指标模型 (Developer Base Metrics Model)

衡量社区的开发者数量规模，包括：
- 社区贡献者数量
- 代码贡献者数量
- 非代码贡献者数量
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 权重常量
WEIGHT = 0.3334


class DeveloperBaseMetricsModel(BaseMetricsModel):
    """
    开发者基数指标模型

    评估社区开发者规模
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Developer Base'
        metrics_weights_thresholds = {
            "total_active_contributors_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "code_contributors_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "non_code_contributors_by_period": {
                "weight": WEIGHT,
                "threshold": None
            }
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, custom_fields=custom_fields)