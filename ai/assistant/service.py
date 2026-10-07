"""Decision-first assistant: PostgreSQL and Python decide; local Qwen explains."""
import json
import os
import re
from collections import Counter, defaultdict
from datetime import date, datetime

import requests

from ai.assistant.query_router import route_question
from ai.assistant.context_builder import build_context
from ai.assistant.response_generator import create_response, create_energy_anomaly_response
from ai.recommendations.rule_engine import (
    find_highest_energy_consumer, find_energy_anomalies,
    find_highest_water_consumer, find_water_anomalies,
    find_highest_waste_producer, find_waste_anomalies,
)
from ai.recommendations.decision_summary import build_decision_summary
from ai.recommendations.recommendation_engine import generate_recommendations
from ai.recommendations.explanation import explain_recommendation
from ai.simulation.scenario_parser import parse_energy_reduction_question
from ai.simulation.simulation_engine import simulate_energy_reduction
from ai.assistant.data_retriever import get_facility_energy_baseline


def _latest_m3(records):
    latest = {}
    for item in records or []:
        key = item.get("facility_id")
        if key is not None and (key not in latest or str(item.get("timestamp", "")) > str(latest[key].get("timestamp", ""))):
            latest[key] = item
    return list(latest.values())


def _answer(summary, evidence=None, explanation=None, action="Review the evidence and verify the relevant readings.", basis="PostgreSQL"):
    return create_response(summary, evidence or [], action, basis) | {"explanation": explanation or summary}


def _context_summary(context):
    data = context.get("data", {})
    counts = {key: len(value) for key, value in data.items() if isinstance(value, list)}
    summary = {"route": context.get("route"), "record_counts": counts}
    for key in ("historical_metric", "m3_energy_error"):
        if key in data:
            summary[key] = data[key]
    return summary


def _resource_answer(metric, data):
    name = metric.capitalize()
    if metric == "energy":
        highest = find_highest_energy_consumer(data)
        return highest, [], "energy_consumption_kwh", "kWh", "energy_readings"
    if metric == "water":
        highest = find_highest_water_consumer(data)
        anomalies = find_water_anomalies(data)
        return highest, anomalies, "water_consumption_liters", "litres", "water_readings"
    highest = find_highest_waste_producer(data)
    anomalies = find_waste_anomalies(data)
    return highest, anomalies, "waste_quantity_kg", "kg", "waste_readings"


def _recommend(problems):
    recs = generate_recommendations(problems) if problems else []
    return recs, [explain_recommendation(r) for r in recs]


def _scenario(question, metric, context):
    parsed = parse_energy_reduction_question(question)
    facility_match = re.search(r"what if\s+(.+?)\s+(?:reduces?|decreases?|lowers?)\b", question, re.I)
    facility = parsed.get("facility_name") if parsed else (facility_match.group(1).strip(" '\\\"?.") if facility_match else None)
    if facility and re.fullmatch(r"(?:energy|water)(?:\s+(?:consumption|usage|use))?(?:\s+is)?", facility, re.I):
        facility = None
    reduction = re.search(r"(?:reduce|reduces|decrease|decreases|lower|lowers).*?(\d+(?:\.\d+)?)\s*%", question, re.I)
    if not reduction:
        return {"message": "Specify a reduction percentage to run a simulation."}, ""
    pct = float(reduction.group(1))
    if not 0 < pct < 100:
        return {"message": "The simulated reduction must be greater than 0% and less than 100%."}, ""
    if metric == "water":
        rows = context.get("data", {}).get("water", [])
        if facility:
            matched = [r for r in rows if facility.casefold() in r.get("facility_name", "").casefold()]
            rows = matched
        if not rows:
            return {"message": "No current water data is available for this simulation."}, ""
        baseline_row = rows[0] if facility else None
        base = baseline_row.get("water_consumption_liters") if baseline_row else sum(r.get("water_consumption_liters") or 0 for r in rows)
        scenario_facility = baseline_row.get("facility_name") if baseline_row else "All facilities"
        return {"scenario_type": "water_reduction", "facility_name": scenario_facility,
                "baseline_value": base, "simulated_value": round(base * (1-pct/100), 2),
                "estimated_change_pct": -pct, "unit": "litres", "status": "SIMULATED",
                "assumptions": ["Applies the requested reduction to the latest water reading; this is not a forecast."]}, "water_readings"
    if not facility:
        rows = context.get("data", {}).get("energy", [])
        if not rows:
            return {"message": "No current energy data is available for this simulation."}, ""
        baseline = {"facility_id": None, "facility_name": "All facilities",
                    "energy_consumption_kwh": sum(r.get("energy_consumption_kwh") or 0 for r in rows)}
    else:
        baseline = next((r for r in context.get("data", {}).get("energy", []) if facility.casefold() in r.get("facility_name", "").casefold()), None)
        if baseline is None:
            baseline = get_facility_energy_baseline(facility)
    if not baseline:
        return {"message": f"No latest energy data found for {facility}."}, "energy_readings"
    return simulate_energy_reduction(baseline["facility_id"], baseline["facility_name"], baseline["energy_consumption_kwh"], pct), "energy_readings"


