"""(Moved from auth.py; logic unchanged, only the users.json path now comes from config.)
Prototype auth: users.json with PBKDF2-hashed passwords. Replace with PostgreSQL + secure sessions/JWT for production."""
import json, os, hashlib, secrets, re
import config
FILE = config.USERS_FILE  # dashboard/users.json
def _load(): return json.load(open(FILE)) if os.path.exists(FILE) else []
def _hash(pw, salt): return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 120_000).hex()
def register(f):
    if any(not str(f[k]).strip() for k in ("full_name", "admin_id", "email", "org", "phone", "password")): return "All fields are required."
    if not re.match(r"^\S+@\S+\.\S+$", f["email"]): return "Enter a valid email."
    p = f["password"]
    if len(p) < 8 or not re.search(r"[A-Za-z]", p) or not re.search(r"\d", p): return "Password needs 8+ characters with letters and numbers."
    if p != f["confirm"]: return "Passwords do not match."
    if not f["terms"]: return "Please accept the terms and conditions."
    users = _load()
    if any(u["admin_id"].lower() == f["admin_id"].lower() for u in users): return "Admin ID already exists."
    if any(u["email"].lower() == f["email"].lower() for u in users): return "Email already registered."
    salt = secrets.token_hex(16)
    users.append({k: f[k] for k in ("full_name", "admin_id", "email", "org", "phone")} | {"salt": salt, "hash": _hash(p, salt)})
    json.dump(users, open(FILE, "w"), indent=2)
    return None
def login(ident, pw):
    for u in _load():
        if ident.lower() in (u["admin_id"].lower(), u["email"].lower()) and secrets.compare_digest(u["hash"], _hash(pw, u["salt"])):
            return {k: u[k] for k in ("full_name", "admin_id", "email", "org")}
    return None
