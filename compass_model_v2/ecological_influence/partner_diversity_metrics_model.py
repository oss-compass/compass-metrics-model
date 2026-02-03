"""
生态伙伴多样性指标模型 (Partner Diversity Metrics Model)

衡量合作伙伴的多样性，包括：
- 商业组织数量
- 商业组织贡献者数量
- 研究机构数量
- 研究机构开发者数量
- 个人主力贡献者数量
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 权重常量
BUSINESS_ORG_COUNT_WEIGHT = 0.2
BUSINESS_ORG_CONTRIBUTORS_WEIGHT = 0.2
RESEARCH_INSTITUTION_COUNT_WEIGHT = 0.2
RESEARCH_INSTITUTION_DEVELOPERS_WEIGHT = 0.2
INDIVIDUAL_CORE_CONTRIBUTORS_WEIGHT = 0.2


class PartnerDiversityMetricsModel(BaseMetricsModel):
    """
    生态伙伴多样性指标模型

    评估合作伙伴的多样性
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Partner Diversity'
        metrics_weights_thresholds = {
            "business_org_count": {
                "weight": BUSINESS_ORG_COUNT_WEIGHT,
                "threshold": None
            },
            "business_org_contributors": {
                "weight": BUSINESS_ORG_CONTRIBUTORS_WEIGHT,
                "threshold": None
            },
            "research_institution_count": {
                "weight": RESEARCH_INSTITUTION_COUNT_WEIGHT,
                "threshold": None
            },
            "research_institution_developers": {
                "weight": RESEARCH_INSTITUTION_DEVELOPERS_WEIGHT,
                "threshold": None
            },
            "individual_core_contributors": {
                "weight": INDIVIDUAL_CORE_CONTRIBUTORS_WEIGHT,
                "threshold": None
            },
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, custom_fields=custom_fields)