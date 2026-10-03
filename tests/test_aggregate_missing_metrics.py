from compass_common.algorithm_utils import get_score_by_aggregate_score


def test_missing_metric_is_excluded_from_weighted_average():
    weights = {"present": {"weight": 1}, "missing": {"weight": 3}}
    assert get_score_by_aggregate_score({"present": 0.8}, weights) == 0.8
    assert get_score_by_aggregate_score({}, weights) == 0.0
