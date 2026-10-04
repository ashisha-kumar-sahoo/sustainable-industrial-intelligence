import pandas as pd


def forecast_water(
    data: pd.DataFrame,
    periods: int = 7
) -> pd.DataFrame:
    """
    Forecast future water consumption using
    the average historical consumption.
    """

    df = data.copy()

    if "reading_ts" not in df.columns:
        raise ValueError("Missing column: reading_ts")

    if "water_consumption_liters" not in df.columns:
        raise ValueError(
            "Missing column: water_consumption_liters"
        )

    if df.empty:
        return pd.DataFrame(
            columns=[
                "reading_ts",
                "forecast_water_liters"
            ]
        )

    df["reading_ts"] = pd.to_datetime(df["reading_ts"])

    average_water = df["water_consumption_liters"].mean()

    last_timestamp = df["reading_ts"].max()

    future_dates = pd.date_range(
        start=last_timestamp + pd.Timedelta(days=1),
        periods=periods,
        freq="D"
    )

    forecast = pd.DataFrame({
        "reading_ts": future_dates,
        "forecast_water_liters": average_water
    })

    return forecast