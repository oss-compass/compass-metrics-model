"""
技术采纳度指标模型 (Technology Adoption Metrics Model)

衡量技术被采用的程度，包括：
- 软件包下载量
- 开源软件采用量
- 商业软件采用量
- 论文引用量
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 权重常量
# package_downloads and paper_citations are intentionally not declared: this
# repository ingests neither package registry download data nor publication
# citation data, so a value for them would be invented. The two metrics that the
# enriched contributor index can actually feed keep the model usable and their
# weights are renormalised so that they still sum to 1.
OPEN_SOURCE_ADOPTION_WEIGHT = 0.5
COMMERCIAL_ADOPTION_WEIGHT = 0.5


class TechnologyAdoptionMetricsModel(BaseMetricsModel):
    """
    技术采纳度指标模型

    评估技术被采用的程度
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Technology Adoption'
        metrics_weights_thresholds = {
            "open_source_adoption": {
                "weight": OPEN_SOURCE_ADOPTION_WEIGHT,
                "threshold": None
            },
            "commercial_adoption": {
                "weight": COMMERCIAL_ADOPTION_WEIGHT,
                "threshold": None
            },
        }

        # The ecological influence metrics read the enriched contributor index,
        # so it has to reach BaseMetricsModel; the model signature already accepts
        # it, without forwarding it the metrics would query a None index.
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, custom_fields=custom_fields,
                         contributors_enriched_index=contributors_enriched_index)