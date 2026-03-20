from compass_model.base_metrics_model_v2 import BaseMetricsModel

LIFECYCLE_STATEMENT_W = 0.5  # lifecycle_statement — 生命周期申明
AVG_VUL_FIX_TIME_W = 0.5  # avg_vulnerability_fix_time — 安全漏洞平均修复时间


class MaintenanceManagementMetricsModel(BaseMetricsModel):
    """
    发布与维护 / 维护管理
    - 生命周期申明 → lifecycle_statement
    - 安全漏洞平均修复时间 → avg_vulnerability_fix_time
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source, json_file,
                 contributors_enriched_index, custom_fields, openchecker_index,
                 ):
        model_name = "Maintenance Management"
        metrics_weights_thresholds = {
            "lifecycle_statement": {"weight": LIFECYCLE_STATEMENT_W, "threshold": None},
            "avg_vulnerability_fix_time": {"weight": AVG_VUL_FIX_TIME_W, "threshold": None},
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,
                         contributors_enriched_index=contributors_enriched_index, custom_fields=custom_fields,
                         openchecker_index=openchecker_index,
                         )


# wanchengle yi xiang dagogncheng