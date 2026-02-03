"""
响应及时性指标模型 (Response Timeliness Metrics Model)

衡量社区对问题和PR的响应速度，包括：
- Issue 超过一个周期未响应的占比
- Issue 首次响应时间
- Issue 处理时长
- PR 超过一个周期未响应的占比
- PR 首次响应时间
- PR 处理时长
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 权重常量
WEIGHT = 0.1667



class ResponseTimelinessMetricsModel(BaseMetricsModel):
    """
    响应及时性指标模型

    评估社区对用户反馈和贡献的响应速度
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'ResponseTimelinessModel'
        metrics_weights_thresholds = {
            "issue_new_first_response_time_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "issue_new_unresponsive_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "issue_new_handle_time_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "pr_new_unresponsive_ratio_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "pr_new_handle_time_by_period": {
                "weight": WEIGHT,
                "threshold": None
            },
            "pr_new_first_response_time_by_period": {
                "weight": WEIGHT,
                "threshold": None
            }
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, custom_fields=custom_fields)