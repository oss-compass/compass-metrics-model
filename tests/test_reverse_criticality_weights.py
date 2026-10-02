from compass_common.algorithm_utils import get_score_by_criticality_score


WEIGHTS = {
    "created_since": {"weight": 1, "threshold": 120},
    "updated_since": {"weight": -1, "threshold": 120},
}


def test_equal_opposite_weights_do_not_cancel_denominator():
    assert get_score_by_criticality_score(
        {"created_since": 120, "updated_since": 0}, WEIGHTS
    ) == 1.0
    assert get_score_by_criticality_score(
        {"created_since": 0, "updated_since": 120}, WEIGHTS
    ) == 0.0


def test_missing_reverse_metric_does_not_gain_credit():
    assert get_score_by_criticality_score(
        {"created_since": 120, "updated_since": None}, WEIGHTS
    ) == 0.5
