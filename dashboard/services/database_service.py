"""Data access layer: PostgreSQL tables (when DATABASE_URL is set) or the labelled synthetic sample provider.
Moved from data_service.py: _synth (now synthetic_data), raw, results, forecast.
Note: results/forecast (the Members 3/4 AI-output contract) live here, not in ai_service, so that the dependency order stays
database_service <- alert_service <- ai_service with no circular imports (alerts need results; the assistant needs alerts).
Contract: see docs/dashboard/dashboard-data-contract.md."""
import numpy as np, pandas as pd, streamlit as st
from config import DB, DS, FAC, INJ, CONTRACT, RAW_TABLES, AI_RESULTS_TABLE, FORECASTS_TABLE
from db import query


@st.cache_data
def synthetic_data():
    r = np.random.default_rng(7); ts = pd.date_range(end=pd.Timestamp.now().floor("h"), periods=168, freq="h"); day = np.maximum(0, np.sin((ts.hour.values - 5) / 14 * np.pi)); out = {}
    for ds, (m, base, amp) in DS.items():
        parts = []
        for fi, (f, zs) in enumerate(zip(FAC["facility_id"], FAC["zones"])):
            for zi, z in enumerate(zs):
                v = base * (.8 + .1 * fi + .05 * zi) * (1 - amp / 2 + amp * day) * r.normal(1, .04, 168)
                if ds == "safety": v = r.poisson(.25, 168).astype(float)
                if (ds, f) in INJ and zi == 0: n, k = INJ[(ds, f)]; v[-n:] *= k
                d = pd.DataFrame({"timestamp": ts, "facility_id": f, "zone_id": z, m: v.round(1)}); j = fi * 2 + zi + 1
                if ds == "waste": d["bin_id"] = f"BIN-{j:03d}"; d[m] = d[m].clip(0, 100)
                if ds == "environment": d["pm25"] = (v * .55).round(1); d["pm10"] = (v * .9).round(1); d["co2"] = (420 + v * 2).round(0); d["no2"] = (v * .3).round(1)
                if ds == "equipment": d["machine_id"] = f"M{j:03d}"; d["vibration_mm_s"] = (v * .06 + r.normal(0, .1, 168)).round(2); d["runtime_h"] = np.arange(168) + 500 * j; d["utilization_pct"] = (60 + 30 * day).round(0)
                if ds == "traffic": d["trucks"] = (v * .25).round(0); d["avg_speed_kmh"] = (45 - v * .15).round(1); d["parking_occupancy_pct"] = np.minimum(100, v * .7).round(0)
                if ds == "safety": d["severity_level"] = np.where(v > 0, r.integers(1, 4, 168), 0)
                parts.append(d)
        out[ds] = pd.concat(parts, ignore_index=True)
    return out
@st.cache_data(ttl=60)
def raw(ds, fac=None, zone=None, start=None, end=None, limit=5000):
    if DB:
        q = f"SELECT * FROM {RAW_TABLES.get(ds, RAW_TABLES['energy'])} WHERE timestamp>=:s AND timestamp<:e" + (" AND facility_id=:f" if fac else "") + (" AND zone_id=:z" if zone else "") + " ORDER BY timestamp DESC LIMIT :n"
        p = dict(s=start or "1970-01-01", e=(pd.Timestamp(end) + pd.Timedelta(days=1)) if end else "2100-01-01", n=limit) | ({"f": fac} if fac else {}) | ({"z": zone} if zone else {}); return query(q, **p)
    d = synthetic_data()[ds]
    if fac: d = d[d["facility_id"] == fac]
    if zone: d = d[d["zone_id"] == zone]
    if start: d = d[d["timestamp"] >= pd.Timestamp(start)]
    if end: d = d[d["timestamp"] < pd.Timestamp(end) + pd.Timedelta(days=1)]
    return d.sort_values("timestamp", ascending=False).head(limit).reset_index(drop=True)
@st.cache_data(ttl=60)
def results(ds):
    """Members 3/4 contract. Synthetic mode emulates their output with an hour-of-day baseline (placeholder, not a trained model)."""
    if DB: return query(f"SELECT * FROM {AI_RESULTS_TABLE} WHERE source=:s", s=ds)
    m = DS[ds][0]; d = synthetic_data()[ds].copy(); d["h"] = d["timestamp"].dt.hour; hist = d[d["timestamp"] < d["timestamp"].max() - pd.Timedelta(hours=23)]
    prof = hist.groupby(["facility_id", "zone_id", "h"])[m].median().rename("expected_value").reset_index(); d = d.merge(prof, on=["facility_id", "zone_id", "h"]).rename(columns={m: "actual_value"})
    d["deviation_pct"] = ((d["actual_value"] / d["expected_value"].where(d["expected_value"] > 0) - 1) * 100).replace([np.inf, -np.inf], 0).fillna(0).round(1)
    d["severity"] = np.where(d["deviation_pct"] >= 30, "HIGH", np.where(d["deviation_pct"] >= 15, "MEDIUM", "NORMAL")); d.loc[(d["actual_value"] < 2) & (ds == "safety"), "severity"] = "NORMAL"; d["is_anomaly"] = d["severity"] != "NORMAL"; d["source"] = ds
    return d[CONTRACT]
@st.cache_data(ttl=60)
def forecast(ds):
    if DB: return query(f"SELECT * FROM {FORECASTS_TABLE} WHERE source=:s", s=ds)
    m = DS[ds][0]; d = synthetic_data()[ds]; d = d.assign(h=d["timestamp"].dt.hour); prof = d.groupby(["facility_id", "zone_id", "h"])[m].mean().rename("forecast_value").reset_index()
    fut = pd.DataFrame({"timestamp": pd.date_range(d["timestamp"].max() + pd.Timedelta(hours=1), periods=24, freq="h")}); fut["h"] = fut["timestamp"].dt.hour
    return fut.merge(prof, on="h").drop(columns="h").assign(source=ds)
