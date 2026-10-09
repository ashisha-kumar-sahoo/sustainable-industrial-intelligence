"""Smoke-test dashboard services in the same isolated import layout as Streamlit."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_ROOT = PROJECT_ROOT / "dashboard"

# Dashboard services require Streamlit; skip cleanly in minimal CI environments.
pytest.importorskip("streamlit")


def test_dashboard_services_import_in_runtime_layout():
    code = r"""
import sys
from pathlib import Path
root = Path.cwd()
sys.path.insert(0, str(root / "dashboard"))
sys.path.insert(1, str(root))
from services import auth_service, database_service, resource_service, alert_service, simulation_service
assert hasattr(auth_service, "login") and hasattr(auth_service, "register")
assert database_service is not None
assert resource_service is not None
assert alert_service is not None
assert simulation_service is not None
print("DASHBOARD_SERVICES_IMPORT_OK")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert "DASHBOARD_SERVICES_IMPORT_OK" in result.stdout
