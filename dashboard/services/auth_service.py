"""Prototype authentication with role-based dashboard access."""
import hashlib
import json
import os
import re
import secrets
import config

FILE = config.USERS_FILE


def _load():
    if not os.path.exists(FILE):
        return []
    with open(FILE, encoding="utf-8") as f:
        return json.load(f)


def _hash(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 120_000).hex()


def register(f):
    required = ("full_name", "admin_id", "email", "org", "phone", "password")
    if any(not str(f[k]).strip() for k in required):
        return "All fields are required."
    if not re.match(r"^\S+@\S+\.\S+$", f["email"]):
        return "Enter a valid email."
    p = f["password"]
    if len(p) < 8 or not re.search(r"[A-Za-z]", p) or not re.search(r"\d", p):
        return "Password needs 8+ characters with letters and numbers."
    if p != f["confirm"]:
        return "Passwords do not match."
    if not f["terms"]:
        return "Please accept the terms and conditions."

    role = str(f.get("role", "OPERATIONS")).upper()
    if role not in {"ADMIN", "OPERATIONS", "SUSTAINABILITY"}:
        role = "OPERATIONS"

    users = _load()
    if any(u["admin_id"].lower() == f["admin_id"].lower() for u in users):
        return "User ID already exists."
    if any(u["email"].lower() == f["email"].lower() for u in users):
        return "Email already registered."

    salt = secrets.token_hex(16)
    users.append({
        k: f[k] for k in ("full_name", "admin_id", "email", "org", "phone")
    } | {"role": role, "salt": salt, "hash": _hash(p, salt)})
    os.makedirs(os.path.dirname(FILE), exist_ok=True)
    with open(FILE, "w", encoding="utf-8") as out:
        json.dump(users, out, indent=2)
    return None


def login(ident, pw):
    for u in _load():
        if ident.lower() in (u["admin_id"].lower(), u["email"].lower()) and secrets.compare_digest(
            u["hash"], _hash(pw, u["salt"])
        ):
            return {
                k: u.get(k, "OPERATIONS" if k == "role" else "")
                for k in ("full_name", "admin_id", "email", "org", "role")
            }
    return None
