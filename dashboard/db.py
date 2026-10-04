"""PostgreSQL connection helpers used by the dashboard data layer."""
import pandas as pd
import config


def get_engine():
    if not config.DB:
        raise RuntimeError("DATABASE_URL is not configured; dashboard is using synthetic data mode.")
    from sqlalchemy import create_engine
    return create_engine(config.DB, pool_pre_ping=True)


def query(q, **p):
    from sqlalchemy import text
    with get_engine().connect() as c:
        return pd.read_sql(text(q), c, params=p)


def check_connection():
    """Return (ok, message) without exposing credentials."""
    if not config.DB:
        return False, "DATABASE_URL is not configured"
    try:
        query("SELECT 1 AS ok")
        return True, "PostgreSQL connection is working"
    except Exception as exc:
        return False, f"PostgreSQL connection failed: {type(exc).__name__}: {exc}"
