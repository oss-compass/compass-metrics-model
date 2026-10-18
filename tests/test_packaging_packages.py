"""Every first-party module directory must be declared as a package.

``setup.py`` currently uses ``setuptools.find_packages()``, which only reports
directories that contain an ``__init__.py``.  Most of this project is spread
over plain directories, so the published wheel silently loses modules that the
packaged modules import.
"""

import os
import runpy

import setuptools

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIRST_PARTY_PACKAGES = [
    "compass_common",
    "compass_contributor",
    "compass_metrics",
    "compass_metrics_model",
    "compass_metrics_v2",
    "compass_model",
    "compass_model_v2",
    "compass_prediction",
]


def _declared_packages():
    """Run setup.py with setuptools.setup() captured, and return ``packages``."""
    captured = {}
    original_setup = setuptools.setup
    original_cwd = os.getcwd()
    setuptools.setup = lambda **kwargs: captured.update(kwargs)
    os.chdir(REPO_ROOT)
    try:
        runpy.run_path(os.path.join(REPO_ROOT, "setup.py"), run_name="__main__")
    finally:
        setuptools.setup = original_setup
        os.chdir(original_cwd)

    assert "packages" in captured, "setup.py must pass packages= to setup()"
    return set(captured["packages"])


def _module_directories():
    """Directories inside the first-party packages that contain Python modules."""
    directories = set()
    for top_level in FIRST_PARTY_PACKAGES:
        for root, dirnames, filenames in os.walk(os.path.join(REPO_ROOT, top_level)):
            dirnames[:] = [name for name in dirnames if name != "__pycache__"]
            if not any(name.endswith(".py") for name in filenames):
                continue
            relative = os.path.relpath(root, REPO_ROOT).replace(os.sep, ".")
            directories.add(relative)
    return directories


def test_every_module_directory_is_declared_as_a_package():
    declared = _declared_packages()
    missing = sorted(_module_directories() - declared)

    assert missing == [], "module directories that setup.py does not ship: %s" % missing


def test_import_of_the_v2_model_module_stays_packaged():
    # compass_model/base_metrics_model_v2.py imports compass_metrics_v2, so a
    # wheel without compass_metrics_v2 is broken for any user of the v2 model.
    declared = _declared_packages()

    assert "compass_model" in declared
    assert "compass_metrics_v2" in declared
