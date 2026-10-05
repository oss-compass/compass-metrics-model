from datetime import datetime

import pytest

from compass_metrics_v2 import developer_metrics_v2, issue_metrics_v2


@pytest.mark.parametrize("module", [developer_metrics_v2, issue_metrics_v2])
@pytest.mark.parametrize("input_date,period,expected_end", [
    (datetime(2026, 2, 15, 14, 30, 12, 123456), "month", datetime(2026, 2, 28, 23, 59, 59)),
    (datetime(2026, 11, 15, 14, 30, 12, 123456), "quarter", datetime(2026, 12, 31, 23, 59, 59)),
    (datetime(2026, 12, 15, 14, 30, 12, 123456), "month", datetime(2026, 12, 31, 23, 59, 59)),
])
def test_period_end_uses_full_final_day(module, input_date, period, expected_end):
    _, actual_end = module.get_period_range(input_date, period)
    assert actual_end == expected_end
