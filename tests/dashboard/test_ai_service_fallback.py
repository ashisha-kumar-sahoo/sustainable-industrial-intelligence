"""Regression tests for the AI Assistant fallback and failure logging.

Reproduces the reported ``AI Assistant is temporarily unavailable (KeyError)``
UI failure: ``services.ai_service.ask`` indexed columns that exist only in the
synthetic-mode ``alerts()`` schema, not in the PostgreSQL-mode schema.

Dashboard modules are executed in a subprocess with the same isolated import
layout Streamlit uses (``dashboard`` before the project root), because the
project root also contains a ``config/`` namespace package.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BOOTSTRAP = (
    "import sys\n"
    "from pathlib import Path\n"
    "root = Path.cwd()\n"
    "sys.path.insert(0, str(root / 'dashboard'))\n"
    "sys.path.insert(1, str(root))\n"
)

ALERTS = r"""
import pandas as pd

def db_alerts():
    # PostgreSQL-mode alerts() columns: no 'source'/evidence_* columns.
    return pd.DataFrame([dict(
        alert_id="A-ENR-7", facility_id=7, facility_name="SiliconSphere Fab Module",
        sensor_id=12, alert_type="ENERGY_SPIKE", severity="HIGH",
        message="Energy consumption 34% above baseline.",
        value=4100.0, threshold=3000.0,
        reading_ts="2026-10-09 08:00:00", timestamp="2026-10-09 08:00:00",
        zone_id="Zone C", title="SiliconSphere Fab Module - ENERGY_SPIKE",
        insight_text="Energy consumption 34% above baseline.",
        recommendation="Inspect peak-hour HVAC and high-load equipment.",
        deviation_pct=34.0, status="Open",
    )])

def demo_alerts():
    # Synthetic/demo-mode alerts() columns.
    return pd.DataFrame([dict(
        alert_id="A-ENR-7-Zone C", severity="HIGH", source="energy",
        facility_id=7, zone_id="Zone C", timestamp="2026-10-09 08:00:00",
        title="SiliconSphere Fab Module (Zone C) energy +34% vs baseline",
        evidence_actual=4100.0, evidence_expected=3000.0, deviation_pct=34.0,
        recommendation="Inspect peak-hour HVAC and high-load equipment.",
        insight_text="Energy at SiliconSphere Fab Module is about 34% from its recent baseline.",
        status="Open",
    )])

import services.ai_service as ai

def unreachable(*_args, **_kwargs):
    raise ConnectionError("assistant service refused")

ai.post_json = unreachable
"""


def _run(scenario: str, env: dict | None = None) -> str:
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    result = subprocess.run(
        [sys.executable, "-c", BOOTSTRAP + ALERTS + scenario],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=full_env,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    return result.stdout


def test_postgres_schema_without_facility_named():
    _run(
        """
ai.alerts = db_alerts
r = ai.ask("What are today's biggest problems?")
assert r["connected"] is False and r["sample"] is True and r["answer"]
print("OK")
"""
    )


def test_postgres_schema_with_facility_named():
    _run(
        """
ai.alerts = db_alerts
r = ai.ask("What is happening at SiliconSphere Fab Module?")
assert "Energy consumption 34%" in r["answer"]
assert "Suggested action:" in r["answer"]
assert "4100" in r["evidence"] and "3000" in r["evidence"]
print("OK")
"""
    )


def test_demo_schema_with_facility_named():
    _run(
        """
ai.alerts = demo_alerts
r = ai.ask("Tell me about energy at SiliconSphere Fab Module")
assert r["evidence"] == "Actual 4100.0 vs expected 3000.0"
print("OK")
"""
    )


def test_empty_retrieval_returns_clear_message():
    _run(
        """
ai.alerts = lambda: pd.DataFrame()
r = ai.ask("What are today's biggest problems?")
assert "unavailable" in r["answer"].lower()
assert r["evidence"] == ""
print("OK")
"""
    )


def test_null_numeric_and_message_do_not_crash():
    _run(
        """
f = db_alerts()
for column in ("message", "insight_text", "recommendation", "value", "threshold"):
    f.loc[0, column] = None
ai.alerts = lambda: f
r = ai.ask("SiliconSphere Fab Module")
assert isinstance(r["answer"], str) and r["answer"]
assert "nan" not in r["evidence"].lower()
assert "none" not in r["evidence"].lower()
print("OK")
"""
    )


def test_partial_operational_domain_data():
    _run(
        """
f = db_alerts()
f.loc[0, "value"] = None
ai.alerts = lambda: f
r = ai.ask("SiliconSphere Fab Module")
assert "Reading" in r["evidence"] and "3000" in r["evidence"]
print("OK")
"""
    )


def test_successful_response_passes_through():
    _run(
        """
ai.post_json = lambda url, body, timeout=None: {"answer": "ok", "connected": True}
assert ai.ask("hello")["answer"] == "ok"
print("OK")
"""
    )


def test_ask_uses_extended_timeout_for_llm():
    _run(
        """
captured = {}
def fake_post(url, body, timeout=None):
    captured["timeout"] = timeout
    return {"answer": "ok", "connected": True}
ai.post_json = fake_post
ai.ask("What are today's biggest problems?")
assert captured["timeout"] is not None and captured["timeout"] >= 60, captured
print("OK")
"""
    )


def test_ask_timeout_is_configurable():
    _run(
        """
captured = {}
def fake_post(url, body, timeout=None):
    captured["timeout"] = timeout
    return {"answer": "ok", "connected": True}
ai.post_json = fake_post
ai.ask("hello")
assert captured["timeout"] == 42, captured
print("OK")
""",
        env={"ASSISTANT_TIMEOUT": "42"},
    )


def test_safe_logs_traceback_and_key_without_raising(tmp_path):
    log_path = tmp_path / "assistant_errors.log"
    _run(
        """
import utils
utils.st.warning = lambda *_a, **_k: None

def failing_operation():
    raise KeyError("source")

assert utils.safe(failing_operation, default="fallback", label="AI Assistant") == "fallback"
print("OK")
""",
        env={"ASSISTANT_ERROR_LOG": str(log_path)},
    )
    text = log_path.read_text(encoding="utf-8")
    assert "failing_operation" in text
    assert "KeyError" in text
    assert "'source'" in text
    assert "Traceback" in text


def test_safe_handles_unexpected_exception():
    _run(
        """
import utils
utils.st.warning = lambda *_a, **_k: None

def exploding():
    raise RuntimeError("unexpected")

assert utils.safe(exploding, default=42, label="AI Assistant") == 42
print("OK")
"""
    )
