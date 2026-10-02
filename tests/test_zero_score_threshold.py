from compass_common.algorithm_utils import get_param_score, get_score_by_criticality_score


def test_zero_metric_and_zero_threshold_have_zero_score():
    assert get_param_score(0, 0) == 0.0
    assert get_score_by_criticality_score(
        {"activity": 0}, {"activity": {"weight": 1, "threshold": 0}}
    ) == 0.0


def test_positive_metric_with_zero_threshold_still_scores_normally():
    assert get_param_score(3, 0) == 1.0
