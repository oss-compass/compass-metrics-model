"""
评估模型：开发者吸引 (Developer Attraction)

度量指标（周期：月、季度、年）：
- 新增组织数、新增组织代码/非代码开发者、新增个人代码/非代码开发者
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 权重常量
NEW_ORG_COUNT_WEIGHT = 0.2
NEW_ORG_CODE_CONTRIBUTORS_WEIGHT = 0.2
NEW_ORG_NON_CODE_CONTRIBUTORS_WEIGHT = 0.2
NEW_INDIVIDUAL_CODE_CONTRIBUTORS_WEIGHT = 0.2
NEW_INDIVIDUAL_NON_CODE_CONTRIBUTORS_WEIGHT = 0.2


class DeveloperAttractionMetricsModel(BaseMetricsModel):
    """
    开发者吸引指标模型

    对应 developer_metrics_v2：new_org_count_by_period, new_org_code_contributors_by_period 等
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Developer Attraction'
        metrics_weights_thresholds = {
            "new_org_count_by_period": {"weight": NEW_ORG_COUNT_WEIGHT, "threshold": None},
            "new_org_code_contributors_by_period": {"weight": NEW_ORG_CODE_CONTRIBUTORS_WEIGHT, "threshold": None},
            "new_org_non_code_contributors_by_period": {"weight": NEW_ORG_NON_CODE_CONTRIBUTORS_WEIGHT, "threshold": None},
            "new_individual_code_contributors_by_period": {"weight": NEW_INDIVIDUAL_CODE_CONTRIBUTORS_WEIGHT, "threshold": None},
            "new_individual_non_code_contributors_by_period": {"weight": NEW_INDIVIDUAL_NON_CODE_CONTRIBUTORS_WEIGHT,"threshold": None},
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,contributors_enriched_index = contributors_enriched_index, custom_fields=custom_fields)
