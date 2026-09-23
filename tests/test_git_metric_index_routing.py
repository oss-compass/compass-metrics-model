import unittest
from datetime import datetime

from compass_common.algorithm_utils import get_param_score
from compass_model.base_metrics_model_v2 import BaseMetricsModel


class IndexSensitiveClient:
    def __init__(self):
        self.calls = []

    def search(self, index, body):
        self.calls.append((index, body))
        field = body["aggs"]["count_of_uuid"][next(iter(body["aggs"]["count_of_uuid"]))]["field"]
        values = {"hash": 3, "lines_added": 8, "lines_removed": 2}
        value = values[field] if index == "git-commits" else 0
        return {"hits": {"total": {"value": 1 if value else 0}},
                "aggregations": {"count_of_uuid": {"value": value}}}


class GitMetricIndexRoutingTests(unittest.TestCase):
    def test_active_metrics_query_git_commit_index(self):
        model = BaseMetricsModel.__new__(BaseMetricsModel)
        model.client = IndexSensitiveClient()
        model.git_index = "git-commits"
        model.contributors_enriched_index = "enriched-contributors"
        model.metrics_weights_thresholds = {
            "commit_count_by_period": {},
            "lines_changed_by_period": {},
        }

        metrics, _ = model.get_metrics(datetime(2024, 2, 15), ["repo"])

        self.assertEqual(metrics["commit_count"], 3)
        self.assertEqual(metrics["lines_added"], 8)
        self.assertEqual(metrics["lines_removed"], 2)
        self.assertEqual([index for index, _ in model.client.calls], ["git-commits"] * 3)
        for _, body in model.client.calls:
            self.assertEqual(body["query"]["bool"]["must"][0],
                             {"terms": {"tag": ["repo.git"]}})

    def test_line_additions_contribute_to_the_model_score(self):
        model = BaseMetricsModel.__new__(BaseMetricsModel)
        model.algorithm = "criticality_score"
        model.metrics_weights_thresholds = {
            "lines_changed_by_period": {"weight": 1, "threshold": 10},
        }

        self.assertEqual(
            model.get_metrics_score({"lines_added": 8, "lines_removed": 2}),
            round(get_param_score(8, 10), 5),
        )


if __name__ == "__main__":
    unittest.main()
