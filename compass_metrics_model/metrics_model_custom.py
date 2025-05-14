from compass_model.base_metrics_model import BaseMetricsModel
from compass_metrics_model.metric_constants import COMMUNITY_PORTRAIT_METRICS

DEFAULT_WEIGHT = 1.0
DEFAULT_THRESHOLD = None


class MetricsModelCustom(BaseMetricsModel):
    def __init__(self, repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                 contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                 json_file, contributors_enriched_index, metrics_param):

        model_name = 'Metrics Model Custom'

        custom_fields = {}
        metric_list = []
        if metrics_param:
            metric_list = metrics_param.get("metric_list", [])
            version_number = metrics_param.get("version_number")
            custom_fields = {
                "version_number": version_number
            }


        if not metric_list:
            metric_list = COMMUNITY_PORTRAIT_METRICS


        metrics_weights_thresholds = {}
        for metric in metric_list:
            metrics_weights_thresholds[metric] = {
                "weight": DEFAULT_WEIGHT,
                "threshold": DEFAULT_THRESHOLD
            }

        super().__init__(repo_index, git_index, issue_index, pr_index, issue_comments_index, pr_comments_index,
                         contributors_index, release_index, out_index, from_date, end_date, level, community, source,
                         json_file, model_name, metrics_weights_thresholds, custom_fields=custom_fields,
                         contributors_enriched_index=contributors_enriched_index)
