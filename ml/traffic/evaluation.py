import pandas as pd


def evaluate_congestion_results(
    df: pd.DataFrame,
    status_column="congestion_status",
):
    """
    Evaluate traffic congestion classifications.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    if status_column not in df.columns:
        raise ValueError(
            f"Column '{status_column}' not found."
        )

    return (
        df[status_column]
        .value_counts()
        .rename_axis("traffic_status")
        .reset_index(name="observation_count")
    )


def evaluate_parking_results(
    df: pd.DataFrame,
    status_column="parking_status",
):
    """
    Evaluate parking utilization classifications.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

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