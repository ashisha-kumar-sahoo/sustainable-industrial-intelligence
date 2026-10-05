import pandas as pd


def predict_waste(
    data: pd.DataFrame,
    periods: int = 7
) -> pd.DataFrame:
    """
    Predict future waste quantity using
    the average historical waste quantity.
    """

    df = data.copy()

    required_columns = [
        "reading_ts",
        "waste_quantity_kg",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing waste columns: {missing_columns}"
        )

    if df.empty:
        return pd.DataFrame(
            columns=[
                "reading_ts",
                "predicted_waste_quantity_kg",
            ]
        )

    df["reading_ts"] = pd.to_datetime(df["reading_ts"])

    average_waste = df["waste_quantity_kg"].mean()

    last_timestamp = df["reading_ts"].max()

    future_dates = pd.date_range(
        start=last_timestamp + pd.Timedelta(days=1),
        periods=periods,
        freq="D",
    )

    prediction = pd.DataFrame({
        "reading_ts": future_dates,
        "predicted_waste_quantity_kg": average_waste,
    })

    return prediction