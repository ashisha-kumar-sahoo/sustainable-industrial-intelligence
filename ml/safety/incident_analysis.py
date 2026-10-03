import pandas as pd


def analyze_safety_incidents(
    df: pd.DataFrame,
    incident_column="incident_type",
    severity_column="severity",
):
    """
    Analyze safety incidents by type and severity.

    Works with any compatible Pandas DataFrame.
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
        incident_column,
        severity_column,
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

    data = df.copy()

    data[incident_column] = (
        data[incident_column]
        .astype(str)
        .str.strip()
    )

    data[severity_column] = (
        data[severity_column]
        .astype(str)
        .str.strip()
        .str.title()
    )

    summary = (
        data.groupby(
            [incident_column, severity_column]
        )
        .size()
        .reset_index(
            name="incident_count"
        )
    )

    return summary


def summarize_incident_types(
    df: pd.DataFrame,
    incident_column="incident_type",
):
    """
    Count incidents by incident type.
    """

    if incident_column not in df.columns:
        raise ValueError(
            f"Column '{incident_column}' not found."
        )

    return (
        df[incident_column]
        .value_counts()
        .rename_axis("incident_type")
        .reset_index(
            name="incident_count"
        )
    )