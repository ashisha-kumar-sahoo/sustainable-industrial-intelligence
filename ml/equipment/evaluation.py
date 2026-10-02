import pandas as pd


def evaluate_anomaly_results(
    df: pd.DataFrame,
    prediction_column="anomaly_prediction",
):
    """
    Summarize equipment anomaly detection results.
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


def evaluate_inspection_results(
    df: pd.DataFrame,
    priority_column="inspection_priority",
):
    """
    Summarize equipment inspection priorities.
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
            name="equipment_count"
        )
    )