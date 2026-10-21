# -*- coding: utf-8 -*-
"""contribution_weeks 的 groupby 耗尽回归测试。"""
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from compass_metrics.contributor_metrics import contributor_detail_list


def _record(contributor, contribution=1, contribution_without_observe=1):
    return {
        "contributor": contributor,
        "contribution": contribution,
        "contribution_without_observe": contribution_without_observe,
        "ecological_type": "organization participant",
        "organization": "org",
        "is_bot": False,
        "repo_name": "a/b",
        "contribution_type_list": [
            {"contribution_type": "pc", "contribution": contribution}
        ],
    }


# alice 连续 10 周每周有记录；bob 单周重贡献（吸收 core 名额）
ITEMS = [_record("alice") for _ in range(10)] + [
    _record("bob", contribution=10000, contribution_without_observe=10000)
]


class _NoopClient:
    def search(self, index=None, body=None):
        return {"hits": {"total": {"value": 0}}}


class TestContributionWeeks(unittest.TestCase):
    def test_contribution_weeks_counts_group_size(self):
        """line 518 的 for item in list(group) 已耗尽 groupby 迭代器，
        line 546 的 len(list(group)) 恒为 0：contribution_weeks 永远是 0，
        get_regular_contributor 的"参与 3/4 周数即常贡献者"规则成为死代码，
        满足该规则的贡献者被误分类为 casual。"""
        with patch(
            "compass_metrics.contributor_metrics.get_contributor_list",
            return_value=ITEMS,
        ):
            result = contributor_detail_list(
                _NoopClient(), "contributors_enriched",
                datetime(2024, 5, 10), ["https://github.com/a/b"],
                from_date=datetime(2024, 3, 1),
            )
        by_name = {
            item["contributor"]: item
            for item in result["contributor_detail_list"]
        }
        self.assertEqual(by_name["alice"]["contribution_weeks"], 10)
        self.assertNotEqual(by_name["alice"]["mileage_type"], "casual")


if __name__ == "__main__":
    unittest.main()
