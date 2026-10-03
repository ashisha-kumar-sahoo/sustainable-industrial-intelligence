import pandas as pd


def evaluate_anomaly_results(
    df: pd.DataFrame,
    prediction_column="anomaly_prediction",
):
    """
    Evaluate anomaly detection results.

    Counts normal and anomalous observations.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    if prediction_column not in df.columns:
        raise ValueError(
            f"Column '{prediction_column}' not found."
        )

    result = df[prediction_column].dropna()

    total = len(result)
    anomalies = (result == -1).sum()
    normal = (result == 1).sum()

    anomaly_rate = (
        anomalies / total
        if total > 0
        else 0
    )

    return {
        "total_observations": total,
        "normal_observations": normal,
        "anomalous_observations": anomalies,
        "anomaly_rate": anomaly_rate,
    }


def evaluate_risk_results(
    df: pd.DataFrame,
    risk_column="environment_risk",
):
    """
    Evaluate environmental risk classifications.

    Returns the count of observations
    in each risk category.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

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