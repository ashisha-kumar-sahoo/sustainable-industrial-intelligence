"""KPI-card data preparation and rendering."""

import streamlit as st

import config
from services.database_service import results
from services.resource_service import kpi_for
from utils import safe

SEVERITY_CLASS = {"HIGH": "high", "MEDIUM": "medium", "NORMAL": "normal"}


def kpis_data() -> dict:
    """Calculate KPI values for every domain enabled by the selected profile."""
    cards = {}
    for dataset in config.active_domains():
        data = safe(
            results,
            dataset,
            default=None,
            label=f"{dataset} KPI data",
        )
        if data is None:
            cards[dataset] = (config.KP[dataset][0], "–", "unavailable", "NORMAL", 0)
        else:
            cards[dataset] = kpi_for(dataset, data)
    return cards


def badge(severity: str) -> str:
    """Return the short label used inside a KPI card."""
    labels = {"HIGH": "High", "MEDIUM": "Medium", "NORMAL": "Normal"}
    return labels.get(severity, "Normal")


def kpi_html(cards: list[tuple]) -> str:
    """Render KPI cards using the dashboard's shared CSS classes."""
    card_markup = []
    for label, value, delta, severity in cards:
        css_class = SEVERITY_CLASS.get(severity, "normal")
        card_markup.append(
            f'<div class="kpi s-{css_class}">'
            f"<small>{label}</small><b>{value}</b>"
            f"<i>{delta} · {badge(severity)}</i></div>"
        )
    return '<div class="kg">' + "".join(card_markup) + "</div>"


def render_kpis(cards: list[tuple]) -> None:
    """Display a row of KPI cards."""
    st.markdown(kpi_html(cards), unsafe_allow_html=True)
