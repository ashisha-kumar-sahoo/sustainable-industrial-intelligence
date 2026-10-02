import pandas as pd


def analyze_equipment_utilization(
    df: pd.DataFrame,
    utilization_column="utilization",
):
    """
    Analyze equipment utilization levels.

    Works with any Pandas DataFrame containing
    a utilization column.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "Input DataFrame is empty."
        )

    if utilization_column not in df.columns:
        raise ValueError(
            f"Column '{utilization_column}' not found."
        )

    result = df.copy()

    result[utilization_column] = pd.to_numeric(
        result[utilization_column],
        errors="coerce"
    )

    result = result.dropna(
        subset=[utilization_column]
    ).reset_index(drop=True)

    if (
        (result[utilization_column] < 0).any()
        or (result[utilization_column] > 100).any()
    ):
        raise ValueError(
            "Utilization must be between 0 and 100."
        )

    result["utilization_status"] = (
        result[utilization_column].apply(
            lambda value:
            "High Utilization"
            if value >= 80
            else (
                "Low Utilization"
                if value < 40
                else "Normal Utilization"
            )
        )
    )

    return result


def summarize_equipment_utilization(
    df: pd.DataFrame,
    status_column="utilization_status",
):
    """
    Summarize equipment utilization categories.
    """

    if status_column not in df.columns:
        raise ValueError(
            f"Column '{status_column}' not found."
        )

    return (
        df[status_column]
        .value_counts()
        .rename_axis("utilization_status")
        .reset_index(
            name="observation_count"
        )
    )