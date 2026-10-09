"""Scenario simulation integration and transparent local fallback."""

from __future__ import annotations

import pandas as pd

import config
from services.database_service import results
from utils import post_json


def simulate(dataset: str, action: str, reduction_pct: float) -> dict:
    """Run Member 6's simulation service or a clearly labelled local estimate.

    The local fallback applies the requested percentage to the sum of the
    latest 24-hour results. It is a deterministic what-if calculation, not an
    ML forecast or a measured future outcome.
    """
    simulation_url = config.simulation_url()
    if simulation_url:
        return post_json(
            simulation_url,
            {
                "dataset": dataset,
                "action": action,
                "reduction_pct": reduction_pct,
            },
        )

    dataset_results = results(dataset)
    if dataset_results.empty:
        return {
            "current": 0.0,
            "simulated": 0.0,
            "change_pct": 0.0,
            "sample": False,
            "mode": "local_estimate",
            "message": "No data is available for this scenario.",
        }

    latest_timestamp = dataset_results["timestamp"].max()
    cutoff = latest_timestamp - pd.Timedelta(hours=24)
    current_value = float(
        dataset_results.loc[
            dataset_results["timestamp"] > cutoff, "actual_value"
        ].sum()
    )
    simulated_value = current_value * (1 - reduction_pct / 100)

    return {
        "current": current_value,
        "simulated": simulated_value,
        "change_pct": -float(reduction_pct),
        "sample": False,
        "mode": "local_estimate",
        "message": "This is a deterministic estimate, not a forecast.",
    }
