import pandas as pd
from sklearn.ensemble import IsolationForest


DEFAULT_FEATURES = [
    "aqi",
    "pm25",
    "pm10",
    "temperature",
    "co2",
    "no2",
]


def detect_environment_anomalies(
    df: pd.DataFrame,
    features=None,
    contamination="auto",
    random_state=42,
):
    """
    Detect environmental anomalies using Isolation Forest.

    Parameters
    ----------
    df : pandas.DataFrame
        Input environmental data.

    features : list, optional
        Numerical columns used by the model.

    contamination : float or "auto"
        Expected proportion of anomalies.

    random_state : int
        Random seed for reproducibility.

    Returns
    -------
    pandas.DataFrame
        Copy of the input data with anomaly results.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "Input DataFrame is empty."
        )

    if features is None:
        features = DEFAULT_FEATURES

    missing_features = [
        column
        for column in features
        if column not in df.columns
    ]

    if missing_features:
        raise ValueError(
            "Missing model features: "
            + ", ".join(missing_features)
        )

    result = df.copy()

    X = result[features].copy()

    # Make sure model features are numeric
    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Remove invalid rows for model fitting
    valid_mask = X.notna().all(axis=1)

    if valid_mask.sum() < 2:
        raise ValueError(
            "At least two valid observations are required."
        )

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state
    )

    model.fit(X.loc[valid_mask])

    result["anomaly_score"] = pd.NA
    result["anomaly_prediction"] = pd.NA
    result["anomaly_status"] = "Unknown"

    result.loc[valid_mask, "anomaly_score"] = (
        model.decision_function(X.loc[valid_mask])
    )

    result.loc[valid_mask, "anomaly_prediction"] = (
        model.predict(X.loc[valid_mask])
    )

    result.loc[
        valid_mask,
        "anomaly_status"
    ] = result.loc[
        valid_mask,
        "anomaly_prediction"
    ].map({
        1: "Normal",
        -1: "Anomaly"
    })

    return result


def get_anomaly_features():
    """
    Return the default features used for
    environmental anomaly detection.
    """

    return DEFAULT_FEATURES.copy()