"""
生态伙伴影响力指标模型 (Partner Influence Metrics Model)

衡量合作伙伴的影响力，包括：
- 商业组织生态影响力
- 研究机构生态影响力
- 个人贡献者生态影响力
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 权重常量
BUSINESS_ORG_INFLUENCE_WEIGHT = 0.3333
RESEARCH_INSTITUTION_INFLUENCE_WEIGHT = 0.3333
INDIVIDUAL_CONTRIBUTOR_INFLUENCE_WEIGHT = 0.3334


class PartnerInfluenceMetricsModel(BaseMetricsModel):
    """
    生态伙伴影响力指标模型

    评估合作伙伴的影响力
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index,
                 issue_comments_index, pr_comments_index, contributors_index,
                 release_index, out_index, from_date, end_date, level, community,
                 source, json_file):
        model_name = 'Partner Influence'
        metrics_weights_thresholds = {
            "business_org_influence": {
                "weight": BUSINESS_ORG_INFLUENCE_WEIGHT,
                "threshold": None
            },
            "research_institution_influence": {
                "weight": RESEARCH_INSTITUTION_INFLUENCE_WEIGHT,
                "threshold": None
            },
            "individual_contributor_influence": {
                "weight": INDIVIDUAL_CONTRIBUTOR_INFLUENCE_WEIGHT,
                "threshold": None
            },
        }

        super().__init__(repo_index, git_index, issue_index, pr_index,
                        issue_comments_index, pr_comments_index, contributors_index,
                        release_index, out_index, from_date, end_date, level, community,
                        source, json_file, model_name, metrics_weights_thresholds)