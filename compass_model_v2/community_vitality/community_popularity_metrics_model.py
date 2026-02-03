"""
社区流行度指标模型 (Community Popularity Metrics Model)

衡量社区的受欢迎程度，包括：
- Stars
- Forks
- 社交网站提及
- Github提及
- 媒体报道
- 搜索查询量
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 权重常量
STARS_WEIGHT = 0.1667
FORKS_WEIGHT = 0.1667
SOCIAL_MENTIONS_WEIGHT = 0.1667
GITHUB_MENTIONS_WEIGHT = 0.1667
MEDIA_COVERAGE_WEIGHT = 0.1667
SEARCH_QUERIES_WEIGHT = 0.1665


class CommunityPopularityMetricsModel(BaseMetricsModel):
    """
    社区流行度指标模型

    评估社区的受欢迎程度
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Community Popularity'
        metrics_weights_thresholds = {
            "repo_stars_by_period": {
                "weight": STARS_WEIGHT,
                "threshold": None
            },
            "repo_forks_by_period": {
                "weight": FORKS_WEIGHT,
                "threshold": None
            },

        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, custom_fields=custom_fields)