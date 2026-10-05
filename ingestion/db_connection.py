"""
Database connection bridge for ingestion.

Reuses the central PostgreSQL connection from config.database.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.database import get_connection
except ImportError:
    from ..config.database import get_connection

__all__ = ['get_connection']