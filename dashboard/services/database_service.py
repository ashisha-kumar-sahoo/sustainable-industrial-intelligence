"""Dashboard data access.

DB mode maps the real PostgreSQL schema to one stable dashboard contract.
Synthetic mode remains available as a clearly labelled fallback.
"""
import numpy as np
import pandas as pd
import streamlit as st

from config import DB, DS, FAC, CONTRACT, active_domains
from db import query


def _zone_from_location(location):
    if not isinstance(location, str):
        return "Unknown"
    return location.split(" - ", 1)[0]


def _attach_facility_names(df):
    if df.empty:
        return df
    if "facility_name" not in df.columns:
        names = FAC.set_index("facility_id")["name"].to_dict()
        df["facility_name"] = df["facility_id"].map(names)
    if "zone_id" not in df.columns:
        zones = FAC.set_index("facility_id")["zone"].to_dict()
        df["zone_id"] = df["facility_id"].map(zones).fillna("Unknown")
    return df


@st.cache_data
def synthetic_data():
    r = np.random.default_rng(7)
    ts = pd.date_range(end=pd.Timestamp.now().floor("h"), periods=168, freq="h")
    day = np.maximum(0, np.sin((ts.hour.values - 5) / 14 * np.pi))
    out = {}
    for ds, (m, base, amp) in DS.items():
        parts = []
        for fi, row in FAC.iterrows():
            f = int(row["facility_id"])
            z = row["zone"]
            v = base * (.8 + .03 * fi) * (1 - amp / 2 + amp * day) * r.normal(1, .04, 168)
            if ds == "safety":
                v = r.poisson(.25, 168).astype(float)
            d = pd.DataFrame({"timestamp": ts, "facility_id": f, "zone_id": z, m: v.round(1)})
            if ds == "waste":
                d["bin_id"] = f"BIN-{f:03d}"
                d[m] = d[m].clip(0, 100)
            if ds == "environment":
                d["pm25"] = (v * .55).round(1)
                d["pm10"] = (v * .9).round(1)
                d["co2"] = (420 + v * 2).round(0)
                d["no2"] = (v * .3).round(1)
            if ds == "equipment":
                d["machine_id"] = f"M{f:03d}"
                d["vibration_mm_s"] = (v * .06 + r.normal(0, .1, 168)).round(2)
                d["runtime_h"] = np.arange(168) + 500 * f
                d["utilization_pct"] = (60 + 30 * day).round(0)
            if ds == "traffic":
                d["trucks"] = (v * .25).round(0)
                d["avg_speed_kmh"] = (45 - v * .15).round(1)
                d["parking_occupancy_pct"] = np.minimum(100, v * .7).round(0)
            if ds == "safety":
                d["severity_level"] = np.where(v > 0, r.integers(1, 4, 168), 0)
            parts.append(d)
        out[ds] = pd.concat(parts, ignore_index=True)
    return out


