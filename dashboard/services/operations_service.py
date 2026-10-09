"""Data shaping helpers for the dashboard's operational overview."""

from __future__ import annotations

import pandas as pd

from config import FAC

OPERATIONS_DATASETS = ["traffic", "equipment", "safety"]


def facility_severity_rows(layer, get_results) -> pd.DataFrame:
    """Build one severity record per facility for the estate map.

    ``get_results(dataset)`` must return the filtered AI-results DataFrame for
    the requested dataset. A facility with no recent records is marked NORMAL
    and receives a zero average rather than being omitted from the map.
    """
    rows = []
    layer_results = get_results(layer)

    for _, facility in FAC.iterrows():
        if not layer_results.empty:
            latest_timestamp = layer_results["timestamp"].max()
            recent_cutoff = latest_timestamp - pd.Timedelta(hours=6)
            facility_results = layer_results.loc[
                (layer_results["facility_id"] == facility["facility_id"])
                & (layer_results["timestamp"] > recent_cutoff)
            ]
        else:
            facility_results = layer_results

        if facility_results.empty:
            severity = "NORMAL"
            average_value = 0.0
        else:
            severities = facility_results["severity"]
            if severities.eq("HIGH").any():
                severity = "HIGH"
            elif severities.eq("MEDIUM").any():
                severity = "MEDIUM"
            else:
                severity = "NORMAL"
            average_value = float(facility_results["actual_value"].mean())

        height_by_severity = {"HIGH": 180, "MEDIUM": 120, "NORMAL": 70}
        rows.append(
            {
                "name": facility["name"],
                "lat": facility["lat"],
                "lon": facility["lon"],
                "severity": severity,
                "height": height_by_severity[severity],
                "tip": f"{layer}: {severity} (average {average_value:.0f})",
            }
        )

    return pd.DataFrame(rows)
