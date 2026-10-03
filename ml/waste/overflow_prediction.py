import pandas as pd


def predict_overflow(
    data,
    overflow_threshold=80
):
    """
    Predict waste bin overflow risk
    using fill level and fill rate.
    """

    data = data.copy()

    # Default values
    data["overflow_risk"] = "LOW"
    data["overflow_prediction"] = False

    # Medium risk
    data.loc[
        data["fill_level"] >= 60,
        "overflow_risk"
    ] = "MEDIUM"

    # High risk
    data.loc[
        data["fill_level"] >= overflow_threshold,
        "overflow_risk"
    ] = "HIGH"

    # Very high fill rate can also indicate risk
    data.loc[
        (data["fill_rate"] > 10) &
        (data["fill_level"] >= 50),
        "overflow_risk"
    ] = "HIGH"

    # Overflow prediction
    data["overflow_prediction"] = (
        data["overflow_risk"] == "HIGH"
    )

    return data