def _db_raw(ds, fac=None, zone=None, start=None, end=None, limit=5000):
    # All queries use the actual public schema. Values are renamed into the
    # dashboard's stable timestamp/facility/zone contract.
    queries = {
        "energy": """
            SELECT r.reading_ts AS timestamp, r.facility_id,
                   f.facility_name, f.location AS facility_location,
                   r.energy_consumption_kwh AS kwh,
                   r.voltage, r.current, r.power_factor, r.peak_demand_kw
            FROM public.energy_readings r
            JOIN public.facilities f USING (facility_id)
            WHERE 1=1
        """,
        "water": """
            SELECT r.reading_ts AS timestamp, r.facility_id,
                   f.facility_name, f.location AS facility_location,
                   r.water_consumption_liters AS kl, r.water_pressure,
                   r.water_temperature, r.flow_rate
            FROM public.water_readings r
            JOIN public.facilities f USING (facility_id)
            WHERE 1=1
        """,
        "waste": """
            SELECT r.reading_ts AS timestamp, r.sensor_id, r.facility_id,
                   f.facility_name, f.location AS facility_location,
                   r.fill_level_percent AS fill_pct,
                   r.fill_rate_percent_per_hour, r.waste_quantity_kg,
                   r.recyclable_quantity_kg, r.hazardous_quantity_kg,
                   r.waste_type, r.disposal_method
            FROM public.waste_readings r
            JOIN public.facilities f USING (facility_id)
            WHERE 1=1
        """,
        "environment": """
            SELECT r.reading_ts AS timestamp, r.facility_id,
                   f.facility_name, f.location AS facility_location,
                   r.aqi, r.pm25, r.pm10, r.co2, r.no2, r.so2,
                   r.temperature, r.humidity
            FROM public.air_quality_readings r
            JOIN public.facilities f USING (facility_id)
            WHERE 1=1
        """,
        "traffic": """
            SELECT r.reading_ts AS timestamp, r.facility_id,
                   f.facility_name, f.location AS facility_location,
                   r.vehicle_count AS vehicles, r.heavy_vehicle_count AS trucks,
                   r.average_speed_kmph AS avg_speed_kmh,
                   r.lane_occupancy_percent AS parking_occupancy_pct,
                   r.congestion_level
            FROM public.traffic_readings r
            JOIN public.facilities f USING (facility_id)
            WHERE 1=1
        """,
        "equipment": """
            SELECT r.reading_ts AS timestamp, r.sensor_id, r.facility_id,
                   f.facility_name, f.location AS facility_location,
                   r.equipment_id AS machine_id,
                   r.temperature_c AS temperature,
                   r.vibration_mms AS vibration_mm_s,
                   r.operating_hours,
                   r.utilization_percent AS utilization_pct,
                   r.equipment_status,
                   CASE r.equipment_status
                       WHEN 'NORMAL' THEN 100
                       WHEN 'WARNING' THEN 60
                       WHEN 'CRITICAL' THEN 25
                       WHEN 'OFFLINE' THEN 0
                       ELSE 50
                   END AS health_score
            FROM public.equipment_readings r
            JOIN public.facilities f USING (facility_id)
            WHERE 1=1
        """,
        "safety": """
            SELECT r.reading_ts AS timestamp, r.sensor_id, r.facility_id,
                   f.facility_name, f.location AS facility_location,
                   CASE WHEN r.incident_type IS NOT NULL
                              AND r.incident_type <> 'ROUTINE_MONITORING'
                        THEN 1 ELSE 0 END AS incidents,
                   CASE r.severity
                       WHEN 'Critical' THEN 4
                       WHEN 'High' THEN 3
                       WHEN 'Medium' THEN 2
                       WHEN 'Low' THEN 1
                       ELSE 0
                   END AS severity_level,
                   r.incident_type, r.severity, r.people_affected,
                   r.response_time, r.gas_leak_ppm, r.smoke_detected,
                   r.fire_alarm, r.emergency_button,
                   r.temperature_c AS safety_temperature_c,
                   r.synthetic_context
            FROM public.safety_readings r
            JOIN public.facilities f USING (facility_id)
            WHERE 1=1
        """,
    }
    if ds not in queries:
        return pd.DataFrame()

    sql = queries[ds]
    params = {}
    if fac is not None:
        alias = "r"
        sql += f" AND {alias}.facility_id = :facility_id"
        params["facility_id"] = fac
    if start is not None:
        time_col = "r.reading_ts"
        sql += f" AND {time_col} >= :start_ts"
        params["start_ts"] = pd.Timestamp(start).to_pydatetime()
    if end is not None:
        time_col = "r.reading_ts"
        sql += f" AND {time_col} < :end_ts"
        params["end_ts"] = (pd.Timestamp(end) + pd.Timedelta(days=1)).to_pydatetime()
    order_col = "r.reading_ts"
    sql += f" ORDER BY {order_col} DESC LIMIT :limit"
    params["limit"] = int(limit)

    d = query(sql, **params)
    d["zone_id"] = d["facility_location"].map(_zone_from_location)
    d.drop(columns=["facility_location"], inplace=True)

    if zone is not None:
        d = d[d["zone_id"] == zone]

    return d.reset_index(drop=True)


@st.cache_data(ttl=60)
def raw(ds, fac=None, zone=None, start=None, end=None, limit=5000):
    if ds not in active_domains():
        return pd.DataFrame()
    if DB and ds in {"energy", "water", "waste", "environment", "traffic", "equipment", "safety"}:
        return _db_raw(ds, fac, zone, start, end, limit)

    d = synthetic_data()[ds]
    if fac is not None:
        d = d[d["facility_id"] == fac]
    if zone is not None:
        d = d[d["zone_id"] == zone]
    if start:
        d = d[d["timestamp"] >= pd.Timestamp(start)]
    if end:
        d = d[d["timestamp"] < pd.Timestamp(end) + pd.Timedelta(days=1)]
    return d.sort_values("timestamp", ascending=False).head(limit).reset_index(drop=True)


