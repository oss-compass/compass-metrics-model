from compass_model.base_metrics_model import BaseMetricsModel


CRITICAL = 10    # 严重风险
HIGH = 7.5       # 高风险  
MEDIUM = 5       # 中等风险
LOW = 2.5        # 低风险

THRESHOLD = 10


class ScorecardMetricsModel(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, openchecker_index):
        model_name = 'Scorecard'
        algorithm = "aggregate_score"
        metrics_weights_thresholds = {
            "binary_artifacts": { "weight": HIGH, "threshold": THRESHOLD }, 
            "branch_protection": { "weight": HIGH, "threshold": THRESHOLD }, 
            "ci_tests": { "weight": LOW, "threshold": THRESHOLD },  #不支持
            "cii_best_practices": { "weight": LOW, "threshold": THRESHOLD }, 
            "code_review": { "weight": HIGH, "threshold": THRESHOLD }, 
            "contributors": { "weight": HIGH, "threshold": THRESHOLD }, 
            "dangerous_workflow": { "weight": CRITICAL, "threshold": THRESHOLD },  
            "dependency_update_tool": { "weight": HIGH, "threshold": THRESHOLD },  #不支持
            "fuzzing": { "weight": MEDIUM, "threshold": THRESHOLD },
            "license": { "weight": LOW, "threshold": THRESHOLD },  
            "maintained": { "weight": HIGH, "threshold": THRESHOLD }, 
            "packaging": { "weight": MEDIUM, "threshold": THRESHOLD }, 
            "pinned_dependencies": { "weight": MEDIUM, "threshold": THRESHOLD }, 
            "sast": { "weight": MEDIUM, "threshold": THRESHOLD },  
            "sbom": { "weight": MEDIUM, "threshold": THRESHOLD },  
            "security_policy": { "weight": MEDIUM, "threshold": THRESHOLD },  
            "signed_releases": { "weight": HIGH, "threshold": THRESHOLD },
            "token_permissions": { "weight": HIGH, "threshold": THRESHOLD }, 
            "vulnerabilities": { "weight": HIGH, "threshold": THRESHOLD }, 
            "webhooks": { "weight": CRITICAL, "threshold": THRESHOLD }, 
        }
        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, 
                         contributors_enriched_index = contributors_enriched_index, 
                         algorithm=algorithm, 
                         openchecker_index=openchecker_index)
