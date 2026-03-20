from compass_model.base_metrics_model_v2 import BaseMetricsModel

WEIGHT = 0.5


class SecurityManagementMetricsMode(BaseMetricsModel):
    """
    安全管理
    - 漏洞响应与披露（SECURITY.md + 可选 SLA 指标）
    - 公开未修复漏洞（优先 opencheck/OSV 结果）
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields, openchecker_index):
        model_name = 'Security Management'
        metrics_weights_thresholds = {
            "vulnerability_disclosure": {
                "weight": WEIGHT,
                "threshold": None,
            },
            "security_vulnerability": {
                "weight": WEIGHT,
                "threshold": None,
            },

        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,
                         contributors_enriched_index=contributors_enriched_index, custom_fields=custom_fields,
                         openchecker_index=openchecker_index)
