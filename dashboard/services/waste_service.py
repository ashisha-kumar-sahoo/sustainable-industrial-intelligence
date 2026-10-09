"""Waste-domain model integration for the dashboard."""

import pandas as pd

from ml.waste.overflow_prediction import predict_waste_overflow

REQUIRED_DASHBOARD_COLUMNS = {
    "timestamp",
    "facility_id",
    "fill_pct",
    "fill_rate_percent_per_hour",
}


def predict_overflow(raw_data: pd.DataFrame) -> tuple[pd.DataFrame, str | None]:
    """Run the six-hour overflow estimator on dashboard-shaped waste readings.

    Returns the prediction table and an optional explanation when the supplied
    dataset does not contain the telemetry required by the model.
    """
    if raw_data is None or raw_data.empty:
        return pd.DataFrame(), "No waste telemetry is available for prediction."

    missing_columns = sorted(REQUIRED_DASHBOARD_COLUMNS - set(raw_data.columns))
    if missing_columns:
        return (
            pd.DataFrame(),
            "The overflow estimator requires fill-level and fill-rate telemetry. "
            f"Missing columns: {', '.join(missing_columns)}.",
        )

    model_data = raw_data.rename(
        columns={
            "timestamp": "reading_ts",
            "fill_pct": "fill_level_percent",
        }
    ).copy()
    predictions = predict_waste_overflow(model_data, horizon_hours=6)

    if predictions.empty:
        return predictions, "No valid fill-level/fill-rate readings remain after validation."

    group_columns = ["facility_id"]
    if "sensor_id" in predictions.columns:
        group_columns.append("sensor_id")

    latest_predictions = (
        predictions.sort_values("reading_ts")
        .groupby(group_columns, dropna=False)
        .tail(1)
        .sort_values("predicted_fill_level_percent", ascending=False)
        .reset_index(drop=True)
    )
    return latest_predictions, None
