"""Transparent, data-driven model metrics for the demo.

Metrics are computed from the current PostgreSQL readings when available.
Forecast MAE/RMSE use a one-step naive holdout backtest. Anomaly detection has
no ground-truth labels in the prototype, so the dashboard reports anomaly rate
and explicitly states that precision/recall are not claimed.
"""
import numpy as np
import pandas as pd

from services.database_service import raw


def _forecast_metrics(ds):
    d = raw(ds, limit=5000)
    if d.empty or "timestamp" not in d:
        return None
    value_col = {"energy": "kwh", "water": "kl", "waste": "fill_pct", "environment": "aqi", "traffic": "vehicles"}.get(ds)
    if value_col not in d:
        return None
    d = d[["timestamp", "facility_id", value_col]].dropna().sort_values("timestamp")
    if len(d) < 20:
        return None
    # One-step holdout using previous observation per facility.
    d["pred"] = d.groupby("facility_id")[value_col].shift(1)
    test = d.dropna(subset=["pred"]).tail(max(10, min(100, len(d)//5)))
    if test.empty:
        return None
    err = test[value_col].to_numpy(dtype=float) - test["pred"].to_numpy(dtype=float)
    return {
        "model": "One-step persistence baseline",
        "dataset": ds,
        "n_test": int(len(test)),
        "mae": round(float(np.mean(np.abs(err))), 3),
        "rmse": round(float(np.sqrt(np.mean(err ** 2))), 3),
    }


def collect_metrics():
    metrics = []
    for ds in ("energy", "water", "waste", "environment", "traffic"):
        try:
            m = _forecast_metrics(ds)
            if m:
                metrics.append(m)
        except Exception:
            pass

    anomaly_rows = []
    for ds in ("energy", "water", "waste", "environment", "traffic"):
        try:
            d = raw(ds, limit=5000)
            if not d.empty:
                value_col = {"energy":"kwh","water":"kl","waste":"fill_pct","environment":"aqi","traffic":"vehicles"}[ds]
                vals = pd.to_numeric(d[value_col], errors="coerce").dropna()
                if len(vals):
                    q1, q3 = vals.quantile([.25, .75])
                    iqr = q3 - q1
                    flags = (vals < q1 - 1.5*iqr) | (vals > q3 + 1.5*iqr)
                    anomaly_rows.append({"dataset": ds, "observations": int(len(vals)), "anomaly_rate_pct": round(float(flags.mean()*100), 2)})
        except Exception:
            pass

    return {"forecast": metrics, "anomaly": anomaly_rows,
            "anomaly_note": "No ground-truth anomaly labels are present in the prototype; precision/recall are therefore not claimed."}
