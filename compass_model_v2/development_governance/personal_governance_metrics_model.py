"""
个人开放治理指标模型 (Personal Governance Metrics Model)

衡量个人层面的开放治理情况，包括：
- 个人代码贡献者
- 个人代码贡献者占比
- 个人代码贡献量
- 个人代码贡献量占比
- 个人非代码贡献者
- 个人非代码贡献者占比
- 个人非代码贡献量
- 个人非代码贡献量占比
- 个人管理者数量
- 个人管理者数量占比
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 权重常量
PERSONAL_CODE_CONTRIBUTORS_WEIGHT = 0.1
PERSONAL_CODE_CONTRIBUTORS_RATIO_WEIGHT = 0.1
PERSONAL_CODE_CONTRIBUTION_WEIGHT = 0.1
PERSONAL_CODE_CONTRIBUTION_RATIO_WEIGHT = 0.1
PERSONAL_NON_CODE_CONTRIBUTORS_WEIGHT = 0.1
PERSONAL_NON_CODE_CONTRIBUTORS_RATIO_WEIGHT = 0.1
PERSONAL_NON_CODE_CONTRIBUTION_WEIGHT = 0.1
PERSONAL_NON_CODE_CONTRIBUTION_RATIO_WEIGHT = 0.1
PERSONAL_MANAGER_COUNT_WEIGHT = 0.1
PERSONAL_MANAGER_COUNT_RATIO_WEIGHT = 0.1
WEIGHT = 0.1


class PersonalGovernanceMetricsModel(BaseMetricsModel):
    """
    个人开放治理指标模型

    评估个人层面的开放治理情况
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Personal Governance'
        metrics_weights_thresholds = {
            "individual_code_contributors_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "individual_code_contributors_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "individual_code_contribution_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "individual_code_contribution_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "individual_non_code_contributors_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "individual_non_code_contributors_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "individual_non_code_contribution_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "individual_non_code_contribution_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "individual_managers_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "individual_managers_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            }
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, contributors_enriched_index=contributors_enriched_index,custom_fields=custom_fields)
