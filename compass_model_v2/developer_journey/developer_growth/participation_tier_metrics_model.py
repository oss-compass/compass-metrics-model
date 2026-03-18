"""
评估模型：开发者参与度分层 (Participation Tier)

度量指标（周期：月、季度、年）：
- 组织/个人 × 代码/Issue × 核心（含管理者）/常客/访客 数量（12 项）
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 12 项均权
W = 1.0 / 12


class ParticipationTierMetricsModel(BaseMetricsModel):
    """
    开发者参与度分层指标模型

    对应 developer_metrics_v2：org_code_core_contributors_by_period 等 12 个 by_period 函数
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Participation Tier'
        metrics_weights_thresholds = {
            "org_code_core_contributors_by_period": {"weight": W, "threshold": None},
            "org_issue_core_contributors_by_period": {"weight": W, "threshold": None},
            "org_code_regular_contributors_by_period": {"weight": W, "threshold": None},
            "org_issue_regular_contributors_by_period": {"weight": W, "threshold": None},
            "org_code_visitor_contributors_by_period": {"weight": W, "threshold": None},
            "org_issue_visitor_contributors_by_period": {"weight": W, "threshold": None},
            "individual_code_core_contributors_by_period": {"weight": W, "threshold": None},
            "individual_issue_core_contributors_by_period": {"weight": W, "threshold": None},
            "individual_code_regular_contributors_by_period": {"weight": W, "threshold": None},
            "individual_issue_regular_contributors_by_period": {"weight": W, "threshold": None},
            "individual_code_visitor_contributors_by_period": {"weight": W, "threshold": None},
            "individual_issue_visitor_contributors_by_period": {"weight": W, "threshold": None},
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,
                         contributors_enriched_index=contributors_enriched_index, custom_fields=custom_fields)

