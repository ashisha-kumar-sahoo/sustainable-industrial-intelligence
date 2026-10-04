"""Estate-operations data shaping: which datasets belong to the Operations page and the per-facility severity used by the estate map.
Moved from pages.py: the Operations tab list and the facility loop inside overview(). No Streamlit calls."""
import pandas as pd
from config import FAC

OPERATIONS_DATASETS = ["traffic", "equipment", "safety"]


def facility_severity_rows(layer, get_results):
    """One row per facility for the 3D map. `get_results(ds)` returns the (filtered) AI-results frame for a dataset."""
    rows = []
    for _, f in FAC.iterrows():
        r = get_results(layer); r = r[(r["facility_id"] == f["facility_id"]) & (r["timestamp"] > r["timestamp"].max() - pd.Timedelta(hours=6))] if len(r) else r
        sv = "HIGH" if len(r) and r["severity"].eq("HIGH").any() else "MEDIUM" if len(r) and r["severity"].eq("MEDIUM").any() else "NORMAL"; v = float(r["actual_value"].mean()) if len(r) else 0
        rows.append(dict(name=f["name"], lat=f["lat"], lon=f["lon"], severity=sv, height=40 + {"HIGH": 140, "MEDIUM": 80, "NORMAL": 30}[sv], tip=f"{layer}: {sv} (avg {v:.0f})"))
    return pd.DataFrame(rows)
