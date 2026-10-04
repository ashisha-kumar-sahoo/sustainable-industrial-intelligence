"""Scenario simulation (Member 6 service). Moved unchanged from data_service.simulate.
POSTs to SIMULATION_URL when set; otherwise returns the simple SIMULATED estimate from the last 24h of AI results."""
import pandas as pd
import config
from utils import post_json
from services.database_service import results


def simulate(ds, action, pct):
    """Member 6 simulation. POST SIMULATION_URL {dataset, action, reduction_pct}. Fallback = simple estimate (SIMULATED)."""
    if config.simulation_url(): return post_json(config.simulation_url(), dict(dataset=ds, action=action, reduction_pct=pct))
    r = results(ds); cur = float(r[r["timestamp"] > r["timestamp"].max() - pd.Timedelta(hours=24)]["actual_value"].sum()); return dict(current=cur, simulated=cur * (1 - pct / 100), change_pct=-pct, sample=True)
