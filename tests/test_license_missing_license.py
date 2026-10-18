"""A repository without any licence must not be reported as licensed.

``license_is_weak`` and ``license_commercial_allowed`` are built with ``all()``
over the detected licences.  ``all([])`` is ``True``, so a repository that has
no licence at all was reported as "all licences are permissive" and "all
licences allow closed source modification" — the opposite of what a missing
licence means.
"""

import sys
import types


def _install_search_stubs():
    """The metric modules import the search clients at module import time."""
    if "elasticsearch" in sys.modules:
        return

    class _Client:
        def __init__(self, *args, **kwargs):
            pass

    elasticsearch = types.ModuleType("elasticsearch")
    elasticsearch.Elasticsearch = _Client
    elasticsearch.RequestsHttpConnection = _Client
    helpers = types.ModuleType("elasticsearch.helpers")
    helpers.bulk = lambda *args, **kwargs: None
    elasticsearch.helpers = helpers
    exceptions = types.ModuleType("elasticsearch.exceptions")

    class NotFoundError(Exception):
        pass

    exceptions.NotFoundError = NotFoundError
    elasticsearch.exceptions = exceptions

    opensearchpy = types.ModuleType("opensearchpy")
    opensearchpy.OpenSearch = _Client
    os_helpers = types.ModuleType("opensearchpy.helpers")
    os_helpers.bulk = lambda *args, **kwargs: None
    os_helpers.scan = lambda *args, **kwargs: None
    opensearchpy.helpers = os_helpers

    sys.modules["elasticsearch"] = elasticsearch
    sys.modules["elasticsearch.helpers"] = helpers
    sys.modules["elasticsearch.exceptions"] = exceptions
    sys.modules["opensearchpy"] = opensearchpy
    sys.modules["opensearchpy.helpers"] = os_helpers


_install_search_stubs()

from compass_metrics import license as license_metrics  # noqa: E402


def _detected(monkeypatch, licenses):
    monkeypatch.setattr(
        license_metrics, "get_license_msg",
        lambda *args, **kwargs: {
            "license_list": list(licenses),
            "osi_license_list": list(licenses),
            "non_osi_licenses": [],
        })


def test_no_licence_is_not_reported_as_permissive(monkeypatch):
    _detected(monkeypatch, [])

    result = license_metrics.license_is_weak(None, "contributors", "v1.0", ["repo"])

    assert result["license_is_weak"] == 0
    assert result["license_list"] == []


def test_no_licence_is_not_reported_as_commercially_allowed(monkeypatch):
    _detected(monkeypatch, [])

    result = license_metrics.license_commercial_allowed(None, "contributors", "v1.0", ["repo"])

    assert result["license_commercial_allowed"] == 0


def test_mit_is_still_reported_as_permissive_and_commercial(monkeypatch):
    _detected(monkeypatch, ["MIT"])

    weak = license_metrics.license_is_weak(None, "contributors", "v1.0", ["repo"])
    commercial = license_metrics.license_commercial_allowed(None, "contributors", "v1.0", ["repo"])

    assert weak["license_is_weak"] == 1
    assert commercial["license_commercial_allowed"] == 1


def test_gpl_is_neither_permissive_nor_commercial(monkeypatch):
    _detected(monkeypatch, ["GPL-3.0"])

    weak = license_metrics.license_is_weak(None, "contributors", "v1.0", ["repo"])
    commercial = license_metrics.license_commercial_allowed(None, "contributors", "v1.0", ["repo"])

    # A strong copyleft licence is the documented counter-example for both
    # flags, so the "no licence" answer must not be confused with it.
    assert weak["license_is_weak"] == 0
    assert commercial["license_commercial_allowed"] == 0
