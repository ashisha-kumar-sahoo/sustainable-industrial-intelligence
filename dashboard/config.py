"""Central dashboard configuration.

PostgreSQL is the source of truth when DATABASE_URL is configured. The facility
profile selector demonstrates how the same dashboard can be configured for an
industrial estate or a hospital without changing the analytics architecture.
"""
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "Sustainable Industrial Intelligence"
APP_ICON = "🏭"
APP_LAYOUT = "wide"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
# Keep account records outside the source tree so passwords and personal
# details are not accidentally committed to GitHub.
DEFAULT_USER_DIRECTORY = os.path.join(
    os.path.expanduser("~"), ".sustainable-industrial-intelligence"
)
USERS_FILE = os.getenv(
    "USERS_FILE",
    os.path.join(DEFAULT_USER_DIRECTORY, "users.json"),
)

_database_url = os.getenv("DATABASE_URL", "").strip()
if _database_url and "CHANGE_ME" not in _database_url:
    DB = _database_url
elif os.getenv("DB_PASSWORD"):
    # Build a correctly escaped SQLAlchemy URL from the canonical DB_* settings.
    from sqlalchemy.engine import URL
    DB = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "smart_industrial_estate"),
    )
else:
    DB = None
MODE = "PostgreSQL — source of truth" if DB else "Synthetic / sensor simulation (demo fallback)"


def _table(env_name, default):
    value = os.getenv(env_name, default).strip()
    if not value.replace("_", "").isalnum() or value[0].isdigit():
        raise ValueError(f"Invalid SQL identifier in {env_name}: {value!r}")
    return value


LAT = float(os.getenv("ESTATE_LAT", 20.29))
LON = float(os.getenv("ESTATE_LON", 85.84))


def assistant_url():
    return os.getenv("ASSISTANT_URL", "http://127.0.0.1:8000/api/ask").strip()


def simulation_url():
    return os.getenv("SIMULATION_URL")


# Mirrors the seeded PostgreSQL facility master so the dashboard remains
# usable before the database connection is established.
_FACILITIES = [
    (1, "Precision Forge Unit 1", "Zone A"),
    (2, "Metro Cold Storage Block B", "Zone A"),
    (3, "NovaChem Reactor Hall", "Zone B"),
    (4, "FreshRoots Processing Line", "Zone B"),
    (5, "LoomCraft Spinning Mill", "Zone B"),
    (6, "Velocity Assembly Plant", "Zone C"),
    (7, "SiliconSphere Fab Module", "Zone C"),
    (8, "PackRight Converting Line", "Zone C"),
    (9, "Precision Forge Unit 2", "Zone A"),
    (10, "AgriStore Cold Chain Depot", "Zone D"),
    (11, "GreenLeaf Juice Plant", "Zone D"),
    (12, "ChemCore Formulation Unit", "Zone B"),
    (13, "WeaveWorld Dyeing Unit", "Zone E"),
    (14, "AutoTech Stamping Unit", "Zone C"),
    (15, "ChipVerse Wafer Facility", "Zone E"),
    (16, "BoxCraft Packaging Unit", "Zone D"),
    (17, "SteelCraft Rolling Mill", "Zone E"),
    (18, "MetroCold Annexe", "Zone A"),
    (19, "PureWater Treatment Plant", "Zone E"),
    (20, "TextileFinishing Unit", "Zone B"),
]
FAC = pd.DataFrame(_FACILITIES, columns=["facility_id", "name", "zone"])
FAC["dlat"] = [(i % 5 - 2) * 0.0015 for i in range(len(FAC))]
FAC["dlon"] = [(i // 5 - 2) * 0.002 for i in range(len(FAC))]
FAC["lat"] = LAT + FAC["dlat"]
FAC["lon"] = LON + FAC["dlon"]
FAC["zones"] = FAC["zone"].map(lambda z: [z])

DS = {
    "energy": ("kwh", 2600, 0.6),
    "water": ("kl", 60, 0.5),
    "waste": ("fill_pct", 55, 0.3),
    "environment": ("aqi", 70, 0.35),
    "equipment": ("health_score", 90, 0.2),
    "traffic": ("vehicles", 90, 0.8),
    "safety": ("incidents", 0.3, 0.5),
}

# Kept for compatibility with existing dashboard modules. DB mode does not use
# these names as physical PostgreSQL table names.
RAW_TABLES = {ds: _table(f"{ds.upper()}_TABLE", ds) for ds in DS}
AI_RESULTS_TABLE = _table("AI_RESULTS_TABLE", "ai_results")
FORECASTS_TABLE = _table("FORECASTS_TABLE", "forecasts")
ALERTS_TABLE = _table("ALERTS_TABLE", "alerts")

RECO = {
    "energy": "Inspect peak-hour HVAC and high-load equipment.",
    "water": "Check for leakage or abnormal process usage.",
    "waste": "Schedule priority waste collection.",
    "environment": "Inspect emission sources and ventilation.",
    "equipment": "Schedule preventive machine inspection.",
    "traffic": "Review gate/parking management and truck scheduling.",
    "safety": "Review incident causes and inspect the affected zone.",
}

CONTRACT = [
    "source", "facility_id", "zone_id", "timestamp", "actual_value",
    "expected_value", "deviation_pct", "severity", "is_anomaly"
]

ZONES = sorted(FAC["zone"].unique().tolist())

KP = {
    "energy": ("Energy", "kWh", "sum"),
    "water": ("Water", "L", "sum"),
    "waste": ("Waste fill", "%", "mean"),
    "environment": ("AQI", "", "mean"),
    "traffic": ("Traffic", "veh/24h", "sum"),
    "equipment": ("Equipment", "", "mean"),
    "safety": ("Safety incidents", "", "sum"),
}

EXTRA = {
    "environment": ["pm25", "pm10", "co2", "no2"],
    "equipment": ["utilization_pct", "vibration_mm_s"],
    "traffic": ["trucks", "avg_speed_kmh", "parking_occupancy_pct"],
    "safety": ["severity_level"],
}

ACT = {
    "energy": ["Reduce HVAC energy", "Shift peak load"],
    "water": ["Fix leakage", "Recycle process water"],
    "waste": ["Increase collection frequency"],
    "traffic": ["Stagger truck arrivals"],
    "environment": ["Reduce peak-hour emissions"],
    "equipment": ["Preventive maintenance"],
    "safety": ["Extra zone inspections"],
}

NAV_ICONS = {
    "Overview": "📊", "Resources": "⚡", "Environment": "🌿",
    "Operations": "🏭", "Alerts": "🚨", "AI Assistant": "💬",
    "Recommendations": "✅", "Scenario Simulation": "📝",
    "Raw Data Explorer": "📁",
}

FACILITY_PROFILES = {
    "Industrial Estate": {
        "icon": "🏭",
        "description": "Manufacturing, logistics and utility estate profile.",
        "domains": ["energy", "water", "waste", "environment", "traffic", "equipment", "safety"],
    },
    "Hospital": {
        "icon": "🏥",
        "description": "Hospital configuration using the same dashboard/analytics architecture.",
        "domains": ["energy", "water", "waste", "environment", "equipment", "safety"],
    },
}

def current_profile():
    """Return the selected facility profile, with environment/default fallback."""
    selected = os.getenv("FACILITY_PROFILE", "Industrial Estate")
    try:
        import streamlit as st
        selected = st.session_state.get("facility_profile", selected)
    except Exception:
        pass
    return selected if selected in FACILITY_PROFILES else "Industrial Estate"


def active_domains():
    """Domains enabled for the selected facility profile."""
    return list(FACILITY_PROFILES[current_profile()]["domains"])

