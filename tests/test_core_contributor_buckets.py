from compass_metrics_v2.developer_metrics_v2 import _tier_counts_from_contribution_map


def test_largest_contributor_crossing_half_is_core():
    assert _tier_counts_from_contribution_map({"a": 90, "b": 10}) == (1, 0, 1)


def test_each_tier_contains_the_contributor_crossing_its_boundary():
    assert _tier_counts_from_contribution_map({"a": 40, "b": 30, "c": 20, "d": 10}) == (2, 1, 1)