def _build_decision(route, question, context):
    d = context.get("data", {})
    q = question.casefold()
    recs, explanations = [], []
    if route in {"energy", "comparison", "energy_anomaly", "water"}:
        metric = "water" if "water" in q else "waste" if "waste" in q else "energy"
        rows = d.get(metric, [])
        if metric == "energy":
            # Same M3 output and snapshot for comparison and anomaly questions.
            anomalies = find_energy_anomalies(_latest_m3(d.get("m3_energy", [])))
            highest = find_highest_energy_consumer(rows)
            problems = [{"type": "energy_anomaly", "facility_id": a["facility_id"], "facility_name": a["facility_name"],
                         "actual_value": a["actual_value"], "expected_value": a["expected_value"], "deviation_pct": a["deviation_pct"],
                         "severity": a.get("severity"), "message": f"Energy deviation {a.get('deviation_pct')}%"} for a in anomalies]
            recs, explanations = _recommend(problems)
            if route == "energy_anomaly":
                decision = {"comparison_type": "energy_anomaly", "anomalies": anomalies, "total_anomalies": len(anomalies),
                            "severity_counts": dict(Counter((a.get("severity") or "UNCLASSIFIED").upper() for a in anomalies)),
                            "m3_error": d.get("m3_energy_error")}
                answer = create_energy_anomaly_response(anomalies, recs)
                answer["explanation"] = "Severity totals are counted from the same anomaly records shown in evidence."
            else:
                decision = {"comparison_type": "energy", "highest_consumer": highest, "anomalies": anomalies, "total_anomalies": len(anomalies)}
                if highest:
                    answer = _answer(f"{highest['facility_name']} has the highest latest energy use at {highest['energy_consumption_kwh']} kWh.",
                        [f"Latest reading: {highest['reading_ts']}", f"Detected energy anomalies: {len(anomalies)}"],
                        "Energy usage ranking is based on the latest PostgreSQL reading per facility.",
                        "Inspect the highest-consuming facility and review any listed anomaly.", "PostgreSQL energy_readings; M3 energy intelligence")
                else:
                    answer = _answer("No current energy data is available.", basis="PostgreSQL energy_readings")
        else:
            highest, anomalies, value_key, unit, basis = _resource_answer(metric, rows)
            problems = [{"type": f"{metric}_anomaly", "facility_name": a.get("facility_name"), "facility_id": a.get("facility_id"),
                         "severity": "HIGH", "message": a.get("anomaly_reason") or f"Recorded {metric} anomaly"} for a in anomalies]
            recs, explanations = _recommend(problems)
            decision = {"comparison_type": metric, "highest_consumer" if metric == "water" else "highest_producer": highest,
                        "anomalies": anomalies, "total_anomalies": len(anomalies)}
            answer = _answer(f"{highest['facility_name']} has the highest latest {metric} value at {highest[value_key]} {unit}." if highest else f"No current {metric} data is available.",
                [f"Recorded anomalies: {len(anomalies)}"] if highest else [], f"Comparison uses the latest reading per facility.",
                f"Review the {metric} reading and investigate any recorded anomalies.", f"PostgreSQL {basis}")
    elif route == "historical":
        metric = d.get("historical_metric", "energy")
        history = d.get("history", [])
        totals = defaultdict(float)
        for row in history:
            ts, val = row.get("reading_ts"), row.get("value")
            if ts is not None and val is not None:
                totals[ts.date() if hasattr(ts, "date") else str(ts)[:10]] += val
        daily = [{"date": k, "total": round(v, 2)} for k, v in sorted(totals.items())]
        highest_reading = max((r for r in history if r.get("value") is not None), key=lambda r:r["value"], default=None)
        trend = "insufficient data"
        if len(daily) >= 2:
            trend = "increased" if daily[-1]["total"] > daily[0]["total"] else "decreased" if daily[-1]["total"] < daily[0]["total"] else "was unchanged"
        decision = {"data_type": metric, "period_days": 7, "total_readings": len(history), "daily_totals": daily,
                    "highest_reading": highest_reading, "lowest_reading": min((r for r in history if r.get("value") is not None), key=lambda r:r["value"], default=None), "trend": trend}
        answer = _answer(f"{metric.title()} {trend} across the 7-day period based on {len(history)} readings." if history else f"No {metric} readings are available for the requested period.",
                         [f"Days with readings: {len(daily)}", f"Daily totals: {daily}"], f"Trend compares the first and last daily totals.", "Use this trend as historical analysis, not a forecast.", f"PostgreSQL {metric}_readings")
    elif route == "diagnostic":
        energy = d.get("energy", [])
        m3 = _latest_m3(d.get("m3_energy", []))
        candidates = [r.get("facility_name") for r in energy if r.get("facility_name") and r["facility_name"].casefold() in q]
        facility = candidates[0] if candidates else None
        row = next((r for r in energy if r.get("facility_name") == facility), None)
        intelligence = next((r for r in m3 if r.get("facility_id") == (row or {}).get("facility_id")), None)
        finding = {"facility_name": facility, "latest_reading": row, "energy_intelligence": intelligence}
        if row and intelligence:
            finding["diagnosis"] = "M3 flags a deviation from the preceding reading for this facility/sensor." if intelligence.get("anomaly") else "M3 does not flag this latest reading as anomalous against its preceding facility/sensor reading."
            problem = [{"type": "energy_anomaly", "facility_name": facility, "facility_id": row["facility_id"], "actual_value": intelligence.get("actual_value"),
                       "expected_value": intelligence.get("expected_value"), "deviation_pct": intelligence.get("deviation_pct"), "severity": intelligence.get("severity"), "message": finding["diagnosis"]}] if intelligence.get("anomaly") else []
            recs, explanations = _recommend(problem)
            evidence = [f"Actual: {intelligence.get('actual_value')} kWh", f"Expected: {intelligence.get('expected_value')} kWh", f"Deviation: {intelligence.get('deviation_pct')}%", f"Severity: {intelligence.get('severity')}"]
            answer = _answer(f"{facility}: {finding['diagnosis']}", evidence, finding["diagnosis"], recs[0]["recommended_action"] if recs else "Verify the sensor reading and inspect the facility's energy systems.", "PostgreSQL readings analyzed by M3 energy intelligence")
        else:
            answer = _answer("I could not match a facility or retrieve sufficient energy evidence for a diagnosis.", ["Available facility names are required for facility-specific diagnosis."], basis="PostgreSQL energy_readings")
        decision = {"diagnostic_type": "energy", "facility_name": facility, "finding": finding}
    elif route == "air_quality":
        rows = d.get("air_quality", [])
        worst = max(rows, key=lambda r: r.get("aqi") if r.get("aqi") is not None else -1, default=None)
        decision = {"metric": "AQI", "worst_area": worst, "readings": rows}
        answer = _answer(f"{worst['facility_name']} has the highest latest AQI at {worst['aqi']}." if worst else "No air-quality readings are available.", [worst] if worst else [], basis="PostgreSQL air_quality_readings")
    elif route == "traffic":
        rows = d.get("traffic", [])
        order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        worst = max(rows, key=lambda r: (order.get((r.get("congestion_level") or "").upper(), 0), r.get("lane_occupancy_percent") or 0), default=None)
        decision = {"hotspot": worst, "readings": rows}
        answer = _answer(f"{worst['facility_name']} has the highest recorded congestion level ({worst['congestion_level']})." if worst else "No traffic readings are available.", [worst] if worst else [], basis="PostgreSQL traffic_readings")
    elif route == "equipment":
        rows = d.get("equipment", [])
        decision = {"equipment_needing_attention": rows, "total": len(rows), "basis_note": "Uses sensor status/calibration; no dedicated equipment health table is present in the supplied schema."}
        answer = _answer(f"{len(rows)} sensors need attention based on status or calibration due date." if rows else "No sensor status or calibration issues were found.", rows[:10], basis="PostgreSQL sensors and alerts")
    elif route == "safety":
        rows = d.get("safety_alerts", [])
        decision = {"safety_alerts": rows, "total": len(rows), "availability": "No dedicated incident table exists in the supplied schema; only safety-tagged alerts can be reported."}
        answer = _answer(f"Found {len(rows)} safety/incident alerts." if rows else "No safety-tagged alerts are available; the supplied schema has no dedicated safety incident table.", rows[:10], basis="PostgreSQL alerts")
    elif route == "waste":
        rows = d.get("waste", [])
        highest, anomalies = find_highest_waste_producer(rows), find_waste_anomalies(rows)
        decision = {"highest_producer": highest, "anomalies": anomalies, "total_anomalies": len(anomalies), "overflow_risk": "unavailable: no bin fill-level data in supplied schema"}
        answer = _answer(f"{highest['facility_name']} produces the highest latest recorded waste at {highest['waste_quantity_kg']} kg." if highest else "No current waste data is available.", anomalies, basis="PostgreSQL waste_readings")
    elif route == "scenario":
        metric = "water" if "water" in q else "energy"
        decision, basis = _scenario(question, metric, context)
        answer = _answer("Scenario simulation complete." if decision.get("status") == "SIMULATED" else decision.get("message", "Scenario could not be calculated."), [decision], "This is a deterministic what-if calculation, not a forecast.", basis=basis or "PostgreSQL")
    elif route in {"current_status", "action"}:
        decision = build_decision_summary(d.get("alerts", []), d.get("air_quality", []), d.get("traffic", []))
        problems = decision.get("operational_problems", [])
        energy_anomalies = find_energy_anomalies(_latest_m3(d.get("m3_energy", [])))
        for anomaly in energy_anomalies:
            problems.append({"type": "energy_anomaly", "facility_id": anomaly.get("facility_id"),
                "facility_name": anomaly.get("facility_name"), "severity": anomaly.get("severity"),
                "message": f"Energy deviation {anomaly.get('deviation_pct')}%"})
        for metric, rows, finder, problem_type in (
            ("water", d.get("water", []), find_water_anomalies, "water_anomaly"),
            ("waste", d.get("waste", []), find_waste_anomalies, "waste_anomaly"),
        ):
            for anomaly in finder(rows):
                problems.append({"type": problem_type, "facility_id": anomaly.get("facility_id"),
                    "facility_name": anomaly.get("facility_name"), "severity": "HIGH",
                    "message": anomaly.get("anomaly_reason") or f"Recorded {metric} anomaly"})
        recs, explanations = _recommend(problems)
        answer = _answer(f"{len(problems)} operational problems are prioritized in the current status summary.", problems, "Priorities come from current alerts, air quality, and traffic readings.", recs[0]["recommended_action"] if recs else "Continue routine monitoring.", "PostgreSQL alerts, air_quality_readings, traffic_readings")
    elif route == "general":
        decision = {"description": "An industrial intelligence system combines operational data, analytics, rules, and decision support to help industrial facilities monitor resources and act on problems."}
        answer = _answer(decision["description"], basis="General project description")
    else:
        decision = {"message": "I could not determine the requested analysis. Specify energy, water, waste, air quality, traffic, equipment, safety, history, or a what-if scenario."}
        answer = _answer(decision["message"], basis="No database query performed")
    return decision, recs, explanations, answer


