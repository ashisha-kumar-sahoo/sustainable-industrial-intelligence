import pandas as pd

from ml.environment.preprocessing import (
    preprocess_environment_data,
    create_environment_features,
)
from ml.environment.anomaly_detection import (
    detect_environment_anomalies,
)
from ml.environment.risk_analysis import (
    calculate_environment_risk,
)


def predict_environment_status(
    df: pd.DataFrame,
):
    """
    Run the complete environmental intelligence pipeline.

    The function accepts any compatible DataFrame
    and does not depend on a specific dataset.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    # Step 1: Preprocess
    data = preprocess_environment_data(df)

    # Step 2: Create ML features
    data = create_environment_features(data)

    # Step 3: Detect anomalies
    data = detect_environment_anomalies(data)

    # Step 4: Calculate environmental risk
    data = calculate_environment_risk(data)

    return data