import math
import numbers


def _deviation_magnitude(value):
    """Return a usable absolute deviation, treating None/NaN as no deviation."""
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        return 0.0
    try:
        if math.isnan(value):
            return 0.0
    except (TypeError, ValueError):
        return 0.0
    return abs(float(value))


def calculate_risk(anomaly):

    deviation = _deviation_magnitude(
        anomaly.get("deviation_pct", 0)
    )

    if deviation > 300:
        return "CRITICAL"

    elif deviation > 100:
        return "HIGH"

    elif deviation > 30:
        return "MEDIUM"

    else:
        return "LOW"
