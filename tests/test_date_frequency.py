from compass_common.datetime import get_date_list_by_period


def test_daily_and_weekly_periods_use_the_requested_frequency():
    days = get_date_list_by_period("2026-01-01", "2026-01-03", "day")
    weeks = get_date_list_by_period("2026-01-01", "2026-01-19", "week")

    assert [day.date().isoformat() for day in days] == ["2026-01-01", "2026-01-02", "2026-01-03"]
    assert [day.date().isoformat() for day in weeks] == ["2026-01-05", "2026-01-12", "2026-01-19"]
