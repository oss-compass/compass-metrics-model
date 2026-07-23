import unittest

from compass_common.dict_utils import deep_get


class DeepGetTest(unittest.TestCase):
    def test_returns_existing_falsy_leaf_values(self):
        for value in (0, False, "", [], {}):
            with self.subTest(value=value):
                self.assertIs(
                    deep_get({"metric": value}, ["metric"], "missing"),
                    value,
                )

    def test_returns_existing_truthy_leaf_value(self):
        self.assertEqual(deep_get({"metric": 7}, ["metric"], "missing"), 7)

    def test_returns_default_for_missing_leaf(self):
        self.assertEqual(deep_get({}, ["metric"], "missing"), "missing")

    def test_returns_default_for_none_leaf(self):
        self.assertEqual(
            deep_get({"metric": None}, ["metric"], "missing"),
            "missing",
        )

    def test_returns_default_for_none_intermediate_value(self):
        data = {"component": None}
        self.assertEqual(
            deep_get(data, ["component", "metric"], "missing"),
            "missing",
        )


if __name__ == "__main__":
    unittest.main()
