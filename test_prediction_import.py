import subprocess
import sys


def test_prediction_module_import_does_not_require_optional_runtime_dependency():
    result = subprocess.run(
        [sys.executable, "-c", "import compass_prediction.oss_prediction"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
