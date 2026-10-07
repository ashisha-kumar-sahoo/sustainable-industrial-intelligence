"""Retrieve only the PostgreSQL context needed by a routed question."""
from ai.assistant import data_retriever as data


def build_context(route, question=""):
    result = {"route": route, "data": {}}
    q = (question or "").casefold()
    values = result["data"]
    if route in {"current_status", "action", "diagnostic", "comparison", "energy", "energy_anomaly", "water", "waste", "air_quality", "traffic", "equipment", "safety"}:
        values["alerts"] = data.get_alerts()
    if route in {"current_status", "action", "diagnostic", "comparison", "energy", "energy_anomaly", "water", "waste"}:
        if route in {"current_status", "action", "diagnostic", "comparison", "energy", "energy_anomaly"}:
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
        values["safety_alerts"] = [a for a in values.get("alerts", []) if "SAFETY" in (a.get("alert_type") or "").upper() or "INCIDENT" in (a.get("alert_type") or "").upper()]
    if route == "historical":
        metric = "water" if "water" in q else "waste" if "waste" in q else "energy"
        values["historical_metric"] = metric
        days = 7
        values["history"] = data.get_resource_history(metric, days)
    if route == "scenario":
        if "water" in q:
            values["water"] = data.get_latest_water_data()
        else:
            values["energy"] = data.get_latest_energy_data()
    return result
