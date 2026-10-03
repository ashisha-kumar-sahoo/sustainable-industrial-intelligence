import pandas as pd


def calculate_safety_inspection_priority(
    df: pd.DataFrame,
    severity_column="severity",
    people_column="people_affected",
    response_column="response_time",
):
    """
    Calculate inspection priority for safety incidents.

    Higher priority is assigned to incidents with greater
    severity, impact, or slower response.
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
        severity_column,
        people_column,
        response_column,
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

    result[severity_column] = (
        result[severity_column]
        .astype(str)
        .str.strip()
        .str.title()
    )

    result[people_column] = pd.to_numeric(
        result[people_column],
        errors="coerce"
    )

    result[response_column] = pd.to_numeric(
        result[response_column],
        errors="coerce"
    )

    result = result.dropna(
        subset=[
            severity_column,
            people_column,
            response_column,
        ]
    ).reset_index(drop=True)

    result["severity_priority"] = (
        result[severity_column].map({
            "Low": 0,
            "Medium": 1,
            "High": 2,
            "Critical": 3,
        }).fillna(0)
    )

    result["impact_priority"] = (
        result[people_column] >= 3
    ).astype(int)

    result["response_priority"] = (
        result[response_column] >= 15
    ).astype(int)

    result["inspection_priority_score"] = (
        result["severity_priority"]
        + result["impact_priority"]
        + result["response_priority"]
    )

    result["inspection_priority"] = (
        result["inspection_priority_score"].apply(
            lambda score:
            "High"
            if score >= 4
            else (
                "Medium"
                if score >= 2
                else "Low"
            )
        )
    )

    return result