# -*- coding: utf-8 -*-
"""pr_open_time 分支语义回归测试（patch 数据获取，无网络依赖）。"""
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from compass_metrics.pr_metrics import pr_open_time
from compass_common.datetime import get_time_diff_days


DATE = datetime(2024, 5, 15)
ITEMS = [
    # 开放 PR：更新时间早于指标日（常态）——应计到指标日，而非 updated_at
    {"_source": {"state": "open", "created_at": "2024-02-01T00:00:00",
                 "updated_at": "2024-02-10T00:00:00"}},
    # 已合并 PR：计 created -> merged_at，且不得再落入 closed 分支双计
    {"_source": {"state": "merged", "created_at": "2024-03-01T00:00:00",
                 "merged_at": "2024-03-05T00:00:00",
                 "updated_at": "2024-03-05T00:00:00"}},
    # 已关闭 PR：计 created -> closed_at
    {"_source": {"state": "closed", "created_at": "2024-01-01T00:00:00",
                 "closed_at": "2024-01-20T00:00:00",
                 "updated_at": "2024-01-20T00:00:00"}},
]


class _NoopClient:
    def search(self, index=None, body=None):
        return {"hits": {"total": {"value": 0}}}


class TestPrOpenTime(unittest.TestCase):
    def test_open_merged_closed_each_counted_once_with_correct_end(self):
        """原实现的 `state == 'closed' and closed_at or updated_at < date_str`
        因运算符优先级解析为 (closed and closed_at) or (updated_at < date_str)：
        开放 PR（更新时间早于指标日的常态）被按 updated_at 截断计费、已合并
        PR 在通过 merged 分支后再落进该分支被双计。labs 的
        metrics_model_lab.py:89-90 是正确的分组意图。"""
        with patch("compass_metrics.pr_metrics.get_all_index_data", return_value=ITEMS):
            result = pr_open_time(_NoopClient(), "pr_index", DATE,
                                  ["https://github.com/a/b"])
        expected_samples = [
            get_time_diff_days("2024-02-01T00:00:00", DATE.isoformat()),
            get_time_diff_days("2024-03-01T00:00:00", "2024-03-05T00:00:00"),
            get_time_diff_days("2024-01-01T00:00:00", "2024-01-20T00:00:00"),
        ]
        expected_samples = [x for x in expected_samples if x >= 0]
        expected_avg = sum(expected_samples) / len(expected_samples)
        self.assertAlmostEqual(result["pr_open_time_avg"], expected_avg, places=6)
        self.assertEqual(len(expected_samples), 3)


if __name__ == "__main__":
    unittest.main()
