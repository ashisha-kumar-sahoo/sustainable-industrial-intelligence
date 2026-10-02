import pandas as pd


def evaluate_risk_results(
    df: pd.DataFrame,
    risk_column="safety_risk",
):
    """
    Summarize safety risk results.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    if risk_column not in df.columns:
        raise ValueError(
            f"Column '{risk_column}' not found."
        )

    return (
        df[risk_column]
        .value_counts()
        .rename_axis("risk_level")
        .reset_index(
            name="incident_count"
        )
    )


def evaluate_inspection_results(
    df: pd.DataFrame,
    priority_column="inspection_priority",
):
    """
    Summarize safety inspection priorities.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    if priority_column not in df.columns:
        raise ValueError(
            f"Column '{priority_column}' not found."
        )

    return (
        df[priority_column]
        .value_counts()
        .rename_axis("inspection_priority")
        .reset_index(
            name="incident_count"
        )
    )


def evaluate_hotspot_results(
    df: pd.DataFrame,
    status_column="hotspot_status",
):
    """
    Summarize safety hotspot results.
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
        .rename_axis("hotspot_status")
        .reset_index(
            name="location_count"
        )
    )