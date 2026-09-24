"""Make the packages of this repository importable for the test run.

pytest only puts the directory of a test file on sys.path, so without this file
``import compass_common`` would fail when the suite is started from anywhere
else than the repository root.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
