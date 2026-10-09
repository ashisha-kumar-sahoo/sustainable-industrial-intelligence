"""Tests for account bootstrap, role assignment, and password handling."""

import json
import sys
from pathlib import Path

# The dashboard is a standalone Streamlit app with its own config.py. Put that
# directory first so imports match the documented launch command.
DASHBOARD_ROOT = Path(__file__).resolve().parents[1] / "dashboard"
sys.path.insert(0, str(DASHBOARD_ROOT))
sys.modules.pop("config", None)

from services import auth_service


def valid_registration(**overrides):
    """Return a valid registration form payload for authentication tests."""
    form_data = {
        "full_name": "Test User",
        "admin_id": "test-user",
        "email": "test@example.com",
        "org": "Test Facility",
        "phone": "1234567890",
        "role": "ADMIN",
        "password": "SecurePass123",
        "confirm": "SecurePass123",
        "terms": True,
    }
    form_data.update(overrides)
    return form_data


def use_temporary_account_store(monkeypatch, tmp_path):
    account_path = tmp_path / "users.json"
    legacy_path = tmp_path / "legacy-users.json"
    monkeypatch.setattr(auth_service, "USERS_FILE", str(account_path))
    monkeypatch.setattr(auth_service, "LEGACY_USERS_FILE", str(legacy_path))
    return account_path


def test_first_registered_account_becomes_admin(monkeypatch, tmp_path):
    account_path = use_temporary_account_store(monkeypatch, tmp_path)

    assert auth_service.available_registration_roles() == ["ADMIN"]
    assert auth_service.register(valid_registration()) is None

    stored_users = json.loads(account_path.read_text(encoding="utf-8"))
    assert stored_users[0]["role"] == "ADMIN"
    assert "SecurePass123" not in account_path.read_text(encoding="utf-8")
    assert auth_service.login("test-user", "SecurePass123")["role"] == "ADMIN"


def test_public_registration_cannot_grant_admin_to_second_account(
    monkeypatch, tmp_path
):
    use_temporary_account_store(monkeypatch, tmp_path)
    assert auth_service.register(valid_registration()) is None

    second_user = valid_registration(
        admin_id="second-user",
        email="second@example.com",
        role="ADMIN",
    )
    error_message = auth_service.register(second_user)

    assert error_message == "Administrator access cannot be granted through public registration."
    assert auth_service.available_registration_roles() == ["OPERATIONS", "SUSTAINABILITY"]


def test_public_registration_can_create_operations_user(monkeypatch, tmp_path):
    account_path = use_temporary_account_store(monkeypatch, tmp_path)
    assert auth_service.register(valid_registration()) is None

    second_user = valid_registration(
        admin_id="operator",
        email="operator@example.com",
        role="OPERATIONS",
    )
    assert auth_service.register(second_user) is None

    stored_users = json.loads(account_path.read_text(encoding="utf-8"))
    assert [user["role"] for user in stored_users] == ["ADMIN", "OPERATIONS"]
    assert auth_service.login("operator@example.com", "SecurePass123")["role"] == "OPERATIONS"
