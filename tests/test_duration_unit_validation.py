from datetime import datetime, timedelta

import pytest

from compass_common.datetime import get_time_diff_date


def test_unknown_duration_unit_raises_value_error():
    start = datetime(2026, 1, 1)
    with pytest.raises(ValueError, match="Unsupported date type: week"):
        get_time_diff_date(start, start + timedelta(days=7), "week")


def test_supported_units_keep_existing_values():
    start = datetime(2026, 1, 1)
    assert get_time_diff_date(start, start + timedelta(hours=1), "minute") == 60.0
    assert get_time_diff_date(start, start + timedelta(days=30), "month") == 1.0
