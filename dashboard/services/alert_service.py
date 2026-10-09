"""Alert retrieval and deterministic priority logic."""
import pandas as pd
import streamlit as st

from config import DB, DS, RECO, active_domains
from db import query
from utils import fname
from services.database_service import results


@st.cache_data(ttl=60)
def alerts():
    if DB:
        d = query("""
            SELECT a.alert_id, a.facility_id, f.facility_name,
                   a.sensor_id, a.alert_type, a.severity, a.message,
                   a.value, a.threshold, a.reading_ts
            FROM public.alerts a
            JOIN public.facilities f USING (facility_id)
            WHERE a.status = 'ACTIVE'
            ORDER BY
                CASE a.severity
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4 ELSE 5
                END,
                a.reading_ts DESC
        """)
        if "traffic" not in active_domains() and not d.empty:
            d = d[~d["alert_type"].astype(str).str.contains(
                r"TRAFFIC|CONGESTION|PARKING|VEHICLE", case=False, na=False
            )].copy()
        if d.empty:
            return pd.DataFrame()
        d["timestamp"] = pd.to_datetime(d["reading_ts"])
        d["zone_id"] = d["facility_id"].map(
            dict(zip(
                # Avoid a second DB dependency: seeded location -> zone mapping.
                [int(x) for x in range(1, 21)],
                ["Zone A","Zone A","Zone B","Zone B","Zone B","Zone C","Zone C","Zone C",
                 "Zone A","Zone D","Zone D","Zone B","Zone E","Zone C","Zone E","Zone D",
                 "Zone E","Zone A","Zone E","Zone B"]
            ))
        ).fillna("Unknown")
        d["title"] = d["facility_name"].astype(str) + " — " + d["alert_type"].astype(str)
        d["insight_text"] = d["message"]
        d["recommendation"] = d["alert_type"].map(
            lambda x: RECO.get(str(x).split("_")[0].lower(), "Inspect the affected facility and verify the reading.")
        )
        d["deviation_pct"] = 0.0
        d["status"] = "Open"
        return d

    rows = []
    for ds in DS:
        r = results(ds)
        if r.empty:
            continue
        r = r[r["timestamp"] >= r["timestamp"].max() - pd.Timedelta(hours=5)]
        g = r.groupby(["facility_id", "zone_id"]).agg(
            a=("actual_value", "mean"), e=("expected_value", "mean"),
            dev=("deviation_pct", "mean"), ts=("timestamp", "max")
        ).reset_index()
        for _, x in g[g["dev"].abs() >= 15].iterrows():
            sev = "HIGH" if abs(x["dev"]) >= 30 else "MEDIUM"
            rows.append(dict(
                alert_id=f"A-{ds[:3].upper()}-{x['facility_id']}-{x['zone_id']}",
                severity=sev, source=ds, facility_id=x["facility_id"],
                zone_id=x["zone_id"], timestamp=x["ts"],
                title=f"{fname(x['facility_id'])} ({x['zone_id']}) {ds} {x['dev']:+.0f}% vs baseline",
                evidence_actual=round(x["a"], 1), evidence_expected=round(x["e"], 1),
                deviation_pct=round(x["dev"], 1), recommendation=RECO[ds],
                insight_text=(
                    f"{ds.capitalize()} at {fname(x['facility_id'])} is about "
                    f"{x['dev']:.0f}% from its recent baseline."
                ),
                status="Open"
            ))
    return pd.DataFrame(rows)
