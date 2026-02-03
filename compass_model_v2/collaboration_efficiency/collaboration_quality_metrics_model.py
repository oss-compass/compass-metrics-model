"""
协作开发质量指标模型 (Collaboration Quality Metrics Model)

衡量代码协作的质量和效率，包括：
- 通过PR提交代码的比率
- PR 关联 Issue 的比率
- Review协作比率
- Merge协作比率
- PR 评论频率
- Review Time by Pull Request Size
"""

from compass_model.base_metrics_model_v2 import BaseMetricsModel


#
PR_MERGE_RATIO_WEIGHT = 0.1667
PR_ISSUE_LINKED_RATIO_WEIGHT = 0.1667
PR_REVIEW_COLLABORATION_RATIO_WEIGHT = 0.1667
PR_MERGE_COLLABORATION_RATIO_WEIGHT = 0.1667
PR_COMMENT_FREQUENCY_WEIGHT = 0.1667
PR_REVIEW_TIME_BY_SIZE_WEIGHT = 0.1665

WEIGHT = 0.1


class CollaborationQualityMetricsModel(BaseMetricsModel):
    """
    协作开发质量指标模型

    评估PR协作的质量和效率
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields):
        model_name = 'Collaboration Quality'
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