from compass_common.algorithm_utils import get_medium


def test_median_does_not_reorder_metric_samples():
    samples = [8, 2, 4, 6]

    assert get_medium(samples) == 5
    assert samples == [8, 2, 4, 6]
    assert get_medium([]) is None
