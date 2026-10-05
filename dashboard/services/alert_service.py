"""Alert retrieval/generation (Member 6 contract). Moved unchanged from data_service.alerts.
PostgreSQL mode reads the alerts table; synthetic mode derives sample alerts from the AI results."""
import pandas as pd, streamlit as st
from config import DB, DS, RECO, ALERTS_TABLE
from db import query
from utils import fname
from services.database_service import results


@st.cache_data(ttl=60)
def alerts():
    """Member 6 contract. Synthetic mode derives sample alerts from the results above (decision logic belongs to Member 6)."""
    if DB: return query(f"SELECT * FROM {ALERTS_TABLE} ORDER BY timestamp DESC")
    rows = []
    for ds in DS:
        r = results(ds); r = r[r["timestamp"] >= r["timestamp"].max() - pd.Timedelta(hours=5)]
        g = r.groupby(["facility_id", "zone_id"]).agg(a=("actual_value", "mean"), e=("expected_value", "mean"), dev=("deviation_pct", "mean"), ts=("timestamp", "max")).reset_index()
        for _, x in g[g["dev"] >= 15].iterrows():
            sev = "HIGH" if x["dev"] >= 30 else "MEDIUM"
            rows.append(dict(alert_id=f"A-{ds[:3].upper()}-{x['zone_id']}", severity=sev, source=ds, facility_id=x["facility_id"], zone_id=x["zone_id"], timestamp=x["ts"], title=f"{fname(x['facility_id'])} ({x['zone_id']}) {ds} {x['dev']:+.0f}% vs baseline",
                             evidence_actual=round(x["a"], 1), evidence_expected=round(x["e"], 1), deviation_pct=round(x["dev"], 1), recommendation=RECO[ds],
                             insight_text=f"{ds.capitalize()} in {fname(x['facility_id'])} is about {x['dev']:.0f}% above its recent baseline (actual {x['a']:.0f} vs expected {x['e']:.0f}).", status="Open"))
    return pd.DataFrame(rows).sort_values(["severity", "deviation_pct"], ascending=[True, False]) if rows else pd.DataFrame()
