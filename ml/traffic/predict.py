import pandas as pd

from ml.traffic.preprocessing import (
    preprocess_traffic_data,
    create_traffic_features,
)
from ml.traffic.congestion_detection import (
    detect_traffic_congestion,
)
from ml.traffic.hotspot_detection import (
    detect_traffic_hotspots,
)
from ml.traffic.parking_analysis import (
    analyze_parking_utilization,
)


def predict_traffic_status(
    df: pd.DataFrame,
):
    """
    Run the traffic intelligence pipeline.

    Accepts any compatible DataFrame and does not depend
    on a specific dataset.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input data must be a pandas DataFrame."
        )

    # Step 1: Preprocess traffic data
    data = preprocess_traffic_data(df)

    # Step 2: Create reusable traffic features
    data = create_traffic_features(data)

    # Step 3: Detect congestion
    data = detect_traffic_congestion(data)

    # Step 4: Detect traffic hotspots
    hotspot_summary = detect_traffic_hotspots(data)

    return data, hotspot_summary