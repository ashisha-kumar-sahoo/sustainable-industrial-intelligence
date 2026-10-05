"""Forecasting for Environment Operations AI."""

import pandas as pd
from sklearn.linear_model import LinearRegression

from ai.operations.environment.config import (
    AQI_COLUMN,
    TIMESTAMP_COLUMN,
    FACILITY_COLUMN,
    FORECAST_HORIZON,
)


def forecast_aqi(
    df: pd.DataFrame,
    horizon: int = FORECAST_HORIZON,
) -> pd.DataFrame:
    """Forecast future AQI independently for each facility."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Input DataFrame is empty.")

    required_columns = [
        TIMESTAMP_COLUMN,
        FACILITY_COLUMN,
        AQI_COLUMN,
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    data = df[
        required_columns
    ].copy()

    data[TIMESTAMP_COLUMN] = pd.to_datetime(
        data[TIMESTAMP_COLUMN],
        errors="coerce",
    )

    data[AQI_COLUMN] = pd.to_numeric(
        data[AQI_COLUMN],
        errors="coerce",
    )

    data = data.dropna(
        subset=[
            TIMESTAMP_COLUMN,
            FACILITY_COLUMN,
            AQI_COLUMN,
        ]
    )

    results = []

    for facility_id, group in data.groupby(FACILITY_COLUMN):
        group = group.sort_values(TIMESTAMP_COLUMN)

        if len(group) < 3:
            continue

        group = group.drop_duplicates(
            subset=[TIMESTAMP_COLUMN]
        )

        if len(group) < 3:
            continue

        x = (
            group[TIMESTAMP_COLUMN]
            - group[TIMESTAMP_COLUMN].min()
        ).dt.total_seconds().to_numpy().reshape(-1, 1)

        y = group[AQI_COLUMN].to_numpy()

        model = LinearRegression()
        model.fit(x, y)

        time_deltas = group[TIMESTAMP_COLUMN].diff().dropna()

        if time_deltas.empty:
            continue

        step = time_deltas.median()

        if pd.isna(step) or step <= pd.Timedelta(0):
            continue

        last_timestamp = group[TIMESTAMP_COLUMN].max()

        future_timestamps = [
            last_timestamp + step * index
            for index in range(1, horizon + 1)
        ]

        future_x = (
            pd.Series(future_timestamps)
            - group[TIMESTAMP_COLUMN].min()
        ).dt.total_seconds().to_numpy().reshape(-1, 1)

        predictions = model.predict(future_x)

        for timestamp, prediction in zip(
            future_timestamps,
            predictions,
        ):
            results.append(
                {
                    TIMESTAMP_COLUMN: timestamp,
                    FACILITY_COLUMN: facility_id,
                    "forecast_aqi": max(0.0, float(prediction)),
                }
            )

    return pd.DataFrame(results)