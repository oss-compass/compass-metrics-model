import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compass_common.dict_utils import deep_get


def test_deep_get_returns_present_zero():
    # A stored value of 0 must be returned as-is, not replaced by the default.
    data = {"a": {"b": 0}}
    assert deep_get(data, ["a", "b"], default=None) == 0


def test_deep_get_returns_present_false():
    data = {"a": {"b": False}}
    assert deep_get(data, ["a", "b"], default=None) is False


def test_deep_get_returns_present_empty_list():
    data = {"a": {"b": []}}
    assert deep_get(data, ["a", "b"], default=None) == []


def test_deep_get_returns_present_empty_string():
    data = {"a": {"b": ""}}
    assert deep_get(data, ["a", "b"], default=None) == ""


def test_deep_get_returns_present_value_when_nonzero():
    data = {"a": {"b": 5}}
    assert deep_get(data, ["a", "b"], default=None) == 5


def test_deep_get_returns_default_for_missing_path():
    data = {"a": {}}
    assert deep_get(data, ["a", "b"], default="missing") == "missing"


def test_deep_get_returns_default_for_missing_first_key():
    data = {}
    assert deep_get(data, ["a", "b"], default="missing") == "missing"