def _value_column(ds):
    return DS[ds][0]


def _normalize_result_data(ds, d):
    if d.empty:
        return pd.DataFrame(columns=CONTRACT)
    d = d.copy()
    d["timestamp"] = pd.to_datetime(d["timestamp"], errors="coerce")
    d["zone_id"] = d["zone_id"].fillna("Unknown")
    d["source"] = ds
    m = _value_column(ds)
    if m not in d.columns:
        return pd.DataFrame(columns=CONTRACT)
    d["actual_value"] = pd.to_numeric(d[m], errors="coerce")
    d = d.dropna(subset=["timestamp", "actual_value"])
    hist = d.copy()
    hist["h"] = hist["timestamp"].dt.hour
    prof = (
        hist.groupby(["facility_id", "zone_id", "h"])["actual_value"]
        .median()
        .rename("expected_value")
        .reset_index()
    )
    d["h"] = d["timestamp"].dt.hour
    d = d.merge(prof, on=["facility_id", "zone_id", "h"], how="left")
    d["expected_value"] = d["expected_value"].fillna(d["actual_value"].median())
    expected_values = d["expected_value"].replace(0, np.nan)
    deviation_pct = (d["actual_value"] / expected_values - 1) * 100
    d["deviation_pct"] = deviation_pct.replace(
        [np.inf, -np.inf], 0
    ).fillna(0)
    d["severity"] = np.select(
        [d["deviation_pct"].abs() >= 30, d["deviation_pct"].abs() >= 15],
        ["HIGH", "MEDIUM"], default="NORMAL"
    )
    d["is_anomaly"] = d["severity"] != "NORMAL"
    return d[CONTRACT].sort_values("timestamp").reset_index(drop=True)


@st.cache_data(ttl=60)
def results(ds):
    d = raw(ds, limit=5000)
    return _normalize_result_data(ds, d)


@st.cache_data(ttl=60)
def forecast(ds):
    d = raw(ds, limit=5000)
    if d.empty:
        return pd.DataFrame(columns=["timestamp", "facility_id", "zone_id", "forecast_value", "source"])
    m = _value_column(ds)
    if m not in d:
        return pd.DataFrame(columns=["timestamp", "facility_id", "zone_id", "forecast_value", "source"])
    d["timestamp"] = pd.to_datetime(d["timestamp"])
    d["h"] = d["timestamp"].dt.hour
    profile = d.groupby(["facility_id", "zone_id", "h"])[m].mean().rename("forecast_value").reset_index()
    last = d["timestamp"].max()
    future = pd.DataFrame({"timestamp": pd.date_range(last + pd.Timedelta(hours=1), periods=24, freq="h")})
    future["h"] = future["timestamp"].dt.hour
    combos = profile[["facility_id", "zone_id"]].drop_duplicates()
    future = future.assign(key=1).merge(combos.assign(key=1), on="key").drop(columns="key")
    return future.merge(profile, on=["facility_id", "zone_id", "h"], how="left").drop(columns="h").assign(source=ds)


@st.cache_data(ttl=60)
def alerts():
    if not DB:
        return pd.DataFrame(
            columns=[
                "alert_id",
                "facility_id",
                "facility_name",
                "alert_type",
                "severity",
                "message",
                "reading_ts",
            ]
        )
    return query("""
        SELECT a.alert_id, a.facility_id, f.facility_name,
               a.alert_type, a.severity, a.message, a.reading_ts
        FROM public.alerts a
        JOIN public.facilities f USING (facility_id)
        WHERE a.status = 'ACTIVE'
        ORDER BY a.reading_ts DESC
    """)


def get_facilities():
    if DB:
        return query(
            "SELECT facility_id, facility_name, facility_type, company_name, "
            "location, status, sustainability_rating "
            "FROM public.facilities ORDER BY facility_id"
        )
    return FAC.rename(columns={"name": "facility_name"})[
        ["facility_id", "facility_name", "zone"]
    ]
