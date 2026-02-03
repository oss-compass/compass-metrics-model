"""
组织开放治理指标模型 (Organizational Governance Metrics Model)

衡量组织层面的开放治理情况，包括：
- 组织数
- 组织代码贡献者
- 组织代码贡献者占比
- 组织代码贡献量
- 组织代码贡献量占比
- 组织非代码贡献者
- 组织非代码贡献者占比
- 组织非代码贡献量
- 组织非代码贡献量占比
- 参与治理的组织数
- 组织管理者数量
- 组织管理者数量占比
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 权重常量
ORG_COUNT_WEIGHT = 0.0833
ORG_CODE_CONTRIBUTORS_WEIGHT = 0.0833
ORG_CODE_CONTRIBUTORS_RATIO_WEIGHT = 0.0833
ORG_CODE_CONTRIBUTION_WEIGHT = 0.0833
ORG_CODE_CONTRIBUTION_RATIO_WEIGHT = 0.0833
ORG_NON_CODE_CONTRIBUTORS_WEIGHT = 0.0833
ORG_NON_CODE_CONTRIBUTORS_RATIO_WEIGHT = 0.0833
ORG_NON_CODE_CONTRIBUTION_WEIGHT = 0.0833
ORG_NON_CODE_CONTRIBUTION_RATIO_WEIGHT = 0.0833
GOVERNANCE_ORG_COUNT_WEIGHT = 0.0833
ORG_MANAGER_COUNT_WEIGHT = 0.0833
ORG_MANAGER_COUNT_RATIO_WEIGHT = 0.0834
WEIGHT = 0.0834


class OrganizationalGovernanceMetricsModel(BaseMetricsModel):
    """
    组织开放治理指标模型

    评估组织层面的开放治理情况
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Organizational Governance'
        metrics_weights_thresholds = {
            "participating_orgs_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "org_code_contributors_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "org_code_contributors_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "org_code_contribution_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "org_code_contribution_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "org_non_code_contributors_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "org_non_code_contributors_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "org_non_code_contribution_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "org_non_code_contribution_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "governance_orgs_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "org_managers_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "org_managers_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            }
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,contributors_enriched_index=contributors_enriched_index, custom_fields=custom_fields)