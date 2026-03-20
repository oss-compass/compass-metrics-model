# """
# 评估模型：开发者体验 (Developer Experience)
#
# 度量指标（周期：月、季度、年）：
# - 社区参与体验VOD、产品使用体验VOD
# """
#
# from compass_model.base_metrics_model import BaseMetricsModel
#
#
# COMMUNITY_PARTICIPATION_VOD_WEIGHT = 0.5
# PRODUCT_USAGE_VOD_WEIGHT = 0.5
#
#
# class DeveloperExperienceMetricsModel(BaseMetricsModel):
#     """
#     开发者体验指标模型
#
#     社区参与体验VOD、产品使用体验VOD（占位）
#     """
#
#     def __init__(self, repo_index, git_index, issue_index, pr_index,
#                  issue_comments_index, pr_comments_index, contributors_index,
#                  release_index, out_index, from_date, end_date, level, community,
#                  source, json_file):
#         model_name = 'Developer Experience'
#         metrics_weights_thresholds = {
#             "community_participation_vod": {"weight": COMMUNITY_PARTICIPATION_VOD_WEIGHT, "threshold": None},
#             "product_usage_vod": {"weight": PRODUCT_USAGE_VOD_WEIGHT, "threshold": None},
#         }
#
#         super().__init__(repo_index, git_index, issue_index, pr_index,
#                         issue_comments_index, pr_comments_index, contributors_index,
#                         release_index, out_index, from_date, end_date, level, community,
#                         source, json_file, model_name, metrics_weights_thresholds)
