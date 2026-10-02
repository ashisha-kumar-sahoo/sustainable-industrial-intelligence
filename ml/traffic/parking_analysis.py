import pandas as pd


def analyze_parking_utilization(
    df: pd.DataFrame,
    capacity_column="parking_capacity",
    occupied_column="occupied_spaces",
):
    """
    Analyze parking utilization from capacity
    and occupied-space measurements.

    The function is dataset-independent and accepts
    any compatible Pandas DataFrame.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "Input DataFrame is empty."
        )

    required_columns = [
        capacity_column,
        occupied_column,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    result = df.copy()

    result[capacity_column] = pd.to_numeric(
        result[capacity_column],
        errors="coerce"
    )

    result[occupied_column] = pd.to_numeric(
        result[occupied_column],
        errors="coerce"
    )

    result = result.dropna(
        subset=required_columns
    ).reset_index(drop=True)

    if (result[capacity_column] <= 0).any():
        raise ValueError(
            "Parking capacity must be greater than zero."
        )

    result["parking_utilization"] = (
        result[occupied_column]
        / result[capacity_column]
        * 100
    )

    result["parking_status"] = result[
        "parking_utilization"
    ].apply(
        lambda value:
        "High Utilization"
        if value >= 80
        else "Normal Utilization"
    )

    return result


def summarize_parking_utilization(
    df: pd.DataFrame,
    status_column="parking_status",
):
    """
    Summarize parking utilization categories.
    """

    if status_column not in df.columns:
        raise ValueError(
            f"Column '{status_column}' not found."
        )

    return (
        df[status_column]
        .value_counts()
        .rename_axis("parking_status")
        .reset_index(name="observation_count")
    )