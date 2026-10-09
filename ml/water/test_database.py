"""Water loader contract tests.

The live PostgreSQL integration tests live under tests/integration.
This module must remain safe to collect without database credentials.
"""

import pandas as pd

from .data_loader import validate_columns


def test_water_required_columns_are_validated():
    data = pd.DataFrame({
        "facility_id": [1],
        "sensor_id": [1],
        "reading_ts": ["2026-10-01 00:00:00+05:30"],
        "water_consumption_liters": [1000.0],
        "flow_rate": [100.0],
    })
    assert validate_columns(data) is True
