"""Near-term waste-bin fill prediction using telemetry or a rate projection."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

REQUIRED_COLUMNS = [
    "reading_ts",
    "facility_id",
    "fill_level_percent",
    "fill_rate_percent_per_hour",
]
MODEL_FEATURES = [
    "fill_level_percent",
    "fill_rate_percent_per_hour",
    "hour",
    "day_of_week",
]


def prepare_waste_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Validate and prepare waste telemetry for near-term prediction."""
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Waste telemetry must be provided as a pandas DataFrame.")
    if dataframe.empty:
        return dataframe.copy()

    data = dataframe.copy()
    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in data.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing required waste columns: {missing_columns}")

    data["reading_ts"] = pd.to_datetime(data["reading_ts"], errors="coerce")
    data["fill_level_percent"] = pd.to_numeric(
        data["fill_level_percent"], errors="coerce"
    )
    data["fill_rate_percent_per_hour"] = pd.to_numeric(
        data["fill_rate_percent_per_hour"], errors="coerce"
    )

    data = data.dropna(subset=REQUIRED_COLUMNS).copy()
    data = data.loc[
        data["fill_level_percent"].between(0, 100)
        & (data["fill_rate_percent_per_hour"] >= 0)
    ]

    # Keep each bin's readings together. Sensor IDs distinguish multiple bins
    # in one facility; facility ID is the fallback when sensor ID is absent.
    grouping_columns = ["facility_id"]
    if "sensor_id" in data.columns:
        grouping_columns.append("sensor_id")
    data = data.sort_values([*grouping_columns, "reading_ts"]).reset_index(drop=True)

    data["hour"] = data["reading_ts"].dt.hour
    data["day_of_week"] = data["reading_ts"].dt.dayofweek
    data["projected_fill_6h"] = (
        data["fill_level_percent"]
        + data["fill_rate_percent_per_hour"] * 6
    ).clip(upper=100)
    return data


def predict_waste_overflow(
    dataframe: pd.DataFrame,
    horizon_hours: int = 6,
) -> pd.DataFrame:
    """Estimate bin fill at a future horizon and assign an explainable risk tier.

    With at least 30 rows and 20 usable future targets, a Random Forest is
    trained to predict the fill level ``horizon_hours`` observations ahead
    within each bin. Otherwise the transparent fill-rate projection is used.
    The ``overflow_probability`` field is a normalized risk score, not a
    statistically calibrated probability.
    """
    data = prepare_waste_data(dataframe)
    if data.empty:
        data["predicted_fill_level_percent"] = pd.Series(dtype=float)
        data["overflow_probability"] = pd.Series(dtype=float)
        data["overflow_risk"] = pd.Series(dtype=object)
        data["horizon_hours"] = pd.Series(dtype=int)
        data["prediction_method"] = pd.Series(dtype=object)
        return data

    horizon_hours = max(1, int(horizon_hours))
    rate_projection = (
        data["fill_level_percent"]
        + data["fill_rate_percent_per_hour"] * horizon_hours
    ).clip(0, 100)
    predicted_fill = rate_projection.copy()
    prediction_method = "fill-rate projection"

    grouping_columns = ["facility_id"]
    if "sensor_id" in data.columns:
        grouping_columns.append("sensor_id")

    # The dataset is sorted by bin and timestamp, so this target stays within
    # the same bin instead of accidentally learning from another facility.
    future_fill = data.groupby(grouping_columns)["fill_level_percent"].shift(
        -horizon_hours
    )
    valid_targets = future_fill.notna()

    if len(data) >= 30 and int(valid_targets.sum()) >= 20:
        model = RandomForestRegressor(
            n_estimators=150,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(
            data.loc[valid_targets, MODEL_FEATURES],
            future_fill.loc[valid_targets],
        )
        predicted_fill = pd.Series(
            model.predict(data[MODEL_FEATURES]),
            index=data.index,
        ).clip(0, 100)
        prediction_method = "Random Forest with per-bin future targets"

    data["predicted_fill_level_percent"] = predicted_fill.round(2)
    data["overflow_probability"] = (
        data["predicted_fill_level_percent"] / 100.0
    ).clip(0, 1).round(3)
    data["overflow_risk"] = np.select(
        [
            data["predicted_fill_level_percent"] >= 90,
            data["predicted_fill_level_percent"] >= 75,
        ],
        ["HIGH", "MEDIUM"],
        default="LOW",
    )
    data["horizon_hours"] = horizon_hours
    data["prediction_method"] = prediction_method
    return data


def estimate_hours_to_overflow(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Estimate hours until full using the current fill level and fill rate."""
    data = prepare_waste_data(dataframe)
    if data.empty:
        return pd.DataFrame(
            columns=[
                "reading_ts",
                "facility_id",
                "fill_level_percent",
                "fill_rate_percent_per_hour",
                "hours_to_overflow",
            ]
        )

    data["hours_to_overflow"] = np.where(
        data["fill_rate_percent_per_hour"] > 0,
        (100 - data["fill_level_percent"])
        / data["fill_rate_percent_per_hour"],
        np.inf,
    )
    return data[
        [
            "reading_ts",
            "facility_id",
            "fill_level_percent",
            "fill_rate_percent_per_hour",
            "hours_to_overflow",
        ]
    ]
