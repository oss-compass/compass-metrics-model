from compass_model.base_metrics_model_v2 import BaseMetricsModel

SBOM_W = 0.25  # sbom_in_release — SBOM 检查
BINARY_ARTIFACT_W = 0.25  # security_binary_artifact — 二进制制品包含（越少越好，但此处按 0-10 得分处理）
PACKAGE_SIG_W = 0.25  # security_package_sig — 软件包签名
RELEASE_NOTE_W = 0.25  # lifecycle_release_note — Release Notes


class ReleaseQualityMetricsModel(BaseMetricsModel):
    """
    发布与维护 / 发布质量
    - SBOM 检查 → sbom_in_release
    - 二进制制品包含 → security_binary_artifact
    - 软件包签名 → security_package_sig
    - Release Notes → lifecycle_release_note
    """

    def __init__(
            self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
            contributors_index, release_index, out_index, from_date, end_date, level, community, source, json_file,
            contributors_enriched_index, custom_fields, openchecker_index,
    ):
        model_name = "Release Quality"
        metrics_weights_thresholds = {
            "sbom_in_release": {"weight": SBOM_W, "threshold": None},
            "security_binary_artifact": {"weight": BINARY_ARTIFACT_W, "threshold": None},
            "security_package_sig": {"weight": PACKAGE_SIG_W, "threshold": None},
            "lifecycle_release_note": {"weight": RELEASE_NOTE_W, "threshold": None},
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,
                         contributors_enriched_index=contributors_enriched_index, custom_fields=custom_fields,
                         openchecker_index=openchecker_index,
                         )
