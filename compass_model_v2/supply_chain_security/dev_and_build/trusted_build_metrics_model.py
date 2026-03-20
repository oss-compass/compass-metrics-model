from compass_model.base_metrics_model_v2 import BaseMetricsModel

BUILD_SUCCESS_W = 0.25  # trusted_build_success — 可构建（构建成功率）
CI_INTEGRATION_W = 0.25  # ci_integration — CI 集成
BUILD_METADATA_W = 0.25  # build_metadata_available — 构建元数据可获取
REPRODUCIBLE_W = 0.25  # reproducible_build — 一致性构建


class TrustedBuildMetricsModel(BaseMetricsModel):
    """
    可信构建
    - 可构建 → trusted_build_success
    - CI 集成 → ci_integration
    - 构建元数据可获取 → build_metadata_available
    - 一致性构建 → reproducible_build
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source, json_file,
                 contributors_enriched_index, custom_fields, openchecker_index,
                 ):
        model_name = "Trusted Build"
        metrics_weights_thresholds = {
            "trusted_build_success": {"weight": BUILD_SUCCESS_W, "threshold": None},
            "ci_integration": {"weight": CI_INTEGRATION_W, "threshold": None},
            "build_metadata_available": {"weight": BUILD_METADATA_W, "threshold": None},
            "reproducible_build": {"weight": REPRODUCIBLE_W, "threshold": None},
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,
                         contributors_enriched_index=contributors_enriched_index, custom_fields=custom_fields,
                         openchecker_index=openchecker_index,
                         )
