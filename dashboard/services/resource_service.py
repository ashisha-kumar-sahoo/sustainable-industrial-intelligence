"""Pure data-shaping helpers for resource and domain dashboard pages.

These functions receive already-filtered DataFrames and contain no Streamlit
calls, which keeps calculations straightforward to test.
"""

from __future__ import annotations

import pandas as pd

from config import KP
from utils import fname


def kpi_for(dataset: str, results: pd.DataFrame) -> tuple:
    """Return label, value, baseline delta, severity, and deviation percent."""
    label, unit, aggregation = KP[dataset]
    if results.empty:
        return label, "–", "no data", "NORMAL", 0.0

    latest_timestamp = results["timestamp"].max()
    cutoff = latest_timestamp - pd.Timedelta(hours=24)
    recent_results = results.loc[results["timestamp"] > cutoff]

    if recent_results.empty:
        return label, "–", "no recent data", "NORMAL", 0.0

    actual_value = getattr(recent_results["actual_value"], aggregation)()
    expected_value = getattr(recent_results["expected_value"], aggregation)()
    deviation_pct = (actual_value / expected_value - 1) * 100 if expected_value else 0

    if deviation_pct >= 30:
        severity = "HIGH"
    elif deviation_pct >= 15:
        severity = "MEDIUM"
    else:
        severity = "NORMAL"

    direction = "↑" if deviation_pct >= 0 else "↓"
    value_text = f"{actual_value:,.0f} {unit}".strip()
    delta_text = f"{direction} {abs(deviation_pct):.1f}% vs baseline"

    return label, value_text, delta_text, severity, float(deviation_pct)


def series(results: pd.DataFrame, aggregation: str) -> pd.DataFrame:
    """Aggregate actuals, baselines, and anomaly flags by timestamp."""
    if results.empty:
        return pd.DataFrame(columns=["timestamp", "actual", "expected", "anom"])

    return (
        results.groupby("timestamp")
        .agg(
            actual=("actual_value", aggregation),
            expected=("expected_value", aggregation),
            anom=("is_anomaly", "max"),
        )
        .reset_index()
    )


def forecast_series(forecasts: pd.DataFrame, aggregation: str) -> pd.DataFrame | None:
    """Aggregate forecast values by timestamp, or return None when unavailable."""
    if forecasts.empty:
        return None

    return (
        forecasts.groupby("timestamp")
        .agg(forecast=("forecast_value", aggregation))
        .reset_index()
    )


def group_column(dataset: str) -> str:
    """Return the geographic grouping column used for this domain."""
    return "zone_id" if dataset == "environment" else "facility_id"


def latest_by_group(
    results: pd.DataFrame,
    aggregation: str,
    group_by: str,
) -> pd.DataFrame:
    """Compare the last 24 hours of actual and baseline values by group."""
    if results.empty:
        return pd.DataFrame(columns=[group_by, "actual", "expected", "label"])

    cutoff = results["timestamp"].max() - pd.Timedelta(hours=24)
    recent_results = results.loc[results["timestamp"] > cutoff]
    grouped = (
        recent_results.groupby(group_by)
        .agg(
            actual=("actual_value", aggregation),
            expected=("expected_value", aggregation),
        )
        .reset_index()
    )

    if group_by == "facility_id":
        grouped["label"] = grouped[group_by].map(fname)
    else:
        grouped["label"] = grouped[group_by]

    return grouped


def latest_anomalies(results: pd.DataFrame) -> pd.DataFrame:
    """Return up to ten newest anomalies."""
    if results.empty or "is_anomaly" not in results:
        return results.head(0).copy()

    return (
        results.loc[results["is_anomaly"]]
        .sort_values("timestamp", ascending=False)
        .head(10)
    )


def bin_fill_status(results: pd.DataFrame, forecasts: pd.DataFrame) -> pd.DataFrame:
    """Build current bin fill levels and include forecast peaks when available."""
    if results.empty:
        return pd.DataFrame(
            columns=["facility_id", "zone_id", "current_%", "severity"]
        )

    current_bins = (
        results.sort_values("timestamp")
        .groupby(["facility_id", "zone_id"])
        .tail(1)[["facility_id", "zone_id", "actual_value", "severity"]]
        .rename(columns={"actual_value": "current_%"})
    )

    if not forecasts.empty:
        forecast_peaks = (
            forecasts.groupby(["facility_id", "zone_id"])["forecast_value"]
            .max()
            .rename("predicted_%")
            .reset_index()
        )
        current_bins = current_bins.merge(
            forecast_peaks,
            on=["facility_id", "zone_id"],
            how="left",
        )

    return current_bins


def supporting_metrics(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Calculate mean supporting metrics for each timestamp."""
    if data.empty or not columns:
        return pd.DataFrame(columns=["timestamp", *columns])

    return data.groupby("timestamp")[columns].mean().reset_index()


def sustainability_score(kpis: dict) -> float:
    """Calculate the prototype score from positive 24-hour deviations.

    This is a transparent heuristic score, not a certified sustainability
    rating. Each domain's positive deviation is capped at 50 percent.
    """
    if not kpis:
        return 0.0

    capped_deviations = [
        min(50, max(0, values[4]))
        for values in kpis.values()
        if len(values) > 4
    ]
    if not capped_deviations:
        return 0.0

    return max(0.0, 100 - 2 * sum(capped_deviations) / len(capped_deviations))


def domain_scorecard(kpis: dict) -> pd.DataFrame:
    """Create a compact scorecard showing each domain's heuristic score."""
    rows = []
    for values in kpis.values():
        label, _value, delta, _severity, deviation = values
        score = max(0, 100 - 2 * min(50, max(0, deviation)))
        rows.append((label, f"{score:.0f}", delta))

    return pd.DataFrame(rows, columns=["Domain", "Score /100", "Basis"])
