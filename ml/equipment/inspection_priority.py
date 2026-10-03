import pandas as pd


def calculate_inspection_priority(
    df: pd.DataFrame,
    temperature_column="temperature",
    vibration_column="vibration",
    utilization_column="utilization",
):
    """
    Calculate an equipment inspection priority score.

    The score combines temperature, vibration, and utilization.
    Higher scores indicate that an observation may need
    earlier inspection.
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
        temperature_column,
        vibration_column,
        utilization_column,
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

    for column in required_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce"
        )

    result = result.dropna(
        subset=required_columns
    ).reset_index(drop=True)

    result["temperature_risk"] = (
        result[temperature_column] >= 80
    ).astype(int)

    result["vibration_risk"] = (
        result[vibration_column] >= 5
    ).astype(int)

    result["utilization_risk"] = (
        result[utilization_column] >= 80
    ).astype(int)

    result["inspection_priority_score"] = (
        result["temperature_risk"]
        + result["vibration_risk"]
        + result["utilization_risk"]
    )

    result["inspection_priority"] = (
        result["inspection_priority_score"].apply(
            lambda score:
            "High"
            if score >= 2
            else (
                "Medium"
                if score == 1
                else "Low"
            )
        )
    )

    return result
