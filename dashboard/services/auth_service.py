"""Local prototype authentication with safe account-file handling.

The first registered account becomes the initial administrator. Later public
registrations may choose Operations or Sustainability, but cannot grant
administrator privileges to themselves. This is prototype authentication,
not a substitute for an identity provider in a production deployment.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets

import config

USERS_FILE = config.USERS_FILE
LEGACY_USERS_FILE = os.path.join(config.BASE_DIR, "users.json")
PASSWORD_ITERATIONS = 120_000
ALLOWED_PUBLIC_ROLES = {"OPERATIONS", "SUSTAINABILITY"}


def _load() -> list[dict]:
    """Load local accounts, migrating a legacy project-local file if needed."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, encoding="utf-8") as user_file:
            return json.load(user_file)

    # Preserve any accounts created by an earlier version of the prototype.
    if os.path.exists(LEGACY_USERS_FILE):
        with open(LEGACY_USERS_FILE, encoding="utf-8") as legacy_file:
            legacy_users = json.load(legacy_file)
        if legacy_users:
            _save(legacy_users)
            return legacy_users

    return []


def _save(users: list[dict]) -> None:
    """Write account records outside the project repository."""
    user_directory = os.path.dirname(USERS_FILE)
    os.makedirs(user_directory, exist_ok=True)

    temporary_path = f"{USERS_FILE}.tmp"
    with open(temporary_path, "w", encoding="utf-8") as user_file:
        json.dump(users, user_file, indent=2)
    os.replace(temporary_path, USERS_FILE)


def _hash(password: str, salt: str) -> str:
    """Hash a password with a per-user salt and PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        PASSWORD_ITERATIONS,
    ).hex()


def available_registration_roles() -> list[str]:
    """Return roles available on the public registration form."""
    if not _load():
        return ["ADMIN"]
    return sorted(ALLOWED_PUBLIC_ROLES)


def register(form_data: dict) -> str | None:
    """Validate and create an account; return an error message on failure."""
    required_fields = (
        "full_name",
        "admin_id",
        "email",
        "org",
        "phone",
        "password",
    )
    if any(not str(form_data.get(field, "")).strip() for field in required_fields):
        return "All fields are required."

    email = str(form_data["email"]).strip()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return "Enter a valid email."

    password = str(form_data["password"])
    if (
        len(password) < 8
        or not re.search(r"[A-Za-z]", password)
        or not re.search(r"\d", password)
    ):
        return "Password needs 8+ characters with letters and numbers."

    if password != form_data.get("confirm"):
        return "Passwords do not match."
    if not form_data.get("terms"):
        return "Please accept the terms and conditions."

    users = _load()
    admin_id = str(form_data["admin_id"]).strip()
    if any(user.get("admin_id", "").casefold() == admin_id.casefold() for user in users):
        return "User ID already exists."
    if any(user.get("email", "").casefold() == email.casefold() for user in users):
        return "Email already registered."

    requested_role = str(form_data.get("role", "OPERATIONS")).upper()
    if not users:
        # Bootstrap exactly one initial administrator on a fresh installation.
        assigned_role = "ADMIN"
    elif requested_role in ALLOWED_PUBLIC_ROLES:
        assigned_role = requested_role
    else:
        return "Administrator access cannot be granted through public registration."

    salt = secrets.token_hex(16)
    account = {
        field: str(form_data[field]).strip()
        for field in ("full_name", "admin_id", "email", "org", "phone")
    }
    account.update(
        {
            "role": assigned_role,
            "salt": salt,
            "hash": _hash(password, salt),
        }
    )
    users.append(account)
    _save(users)
    return None


def login(identifier: str, password: str) -> dict | None:
    """Authenticate by user ID or email without exposing password hashes."""
    if not isinstance(identifier, str) or not isinstance(password, str):
        return None

    normalized_identifier = identifier.casefold()
    for user in _load():
        user_id = str(user.get("admin_id", "")).casefold()
        email = str(user.get("email", "")).casefold()
        stored_hash = user.get("hash")
        salt = user.get("salt")

        if not stored_hash or not salt:
            continue
        if normalized_identifier not in {user_id, email}:
            continue
        if not secrets.compare_digest(stored_hash, _hash(password, salt)):
            continue

        return {
            field: user.get(field, "OPERATIONS" if field == "role" else "")
            for field in ("full_name", "admin_id", "email", "org", "role")
        }

    return None
