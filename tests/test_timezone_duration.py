from datetime import datetime, timezone, timedelta

from compass_common.datetime import get_time_diff_date


def test_duration_uses_timezone_offsets_in_timestamp_strings():
    assert get_time_diff_date("2026-01-01T00:00:00+02:00", "2025-12-31T23:00:00Z", "hour") == 1.0


def test_duration_accepts_aware_datetime_and_timestamp_string():
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=2)))
    assert get_time_diff_date(start, "2025-12-31T23:00:00Z", "hour") == 1.0
