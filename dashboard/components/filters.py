"""Global facility, zone, and date filters plus filtered data accessors."""

import datetime

import pandas as pd
import streamlit as st

import config
from services.alert_service import alerts
from services.database_service import forecast, raw, results
from utils import fid, safe


def render_sidebar_filters() -> None:
    """Render the shared filters and keep invalid zone choices in sync."""
    facility_options = ["All", *config.FAC["name"].tolist()]
    facility_name = st.selectbox("Facility", facility_options, key="g_fac")

    if facility_name == "All":
        zone_options = config.ZONES
    else:
        facility_zones = config.FAC.loc[
            config.FAC["name"] == facility_name, "zones"
        ]
        zone_options = facility_zones.iloc[0] if not facility_zones.empty else []

    allowed_zones = ["All", *zone_options]
    if st.session_state.get("g_zone", "All") not in allowed_zones:
        st.session_state.g_zone = "All"

    st.selectbox("Zone", allowed_zones, key="g_zone")
    today = datetime.date.today()
    st.date_input(
        "Date range",
        (today - datetime.timedelta(days=6), today),
        key="g_dates",
    )


def filt(data: pd.DataFrame, dates: bool = True) -> pd.DataFrame:
    """Apply the current sidebar filters to a returned DataFrame."""
    state = st.session_state
    facility_name = state.get("g_fac", "All")
    zone_name = state.get("g_zone", "All")
    date_range = state.get("g_dates")

    if data is None or data.empty:
        return pd.DataFrame() if data is None else data.copy()

    filtered = data.copy()
    if facility_name != "All":
        filtered = filtered.loc[filtered["facility_id"] == fid(facility_name)]
    if zone_name != "All":
        filtered = filtered.loc[filtered["zone_id"] == zone_name]

    if dates and date_range and len(date_range) == 2:
        timestamps = pd.to_datetime(filtered["timestamp"], errors="coerce")
        filtered = filtered.loc[
            timestamps.dt.date.ge(date_range[0])
            & timestamps.dt.date.le(date_range[1])
        ]

    return filtered


def RES(dataset: str) -> pd.DataFrame:
    """Return AI-result rows after applying the global filters."""
    data = safe(
        results,
        dataset,
        default=pd.DataFrame(),
        label=f"{dataset} AI results",
    )
    return filt(data)


def RAW(dataset: str, limit: int = 5000) -> pd.DataFrame:
    """Return raw domain rows for the current filters."""
    state = st.session_state
    date_range = state.get("g_dates") or (None, None)
    facility_name = state.get("g_fac", "All")
    zone_name = state.get("g_zone", "All")

    return safe(
        raw,
        dataset,
        fid(facility_name) if facility_name != "All" else None,
        zone_name if zone_name != "All" else None,
        date_range[0] if len(date_range) > 0 else None,
        date_range[1] if len(date_range) > 1 else None,
        limit,
        default=pd.DataFrame(),
        label=f"{dataset} raw data",
    )


def ALERTS() -> pd.DataFrame:
    """Return alerts after applying facility/zone filters (not date filters)."""
    data = safe(alerts, default=pd.DataFrame(), label="Alerts")
    return filt(data, dates=False)


def FORECAST(dataset: str, label: str | None = None) -> pd.DataFrame:
    """Return forecast rows after facility/zone filtering, ignoring dates."""
    data = safe(
        forecast,
        dataset,
        default=pd.DataFrame(),
        label=label or f"{dataset} forecast",
    )
    return filt(data, dates=False)
