from compass_model.base_metrics_model_v2 import BaseMetricsModel

DEPENDENCY_REACHABLE_W = 0.25  # dependency_reachable — 依赖可获得
SNIPPET_REFERENCE_W = 0.25  # compliance_snippet_reference — 片段引用
PATENT_RISK_W = 0.25  # patent_risk_oin — 专利风险（OIN）
TEST_COVERAGE_W = 0.25  # ecology_test_coverage — 测试覆盖度（Sonar 综合得分 0–10）


class CodeReviewQualityMetricsModel(BaseMetricsModel):
    """
    开发与构建 / 代码审查质量（opencheck 侧）
    - 依赖可获得 → dependency_reachable
    - 片段引用 → compliance_snippet_reference
    - 专利风险 → patent_risk_oin
    - 测试覆盖度 → ecology_test_coverage

    注：代码评审机制（PR Review 覆盖率）属于 PR 域指标，不在本模型中定义。
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source, json_file,
                 contributors_enriched_index, custom_fields, openchecker_index,
                 ):
        model_name = "Code Review Quality"
        metrics_weights_thresholds = {
            "dependency_reachable": {"weight": DEPENDENCY_REACHABLE_W, "threshold": None},
            "compliance_snippet_reference": {"weight": SNIPPET_REFERENCE_W, "threshold": None},
            "patent_risk_oin": {"weight": PATENT_RISK_W, "threshold": None},
            "ecology_test_coverage": {"weight": TEST_COVERAGE_W, "threshold": None},
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,
                         contributors_enriched_index=contributors_enriched_index, custom_fields=custom_fields,
                         openchecker_index=openchecker_index,
                         )
