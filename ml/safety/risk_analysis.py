import pandas as pd


def calculate_safety_risk(
    df: pd.DataFrame,
    severity_column="severity",
    people_column="people_affected",
    response_column="response_time",
):
    """
    Calculate a safety risk level for each incident.

    Risk is based on incident severity, people affected,
    and response time.
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

    result[people_column] = pd.to_numeric(
        result[people_column],
        errors="coerce"
    )

    result[response_column] = pd.to_numeric(
        result[response_column],
        errors="coerce"
    )

    result[severity_column] = (
        result[severity_column]
        .astype(str)
        .str.strip()
        .str.title()
    )

    result = result.dropna(
        subset=[
            people_column,
            response_column,
        ]
    ).reset_index(drop=True)

    def classify_risk(row):
        score = 0

        if row[severity_column] == "Critical":
            score += 3
        elif row[severity_column] == "High":
            score += 2
        elif row[severity_column] == "Medium":
            score += 1

        if row[people_column] >= 3:
            score += 2
        elif row[people_column] >= 1:
            score += 1

        if row[response_column] >= 15:
            score += 2
        elif row[response_column] >= 10:
            score += 1

        if score >= 5:
            return "High"
        elif score >= 3:
            return "Medium"

        return "Low"

    result["safety_risk"] = result.apply(
        classify_risk,
        axis=1
    )

    return result


def summarize_safety_risk(
    df: pd.DataFrame,
    risk_column="safety_risk",
):
    """
    Summarize safety risk levels.
    """

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