from datetime import datetime
from unittest.mock import Mock, patch

from compass_model import base_metrics_model_v2


def test_scoring_failure_uses_zero_and_continues_bulk_write():
    model = object.__new__(base_metrics_model_v2.BaseMetricsModel)
    model.client = Mock()
    model.repo_index = "repos"
    model.release_index = "releases"
    model.git_index = "git"
    model.out_index = "scores"
    model.from_date = datetime(2026, 1, 1)
    model.end_date = datetime(2026, 1, 31)
    model.period = "month"
    model.model_name = "test-model"
    model.community = "test-community"
    model.custom_fields_hash = "fields"
    model.custom_fields = {}
    model.get_metrics = Mock(return_value=({"metric": 1}, {}))
    model.metrics_decay = Mock(side_effect=lambda data, last: data)
    model.get_metrics_score = Mock(side_effect=ValueError("bad score"))
    helpers = Mock()

    with patch.object(base_metrics_model_v2, "add_release_message"), \
         patch.object(base_metrics_model_v2, "get_date_list_by_period", return_value=[datetime(2026, 1, 1)]), \
         patch.object(base_metrics_model_v2, "created_since", return_value={"created_since": datetime(2020, 1, 1)}), \
         patch.object(base_metrics_model_v2, "cache_last_metrics_data"), \
         patch.object(base_metrics_model_v2, "helpers", return_value=helpers):
        model.metrics_model_enrich(["repo"], "repo", "repo")

    assert model.get_metrics_score.call_count == 1
    assert helpers.bulk.call_args.kwargs["actions"][0]["_source"]["score"] == 0
