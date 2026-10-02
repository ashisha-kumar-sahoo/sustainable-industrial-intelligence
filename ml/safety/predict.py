import pandas as pd

from ml.safety.preprocessing import (
    preprocess_safety_data,
    create_safety_features,
)
from ml.safety.risk_analysis import (
    calculate_safety_risk,
)
from ml.safety.inspection_priority import (
    calculate_safety_inspection_priority,
)
from ml.safety.hotspot_detection import (
    detect_safety_hotspots,
)


def predict_safety_status(
    df: pd.DataFrame,
):
    """
    Run the complete safety intelligence pipeline.

    The function accepts any compatible DataFrame
    and does not depend on a specific dataset or file.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    data = preprocess_safety_data(df)

    data = create_safety_features(data)

    data = calculate_safety_risk(data)

    data = calculate_safety_inspection_priority(data)

    hotspot_summary = detect_safety_hotspots(data)

    return data, hotspot_summary