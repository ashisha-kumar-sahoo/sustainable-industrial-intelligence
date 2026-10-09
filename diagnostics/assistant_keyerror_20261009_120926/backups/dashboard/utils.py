"""Small reusable helpers shared by dashboard components and pages."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen

import streamlit as st

from config import FAC


def fid(facility_name: str) -> int:
    """Translate a displayed facility name into its configured identifier."""
    matches = FAC.loc[FAC["name"] == facility_name, "facility_id"]
    if matches.empty:
        raise ValueError(f"Unknown facility name: {facility_name!r}")
    return int(matches.iloc[0])


def fname(facility_id: int) -> str:
    """Translate a facility identifier into its displayed name."""
    matches = FAC.loc[FAC["facility_id"] == facility_id, "name"]
    if matches.empty:
        return f"Facility {facility_id}"
    return str(matches.iloc[0])


def post_json(url: str, body: dict, timeout: float = 15) -> dict:
    """POST a JSON payload and decode the JSON response."""
    request = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def safe(function, *args, default=None, label="", **kwargs):
    """Run a dashboard operation and show a non-fatal user-facing warning."""
    try:
        return function(*args, **kwargs)
    except Exception as exc:
        operation_name = label or getattr(function, "__name__", "Operation")
        st.warning(
            f"⚠️ {operation_name} is temporarily unavailable "
            f"({type(exc).__name__}). The rest of the dashboard can continue."
        )
        return default


def drill(dataset: str, facility_id: int) -> None:
    """Open Raw Data Explorer with the chosen dataset and facility selected."""
    state = st.session_state
    state.page = "Raw Data Explorer"
    state.rx_ds = dataset
    state.g_fac = fname(facility_id)
    state.g_zone = "All"


def ask_ai(question: str) -> None:
    """Open the assistant page and prefill the user's question."""
    st.session_state.page = "AI Assistant"
    st.session_state.aq = question


def nav(page_name: str) -> None:
    """Change the dashboard's selected page."""
    st.session_state.page = page_name
