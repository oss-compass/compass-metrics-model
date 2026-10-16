from datetime import datetime

from compass_metrics_v2.repo_metrics_v2 import get_period_range


def test_period_end_is_the_last_instant_regardless_of_input_time():
    date = datetime(2026, 5, 12, 14, 30, 15, 123456)

    assert get_period_range(date, "month") == (
        datetime(2026, 5, 1), datetime(2026, 5, 31, 23, 59, 59, 999999)
    )
    assert get_period_range(date, "quarter") == (
        datetime(2026, 4, 1), datetime(2026, 6, 30, 23, 59, 59, 999999)
    )
    assert get_period_range(date, "year") == (
        datetime(2026, 1, 1), datetime(2026, 12, 31, 23, 59, 59, 999999)
    )
