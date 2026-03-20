from compass_model.base_metrics_model_v2 import BaseMetricsModel

# 指标 key 与 compass_metrics_v2.supply_chain_security_v2 中函数名一致
LICENSE_HEADER_COPYRIGHT_W = 0.25  # compliance_copyright_statement — 许可头与版权声明
LICENSE_INCLUDED_OSI_W = 0.25  # compliance_license — 许可证包含（OSI）
LICENSE_COMPATIBILITY_W = 0.25  # compliance_license_compatibility — 许可证兼容性
LICENSE_COPYRIGHT_ANTI_TAMPER_W = 0.25  # compliance_copyright_anti_tamper — 许可证与版权声明防篡改


class LegalComplianceMetricsModel(BaseMetricsModel):
    """
    源码管理 / 合法合规
    - 许可头与版权声明 → supply_chain_security_v2.compliance_copyright_statement
    - 许可证包含（OSI）→ compliance_license
    - 许可证兼容性 → compliance_license_compatibility
    - 许可证与版权声明防篡改 → compliance_copyright_anti_tamper
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, custom_fields, openchecker_index):
        model_name = 'Legal Compliance'
        metrics_weights_thresholds = {
            "compliance_copyright_statement": {
                "weight": LICENSE_HEADER_COPYRIGHT_W,
                "threshold": None,
            },
            "compliance_license": {
                "weight": LICENSE_INCLUDED_OSI_W,
                "threshold": None,
            },
            "compliance_license_compatibility": {
                "weight": LICENSE_COMPATIBILITY_W,
                "threshold": None,
            },
            "compliance_copyright_anti_tamper": {
                "weight": LICENSE_COPYRIGHT_ANTI_TAMPER_W,
                "threshold": None,
            },
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,
                         contributors_enriched_index=contributors_enriched_index, custom_fields=custom_fields,
                         openchecker_index=openchecker_index)
