# -*- coding: utf-8 -*-
"""contributor_metrics 的键契约回归测试（fake client，无网络依赖）。"""
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from compass_metrics.contributor_metrics import pr_review_contributor_count


class _FakeSearchClient:
    """按调用次序返回预置的 cardinality 计数：total / bot / without_bot。"""

    def __init__(self, counts):
        self._counts = iter(counts)
        self.queries = []

    def search(self, index=None, body=None):
        self.queries.append(body)
        return {
            "aggregations": {
                "contributor_count": {"value": next(self._counts)}
            }
        }


class TestPrReviewContributorCount(unittest.TestCase):
    def test_emits_total_bot_and_without_bot_keys(self):
        """pr_review_contributor_count 的第三个键曾误写为 _bot 的重复键：
        pr_review_contributor_count_without_bot 永不输出、bot 计数被
        without_bot 覆盖（v2 的 contributor_metrics_v2.py:121-123 三个键齐全，
        是意图证明）。"""
        client = _FakeSearchClient([10, 3, 7])
        result = pr_review_contributor_count(
            client, "contributors", datetime(2024, 6, 1), ["https://github.com/a/b"]
        )
        self.assertEqual(result["pr_review_contributor_count"], 10)
        self.assertEqual(result["pr_review_contributor_count_bot"], 3)
        self.assertEqual(result["pr_review_contributor_count_without_bot"], 7)


if __name__ == "__main__":
    unittest.main()