def _ollama_explain(question, decision, answer):
    """Optional local explanation; reject numerical claims not present in context."""
    endpoint = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    model = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    relevant_keys = ("comparison_type", "highest_consumer", "highest_producer", "total_anomalies", "severity_counts",
                     "diagnosis", "trend", "period_days", "facility_name", "finding", "worst_area", "hotspot",
                     "equipment_needing_attention", "safety_alerts", "scenario_type", "baseline_value", "simulated_value",
                     "status", "message", "overflow_risk")
    trusted = {"decision": {key: decision[key] for key in relevant_keys if key in decision}, "answer": answer}
    context = json.dumps(trusted, default=str, ensure_ascii=False)
    prompt = ("Write one concise natural-language explanation using only the supplied JSON. "
              "Do not invent data, change values, create facilities, claim unsupported anomalies or predictions. "
              "Do not include digits or numerical measurements in the explanation; the exact figures are already in the structured evidence. "
              "If information is unavailable, say so. Return explanation only.\nQUESTION: " + question + "\nTRUSTED JSON: " + context)
    try:
        response = requests.post(endpoint, json={"model": model, "prompt": prompt, "stream": False, "think": False,
            "options": {"num_predict": 120}}, timeout=float(os.getenv("OLLAMA_TIMEOUT", "60")))
        response.raise_for_status()
        text = response.json().get("response", "").strip()
        if not text:
            return None
        # Guard numerical fidelity: any numeric token in the generated text must occur in trusted context.
        allowed = set(re.findall(r"\d+(?:\.\d+)?%?", context))
        if any(token not in allowed for token in re.findall(r"\d+(?:\.\d+)?%?", text)):
            return None
        return text
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return None


