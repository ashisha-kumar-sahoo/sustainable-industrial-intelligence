"""Compatibility import for the single shared PostgreSQL connection helper."""
from config.database import get_connection

__all__ = ["get_connection"]
