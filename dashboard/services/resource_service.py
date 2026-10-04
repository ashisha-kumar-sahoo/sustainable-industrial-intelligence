"""Pure data shaping for the domain pages (energy, water, waste and the shared KPI / trend / score maths).
Moved from pages.py: kpis_data (per-dataset part -> kpi_for), series, and the calculation parts of domain() and overview().
No Streamlit calls here: callers pass already-filtered DataFrames."""
import pandas as pd
from config import KP
from utils import fname


def kpi_for(ds, r):
    """(label, value text, delta text, severity, deviation %) for one dataset's filtered AI results."""
    lab, unit, how = KP[ds]
    if r.empty: return (lab, "–", "no data", "NORMAL", 0)
    l = r[r["timestamp"] > r["timestamp"].max() - pd.Timedelta(hours=24)]; v, e = getattr(l["actual_value"], how)(), getattr(l["expected_value"], how)(); dv = (v / e - 1) * 100 if e else 0
    return (lab, f"{v:,.0f} {unit}".strip(), f"{'↑' if dv >= 0 else '↓'} {abs(dv):.1f}% vs baseline", "HIGH" if dv >= 30 else "MEDIUM" if dv >= 15 else "NORMAL", dv)


def series(r, how):
    return r.groupby("timestamp").agg(actual=("actual_value", how), expected=("expected_value", how), anom=("is_anomaly", "max")).reset_index()


def forecast_series(fc, how):
    """Aggregate a (filtered) forecast frame to one line, or None when there is no forecast."""
    return fc.groupby("timestamp").agg(forecast=("forecast_value", how)).reset_index() if len(fc) else None


def group_column(ds): return "zone_id" if ds == "environment" else "facility_id"


def latest_by_group(r, how, by):
    """Last-24h actual vs expected per facility (or per zone for environment) for the comparison bar chart."""
    g = r[r["timestamp"] > r["timestamp"].max() - pd.Timedelta(hours=24)].groupby(by).agg(actual=("actual_value", how), expected=("expected_value", how)).reset_index()
    g["label"] = g[by].map(fname) if by == "facility_id" else g[by]
    return g


def latest_anomalies(r):
    return r[r["is_anomaly"]].sort_values("timestamp", ascending=False).head(10)


def bin_fill_status(r, fc):
    """Waste: current fill % per bin/zone, plus predicted peak from the forecast when available."""
    cur = r.sort_values("timestamp").groupby(["facility_id", "zone_id"]).tail(1)[["facility_id", "zone_id", "actual_value", "severity"]].rename(columns={"actual_value": "current_%"})
    if len(fc): cur = cur.merge(fc.groupby(["facility_id", "zone_id"])["forecast_value"].max().rename("predicted_%").reset_index(), on=["facility_id", "zone_id"], how="left")
    return cur


def supporting_metrics(x, cols):
    return x.groupby("timestamp")[cols].mean().reset_index()


def sustainability_score(K):
    """Draft overall score: 100 - 2 x mean(24h deviation above baseline capped at 50%)."""
    return max(0, 100 - 2 * sum(min(50, max(0, v[4])) for v in K.values()) / len(K))


def domain_scorecard(K):
    return pd.DataFrame([(v[0], f"{max(0, 100 - 2 * min(50, max(0, v[4]))):.0f}", v[2]) for v in K.values()], columns=["Domain", "Score /100", "Basis"])