def process_question(question, use_llm=True):
    """Return a stable structured result and deterministic fallback on service errors."""
    route = route_question(question)
    result = {"question": question, "route": route, "context": {"route": route, "data": {}},
              "decision": {}, "recommendations": [], "explanations": [], "answer": {},
              "natural_language_response": None, "errors": []}
    if route in {"invalid", "unknown", "general"}:
        decision, recs, explanations, answer = _build_decision(route, question or "", result["context"])
    else:
        try:
            context = build_context(route, question)
            result["context"] = _context_summary(context)
            decision, recs, explanations, answer = _build_decision(route, question, context)
        except Exception as exc:
            result["errors"].append({"stage": "data_or_decision", "type": type(exc).__name__, "message": str(exc)})
            decision = {"status": "unavailable", "message": "Database or intelligence processing failed; no numerical result is available."}
            recs, explanations = [], []
            answer = _answer(decision["message"], basis="Unavailable")
    result.update({"decision": decision, "recommendations": recs, "explanations": explanations, "answer": answer})
    if use_llm and answer:
        result["natural_language_response"] = _ollama_explain(question, decision, answer)
        if result["natural_language_response"] is None:
            result["errors"].append({"stage": "ollama", "message": "Local Ollama explanation unavailable or failed numeric fidelity checks; deterministic answer retained."})
    return result


if __name__ == "__main__":
    for prompt in ("Which facility has the highest energy consumption?", "Which facilities currently have energy anomalies?", "Which facility has the highest water consumption?", "What are today's biggest problems?"):
        output = process_question(prompt)
        print(json.dumps({"question": prompt, "route": output["route"],
                          "decision_summary": {k: v for k, v in output["decision"].items() if k not in {"anomalies", "readings", "operational_problems", "data_quality_issues"}},
                          "answer": output["answer"], "natural_language_response": output["natural_language_response"],
                          "errors": output["errors"]}, indent=2, default=str))
