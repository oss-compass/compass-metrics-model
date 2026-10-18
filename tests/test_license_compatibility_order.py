"""check_license_compatibility must not depend on the order of the licence list.

The compatibility matrix is consulted per ordered pair, but a pair of licences
is either compatible or it is not: reversing the input order must not change
the verdict.
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


def test_dual_mit_apache_is_compatible_in_both_orders():
    forward = license_metrics.check_license_compatibility(["mit", "apache-2.0"])
    reverse = license_metrics.check_license_compatibility(["apache-2.0", "mit"])

    assert forward["status"] == "compatible"
    assert reverse["status"] == "compatible"


def test_genuinely_incompatible_pair_stays_incompatible_in_both_orders():
    # Someone else's licence still has to be honoured: Apache-2.0 may not be
    # combined with GPL-2.0, whichever way round the pair is asked about.
    forward = license_metrics.check_license_compatibility(["apache-2.0", "gpl-2.0"])
    reverse = license_metrics.check_license_compatibility(["gpl-2.0", "apache-2.0"])

    assert forward["status"] == "incompatible"
    assert reverse["status"] == "incompatible"


def test_unknown_licence_is_still_reported():
    result = license_metrics.check_license_compatibility(["no-such-license-1.0"])

    assert result["status"] == "unknown"
