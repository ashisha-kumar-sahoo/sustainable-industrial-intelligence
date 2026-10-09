"""Transparent backtest and anomaly-rate metrics for the prototype dashboard.

Forecast errors use a one-step persistence baseline on a holdout tail. The
prototype has no labelled anomaly ground truth, so it reports anomaly rates
rather than claiming precision, recall, or a validated classifier score.
"""

import numpy as np
import pandas as pd

from services.database_service import raw

VALUE_COLUMNS = {
    "energy": "kwh",
    "water": "kl",
    "waste": "fill_pct",
    "environment": "aqi",
    "traffic": "vehicles",
}
METRICS_DATASETS = tuple(VALUE_COLUMNS)


def _forecast_metrics(dataset: str) -> dict | None:
    """Evaluate a one-step persistence baseline on recent readings."""
    data = raw(dataset, limit=5000)
    if data.empty or "timestamp" not in data.columns:
        return None

    value_column = VALUE_COLUMNS.get(dataset)
    if not value_column or value_column not in data.columns:
        return None

    data = (
        data[["timestamp", "facility_id", value_column]]
        .dropna()
        .sort_values("timestamp")
        .copy()
    )
    if len(data) < 20:
        return None

    # The previous observation for the same facility is the prediction.
    data["prediction"] = data.groupby("facility_id")[value_column].shift(1)
    holdout_size = max(10, min(100, len(data) // 5))
    holdout = data.dropna(subset=["prediction"]).tail(holdout_size)
    if holdout.empty:
        return None

    errors = (
        holdout[value_column].to_numpy(dtype=float)
        - holdout["prediction"].to_numpy(dtype=float)
    )
    return {
        "model": "One-step persistence baseline",
        "dataset": dataset,
        "n_test": int(len(holdout)),
        "mae": round(float(np.mean(np.abs(errors))), 3),
        "rmse": round(float(np.sqrt(np.mean(errors**2))), 3),
    }


def _anomaly_rate(dataset: str) -> dict | None:
    """Calculate an IQR-based outlier rate without claiming labelled accuracy."""
    data = raw(dataset, limit=5000)
    value_column = VALUE_COLUMNS[dataset]
    if data.empty or value_column not in data.columns:
        return None

    values = pd.to_numeric(data[value_column], errors="coerce").dropna()
    if values.empty:
        return None

    first_quartile, third_quartile = values.quantile([0.25, 0.75])
    interquartile_range = third_quartile - first_quartile
    lower_bound = first_quartile - 1.5 * interquartile_range
    upper_bound = third_quartile + 1.5 * interquartile_range
    outliers = (values < lower_bound) | (values > upper_bound)

    return {
        "dataset": dataset,
        "observations": int(len(values)),
        "anomaly_rate_pct": round(float(outliers.mean() * 100), 2),
    }


def collect_metrics() -> dict:
    """Collect available metrics while allowing the dashboard to remain usable."""
    forecast_metrics = []
    anomaly_metrics = []

    for dataset in METRICS_DATASETS:
        try:
            metric = _forecast_metrics(dataset)
            if metric:
                forecast_metrics.append(metric)
        except Exception:
            # Missing database access should not prevent other pages rendering.
            continue

        try:
            metric = _anomaly_rate(dataset)
            if metric:
                anomaly_metrics.append(metric)
        except Exception:
            continue

    return {
        "forecast": forecast_metrics,
        "anomaly": anomaly_metrics,
        "anomaly_note": (
            "No ground-truth anomaly labels are present in the prototype; "
            "precision/recall are therefore not claimed."
        ),
    }
