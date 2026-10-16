import datetime
from types import SimpleNamespace

from compass_common import datetime as date_utils


def test_previous_quarters_end_on_the_last_calendar_day(monkeypatch):
    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls):
            return cls(2026, 5, 12)

    monkeypatch.setattr(date_utils, "datetime", SimpleNamespace(datetime=FixedDateTime, timedelta=datetime.timedelta))

    assert date_utils.get_last_four_quarters_dates() == [
        datetime.datetime(2026, 6, 30),
        datetime.datetime(2026, 3, 31),
        datetime.datetime(2025, 12, 31),
        datetime.datetime(2025, 9, 30),
    ]
