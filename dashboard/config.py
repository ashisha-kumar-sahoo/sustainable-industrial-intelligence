"""Central configuration and constants for the dashboard.

Moved from: data_service.py (environment variables, facility master data, dataset definitions, thresholds/recommendation texts),
pages.py (KP, EXTRA, ACT) and app.py (page title/icon, navigation icons). No secrets live here: DATABASE_URL, ESTATE_LAT/LON,
ASSISTANT_URL and SIMULATION_URL are still read from the environment exactly as before.
"""
import os
import pandas as pd

# ---- application
APP_TITLE = "Sustainable Industrial Intelligence"; APP_ICON = "🏭"; APP_LAYOUT = "wide"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
USERS_FILE = os.path.join(BASE_DIR, "users.json")  # prototype auth store (was sii/users.json next to auth.py)

# ---- environment-driven settings (same variables and defaults as before)
DB = os.getenv("DATABASE_URL"); MODE = "PostgreSQL — team data" if DB else "Synthetic / sensor simulation (sample data)"

# PostgreSQL table names are configurable so Member 2/3/4 can keep their own schema.
# Defaults match the dashboard data contract. Only simple SQL identifiers are accepted.
def _table(env_name, default):
    value = os.getenv(env_name, default).strip()
    if not value.replace("_", "").isalnum() or value[0].isdigit():
        raise ValueError(f"Invalid SQL table name in {env_name}: {value!r}")
    return value


LAT, LON = float(os.getenv("ESTATE_LAT", 20.29)), float(os.getenv("ESTATE_LON", 85.84))
def assistant_url(): return os.getenv("ASSISTANT_URL")      # read at call time, as before
def simulation_url(): return os.getenv("SIMULATION_URL")    # read at call time, as before

# ---- facility master data and dataset definitions
FAC = pd.DataFrame([("F001", "Factory A", .003, -.004, ["Z01", "Z02"]), ("F002", "Factory B", .0035, .0005, ["Z03", "Z04"]), ("F003", "Factory C", .003, .005, ["Z05", "Z06"]),
                    ("F004", "Main Gate & Parking", -.003, -.004, ["Z07", "Z08"]), ("F005", "Utility Plant", -.003, .005, ["Z09", "Z10"])], columns=["facility_id", "name", "dlat", "dlon", "zones"])
FAC["lat"], FAC["lon"] = LAT + FAC["dlat"], LON + FAC["dlon"]
DS = {"energy": ("kwh", 2600, .6), "water": ("kl", 60, .5), "waste": ("fill_pct", 55, .3), "environment": ("aqi", 70, .35), "equipment": ("temp_c", 68, .2), "traffic": ("vehicles", 90, .8), "safety": ("incidents", .3, .5)}
RAW_TABLES = {ds: _table(f"{ds.upper()}_TABLE", ds) for ds in DS}
AI_RESULTS_TABLE = _table("AI_RESULTS_TABLE", "ai_results")
FORECASTS_TABLE = _table("FORECASTS_TABLE", "forecasts")
ALERTS_TABLE = _table("ALERTS_TABLE", "alerts")
INJ = {("energy", "F002"): (6, 1.32), ("environment", "F003"): (8, 1.5), ("equipment", "F001"): (4, 1.3), ("water", "F005"): (6, 1.25), ("waste", "F005"): (12, 1.4), ("traffic", "F004"): (5, 1.6)}
RECO = {"energy": "Inspect peak-hour HVAC and high-load equipment.", "water": "Check for leakage or abnormal process usage.", "waste": "Schedule priority waste collection.", "environment": "Inspect emission sources and ventilation.",
        "equipment": "Schedule machine inspection.", "traffic": "Review gate/parking management and truck scheduling.", "safety": "Review incident causes and inspect the zone."}
CONTRACT = ["source", "facility_id", "zone_id", "timestamp", "actual_value", "expected_value", "deviation_pct", "severity", "is_anomaly"]
ZONES = [z for l in FAC["zones"] for z in l]

# ---- presentation constants used by pages/services (moved from pages.py)
KP = {"energy": ("Energy", "kWh", "sum"), "water": ("Water", "KL", "sum"), "waste": ("Waste fill", "%", "mean"), "environment": ("AQI", "", "mean"), "traffic": ("Traffic", "veh/24h", "sum"), "equipment": ("Equipment temp", "°C", "mean"), "safety": ("Safety incidents", "", "sum")}
EXTRA = {"environment": ["pm25", "pm10", "co2", "no2"], "equipment": ["utilization_pct", "vibration_mm_s"], "traffic": ["trucks", "avg_speed_kmh", "parking_occupancy_pct"], "safety": ["severity_level"]}
ACT = {"energy": ["Reduce HVAC energy", "Shift peak load"], "water": ["Fix leakage", "Recycle process water"], "waste": ["Increase collection frequency"], "traffic": ["Stagger truck arrivals"], "environment": ["Reduce peak-hour emissions"], "equipment": ["Preventive maintenance"], "safety": ["Extra zone inspections"]}

# ---- navigation icons (moved from app.py)
NAV_ICONS = {"Overview": "📊", "Resources": "⚡", "Environment": "🌿", "Operations": "🏭", "Alerts": "🚨", "AI Assistant": "💬", "Recommendations": "✅", "Scenario Simulation": "📝", "Raw Data Explorer": "📁"}
