import pandas as pd

from ml.equipment.preprocessing import (
    preprocess_equipment_data,
    create_equipment_features,
)
from ml.equipment.anomaly_detection import (
    detect_equipment_anomalies,
)
from ml.equipment.inspection_priority import (
    calculate_inspection_priority,
)


def predict_equipment_status(
    df: pd.DataFrame,
):
    """
    Run the complete equipment intelligence pipeline.

    The function accepts any compatible DataFrame
    and does not depend on a specific dataset or file.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    data = preprocess_equipment_data(df)

    data = create_equipment_features(data)

    data = detect_equipment_anomalies(data)

    data = calculate_inspection_priority(data)

    return data