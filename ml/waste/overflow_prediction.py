import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor


REQUIRED_COLUMNS = [
    "reading_ts",
    "facility_id",
    "fill_level_percent",
    "fill_rate_percent_per_hour",
]


def prepare_waste_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare real bin telemetry for near-term overflow prediction."""
    data = df.copy()
    missing = [c for c in REQUIRED_COLUMNS if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required waste columns: {missing}")

    data["reading_ts"] = pd.to_datetime(data["reading_ts"], errors="coerce")
    data["fill_level_percent"] = pd.to_numeric(data["fill_level_percent"], errors="coerce")
    data["fill_rate_percent_per_hour"] = pd.to_numeric(data["fill_rate_percent_per_hour"], errors="coerce")

    data = data.dropna(subset=REQUIRED_COLUMNS).copy()
    data = data[
        data["fill_level_percent"].between(0, 100)
        & (data["fill_rate_percent_per_hour"] >= 0)
    ].sort_values("reading_ts").reset_index(drop=True)

    data["hour"] = data["reading_ts"].dt.hour
    data["day_of_week"] = data["reading_ts"].dt.dayofweek
    data["projected_fill_6h"] = (
        data["fill_level_percent"]
        + data["fill_rate_percent_per_hour"] * 6
    ).clip(upper=100)

    return data


def predict_waste_overflow(df: pd.DataFrame, horizon_hours: int = 6) -> pd.DataFrame:
    """
    Predict bin fill level at the requested horizon.

    The primary signal is physical fill-level telemetry and fill-rate telemetry.
    When enough observations exist, a RandomForest regressor is trained on
    lagged telemetry. Otherwise the deterministic rate projection is used.
    """
    data = prepare_waste_data(df)
    if data.empty:
        for col in ["predicted_fill_level_percent", "overflow_probability", "overflow_risk"]:
            data[col] = pd.Series(dtype=float if col != "overflow_risk" else object)
        return data

    horizon_hours = max(1, int(horizon_hours))
    data["rate_projection"] = (
        data["fill_level_percent"]
        + data["fill_rate_percent_per_hour"] * horizon_hours
    ).clip(upper=100)

    if len(data) >= 30:
        features = ["fill_level_percent", "fill_rate_percent_per_hour", "hour", "day_of_week"]
        target = data["fill_level_percent"].shift(-1)
        train = data.iloc[:-1].copy()
        y = target.iloc[:-1]
        valid = y.notna()
        if valid.sum() >= 20:
            model = RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=-1)
            model.fit(train.loc[valid, features], y.loc[valid])
            data["predicted_fill_level_percent"] = model.predict(data[features]).clip(0, 100)
        else:
            data["predicted_fill_level_percent"] = data["rate_projection"]
    else:
        data["predicted_fill_level_percent"] = data["rate_projection"]

    # Probability is a transparent risk score, not a calibrated probability.
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
    return data


def estimate_hours_to_overflow(df: pd.DataFrame) -> pd.DataFrame:
    """Estimate hours until 100% fill using current level and fill rate."""
    data = prepare_waste_data(df)
    data["hours_to_overflow"] = np.where(
        data["fill_rate_percent_per_hour"] > 0,
        (100 - data["fill_level_percent"]) / data["fill_rate_percent_per_hour"],
        np.inf,
    )
    return data[["reading_ts", "facility_id", "fill_level_percent",
                 "fill_rate_percent_per_hour", "hours_to_overflow"]]
