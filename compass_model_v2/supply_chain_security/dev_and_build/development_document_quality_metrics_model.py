from compass_model.base_metrics_model_v2 import BaseMetricsModel

README_W = 0.25  # ecology_readme — README 文档质量
BUILD_DOC_W = 0.25  # ecology_build_doc — 构建文档
INTERFACE_DOC_W = 0.25  # ecology_interface_doc — 接口文档（docs/openapi）
MAINTAINER_DOC_W = 0.25  # ecology_maintainer_doc — Committers 文件（OWNERS/MAINTAINERS）


class DevelopmentDocumentQualityMetricsModel(BaseMetricsModel):
    """
    开发与构建 / 开发文档质量
    - README 文档质量 → ecology_readme
    - 构建文档 → ecology_build_doc
    - 接口文档（docs/openapi）→ ecology_interface_doc
    - Committers 文件（OWNERS/MAINTAINERS）→ ecology_maintainer_doc
    """

    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source, json_file,
                 contributors_enriched_index, custom_fields, openchecker_index,
                 ):
        model_name = "Development Document Quality"
        metrics_weights_thresholds = {
            "ecology_readme": {"weight": README_W, "threshold": None},
            "ecology_build_doc": {"weight": BUILD_DOC_W, "threshold": None},
            "ecology_interface_doc": {"weight": INTERFACE_DOC_W, "threshold": None},
            "ecology_maintainer_doc": {"weight": MAINTAINER_DOC_W, "threshold": None},
        }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds,
                         contributors_enriched_index=contributors_enriched_index, custom_fields=custom_fields,
                         openchecker_index=openchecker_index,
                         )
