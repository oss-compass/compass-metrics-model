# -*- coding: utf-8 -*-
"""ratio 三元式守卫变量的回归测试：count==0 且 total>0 时应得 0.0 而非 None。"""
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from compass_metrics import issue_metrics, pr_metrics

DATE = datetime(2024, 5, 15)
REPOS = ["https://github.com/a/b"]


class TestRatioZeroCount(unittest.TestCase):
    def _case(self, module, ratio_fn, count_key, total_key, expected_key):
        with patch.object(module, count_key, return_value={count_key: 0}), \
             patch.object(module, total_key, return_value={total_key: 50}):
            result = ratio_fn(None, "index", DATE, REPOS)
        self.assertEqual(result[expected_key], 0.0)

    def test_issue_unresponsive_ratio_zero_count_is_zero(self):
        """count==0、total==50（50 个新 issue 零个无响应——健康常态）：
        ratio 应为 0.0，而非 None（"无数据"）。原实现的守卫写反了变量
        （v2 的 issue_metrics_v2.py:140 守卫 total，是正确形态）。"""
        self._case(issue_metrics, issue_metrics.issue_unresponsive_ratio,
                   "issue_unresponsive_count", "issue_count",
                   "issue_unresponsive_ratio")

    def test_issue_completion_ratio_zero_count_is_zero(self):
        self._case(issue_metrics, issue_metrics.issue_completion_ratio,
                   "create_close_issue_count", "issue_count",
                   "issue_completion_ratio")

    def test_issue_completion_ratio_year_zero_count_is_zero(self):
        self._case(issue_metrics, issue_metrics.issue_completion_ratio_year,
                   "create_close_issue_count", "issue_count",
                   "issue_completion_ratio_year")

    def test_pr_unresponsive_ratio_zero_count_is_zero(self):
        self._case(pr_metrics, pr_metrics.pr_unresponsive_ratio,
                   "pr_unresponsive_count", "pr_count",
                   "pr_unresponsive_ratio")

    def test_zero_total_is_still_none(self):
        """total==0（无数据）仍返回 None 的既有语义保持。"""
        with patch.object(issue_metrics, "issue_unresponsive_count",
                          return_value={"issue_unresponsive_count": 0}), \
             patch.object(issue_metrics, "issue_count",
                          return_value={"issue_count": 0}):
            result = issue_metrics.issue_unresponsive_ratio(None, "index", DATE, REPOS)
        self.assertIsNone(result["issue_unresponsive_ratio"])


if __name__ == "__main__":
    unittest.main()
