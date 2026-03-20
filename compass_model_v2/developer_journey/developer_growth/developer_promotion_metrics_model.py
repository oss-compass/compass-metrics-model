"""
评估模型：开发者晋升 (Developer Promotion)

度量指标（周期：月、季度、年）：
- 组织/个人 × 代码/Issue 核心开发者（含管理者）晋升数量（4 项）
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 4 项均权
W = 0.25


class DeveloperPromotionMetricsModel(BaseMetricsModel):
    """
    开发者晋升指标模型

    对应 developer_metrics_v2：org_code_core_promotion_count_by_period 等 4 个函数
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Developer Promotion'
        metrics_weights_thresholds = {
            "org_code_core_promotion_count_by_period": {"weight": W, "threshold": None},
            "org_issue_core_promotion_count_by_period": {"weight": W, "threshold": None},
            "individual_code_core_promotion_count_by_period": {"weight": W, "threshold": None},
            "individual_issue_core_promotion_count_by_period": {"weight": W, "threshold": None},
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,
                         contributors_enriched_index=contributors_enriched_index, custom_fields=custom_fields)
