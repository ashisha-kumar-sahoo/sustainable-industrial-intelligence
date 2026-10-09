"""Adapters from dashboard data contracts to reusable ML pipelines.

The adapters translate PostgreSQL-backed dashboard fields into each model's
expected inputs. Missing fields are reported instead of being fabricated.
"""

import pandas as pd

from ml.environment.predict import predict_environment_status
from ml.traffic.predict import predict_traffic_status
from ml.equipment.predict import predict_equipment_status
from ml.safety.predict import predict_safety_status


def _location_column(data: pd.DataFrame) -> pd.Series:
    """Choose the best available display location for a model input."""
    if "zone_id" in data.columns:
        return data["zone_id"].fillna("Unknown").astype(str)
    if "facility_name" in data.columns:
        return data["facility_name"].fillna("Unknown").astype(str)
    return pd.Series("Unknown", index=data.index, dtype="object")


def predict_environment(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, str | None]:
    """Run the environment anomaly and rule-based risk pipeline on raw readings."""
    if dataframe is None or dataframe.empty:
        return pd.DataFrame(), "No environmental readings are available for ML analysis."

    required_columns = {"timestamp", "aqi", "pm25", "pm10", "no2"}
    missing_columns = sorted(required_columns - set(dataframe.columns))
    if missing_columns:
        return (
            pd.DataFrame(),
            "The environmental model cannot run because these fields are missing: "
            + ", ".join(missing_columns),
        )

    model_data = dataframe.copy()
    model_data["location"] = _location_column(model_data)
    try:
        predictions = predict_environment_status(model_data)
    except (TypeError, ValueError) as exc:
        return pd.DataFrame(), f"The environmental model could not process these readings: {exc}"

    if predictions.empty:
        return predictions, "No valid environmental rows remained after preprocessing."
    return predictions, None


def predict_traffic(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str | None]:
    """Run traffic congestion and hotspot analysis on raw traffic readings."""
    if dataframe is None or dataframe.empty:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            "No traffic readings are available for ML analysis.",
        )

    column_mapping = {
        "vehicles": "vehicle_count",
        "avg_speed_kmh": "average_speed",
        "parking_occupancy_pct": "occupancy",
    }
    model_data = dataframe.rename(columns=column_mapping).copy()
    required_columns = {
        "timestamp",
        "vehicle_count",
        "average_speed",
        "occupancy",
    }
    missing_columns = sorted(required_columns - set(model_data.columns))
    if missing_columns:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            "The traffic model cannot run because these fields are missing: "
            + ", ".join(missing_columns),
        )

    model_data["location"] = _location_column(model_data)
    try:
        predictions, hotspot_summary = predict_traffic_status(model_data)
    except (TypeError, ValueError) as exc:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            f"The traffic model could not process these readings: {exc}",
        )

    if predictions.empty:
        return predictions, hotspot_summary, "No valid traffic rows remained after preprocessing."
    return predictions, hotspot_summary, None


def predict_equipment(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, str | None]:
    """Run the equipment condition pipeline on stored equipment telemetry."""
    if dataframe is None or dataframe.empty:
        return pd.DataFrame(), "No equipment telemetry is available for ML analysis."

    model_data = dataframe.rename(
        columns={
            "machine_id": "equipment_id",
            "vibration_mm_s": "vibration",
            "vibration_mms": "vibration",
            "utilization_pct": "utilization",
        }
    ).copy()
    required_columns = {
        "timestamp", "equipment_id", "temperature", "vibration",
        "operating_hours", "utilization",
    }
    missing_columns = sorted(required_columns - set(model_data.columns))
    if missing_columns:
        return (
            pd.DataFrame(),
            "The equipment model cannot run because these fields are missing: "
            + ", ".join(missing_columns),
        )

    model_data["location"] = _location_column(model_data)
    try:
        predictions = predict_equipment_status(model_data)
    except (TypeError, ValueError) as exc:
        return pd.DataFrame(), f"The equipment model could not process these readings: {exc}"

    if predictions.empty:
        return predictions, "No valid equipment rows remained after preprocessing."
    return predictions, None


def predict_safety(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str | None]:
    """Run safety risk and hotspot analysis on stored safety telemetry."""
    if dataframe is None or dataframe.empty:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            "No safety telemetry is available for ML analysis.",
        )

    model_data = dataframe.copy()
    required_columns = {
        "timestamp", "incident_type", "severity", "people_affected", "response_time"
    }
    missing_columns = sorted(required_columns - set(model_data.columns))
    if missing_columns:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            "The safety model cannot run because these fields are missing: "
            + ", ".join(missing_columns),
        )

    model_data["location"] = _location_column(model_data)
    try:
        predictions, hotspot_summary = predict_safety_status(model_data)
    except (TypeError, ValueError) as exc:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            f"The safety model could not process these readings: {exc}",
        )

    if predictions.empty:
        return predictions, hotspot_summary, "No valid safety rows remained after preprocessing."
    return predictions, hotspot_summary, None


def unavailable_equipment_message() -> str:
    """Compatibility message retained for callers that need a status string."""
    return "Equipment telemetry is stored in public.equipment_readings."


def unavailable_safety_message() -> str:
    """Compatibility message retained for callers that need a status string."""
    return (
        "Safety telemetry is stored in public.safety_readings. "
        "Synthetic incident labels are illustrative only."
    )
