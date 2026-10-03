import pandas as pd


def calculate_environment_risk(
    df: pd.DataFrame,
    aqi_column="aqi",
    pm25_column="pm25",
    no2_column="no2",
):
    """
    Calculate an operational environmental risk level
    from measurable environmental indicators.

    This is a rule-based risk classification and is not
    a medical or health diagnosis.
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
        aqi_column,
        pm25_column,
        no2_column,
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

    def classify_risk(row):
        aqi = row[aqi_column]
        pm25 = row[pm25_column]
        no2 = row[no2_column]

        warning_count = 0

        if aqi >= 100:
            warning_count += 1

        if pm25 >= 50:
            warning_count += 1

        if no2 >= 40:
            warning_count += 1

        if warning_count >= 2:
            return "High"

        if warning_count == 1:
            return "Moderate"

        return "Low"

    result["environment_risk"] = result.apply(
        classify_risk,
        axis=1
    )

    return result


def summarize_environment_risk(
    df: pd.DataFrame,
    risk_column="environment_risk",
):
    """
    Summarize the number of observations
    in each environmental risk category.
    """

    if risk_column not in df.columns:
        raise ValueError(
            f"Column '{risk_column}' not found."
        )

    summary = (
        df[risk_column]
        .value_counts()
        .rename_axis("risk_level")
        .reset_index(name="observation_count")
    )

    return summary