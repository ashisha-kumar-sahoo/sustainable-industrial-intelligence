"""Retrieve only the PostgreSQL context required for a routed question."""

from ai.assistant import data_retriever as data

RESOURCE_ROUTES = {
    "current_status",
    "action",
    "diagnostic",
    "comparison",
    "energy",
    "energy_anomaly",
    "water",
    "waste",
    "air_quality",
    "traffic",
    "equipment",
    "safety",
}


def build_context(route: str, question: str = "") -> dict:
    """Load only the data sources needed by the selected assistant route."""
    context = {"route": route, "data": {}}
    normalized_question = (question or "").casefold()
    values = context["data"]

    if route in RESOURCE_ROUTES:
        values["alerts"] = data.get_alerts()

    if route in {
        "current_status",
        "action",
        "diagnostic",
        "comparison",
        "energy",
        "energy_anomaly",
        "water",
        "waste",
    }:
        if route in {
            "current_status",
            "action",
            "diagnostic",
            "comparison",
            "energy",
            "energy_anomaly",
        }:
            values["energy"] = data.get_latest_energy_data()
            try:
                values["m3_energy"] = data.get_m3_energy_intelligence()
            except Exception as exc:
                values["m3_energy_error"] = str(exc)

        if route in {"current_status", "action", "comparison", "water"}:
            values["water"] = data.get_latest_water_data()

        if route in {"current_status", "action", "comparison", "waste"}:
            values["waste"] = data.get_latest_waste_data()

    if route in {"current_status", "action", "diagnostic", "comparison", "air_quality"}:
        values["air_quality"] = data.get_latest_air_quality_data()

    if route in {"current_status", "action", "comparison", "traffic"}:
        values["traffic"] = data.get_latest_traffic_data()

    if route == "equipment":
        values["equipment"] = data.get_equipment_health()

    if route == "safety":
        values["safety_readings"] = data.get_latest_safety_data()

    if route == "historical":
        metric = (
            "water"
            if "water" in normalized_question
            else "waste"
            if "waste" in normalized_question
            else "energy"
        )
        values["historical_metric"] = metric
        values["history"] = data.get_resource_history(metric, days=7)

    if route == "scenario":
        if "water" in normalized_question:
            values["water"] = data.get_latest_water_data()
        else:
            values["energy"] = data.get_latest_energy_data()

    return context
