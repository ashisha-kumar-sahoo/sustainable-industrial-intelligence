"""Decision-first assistant: PostgreSQL and Python decide; local Qwen explains."""
import json
import os
import re
from collections import Counter, defaultdict
from datetime import date, datetime

import pandas as pd
import requests

from ai.assistant.query_router import route_question
from ai.assistant.context_builder import build_context
from ai.assistant.guardrails import validate_explanation
from ai.assistant.prompts import build_explanation_prompt
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
from ml.waste.overflow_prediction import predict_waste_overflow


def _latest_m3(records):
    latest = {}
    for item in records or []:
        key = item.get("facility_id")
        item_timestamp = str(item.get("timestamp", ""))
        latest_timestamp = str(latest.get(key, {}).get("timestamp", ""))
        if key is not None and (key not in latest or item_timestamp > latest_timestamp):
            latest[key] = item
    return list(latest.values())


def _answer(
    summary,
    evidence=None,
    explanation=None,
    action="Review the evidence and verify the relevant readings.",
    basis="PostgreSQL",
):
    """Create the standard response structure used by all assistant routes."""
    response = create_response(summary, evidence or [], action, basis)
    response["explanation"] = explanation or summary
    return response


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


def _waste_overflow_predictions(rows):
    """Run the waste model when the supplied rows contain bin telemetry."""
    if not rows:
        return []

    telemetry = pd.DataFrame(rows)
    required_columns = {
        "reading_ts",
        "facility_id",
        "fill_level_percent",
        "fill_rate_percent_per_hour",
    }
    if not required_columns.issubset(telemetry.columns):
        return []

    predictions = predict_waste_overflow(telemetry, horizon_hours=6)
    if predictions.empty:
        return []

    return predictions.to_dict(orient="records")


def _scenario(question, metric, context):
    """Calculate a transparent what-if estimate from the latest readings."""
    parsed_question = parse_energy_reduction_question(question)
    facility_match = re.search(
        r"what if\s+(.+?)\s+(?:reduces?|decreases?|lowers?)\b",
        question,
        re.IGNORECASE,
    )

    if parsed_question:
        facility_name = parsed_question.get("facility_name")
    elif facility_match:
        facility_name = facility_match.group(1).strip(" '\\\"?.")
    else:
        facility_name = None

    generic_metric_name = re.fullmatch(
        r"(?:energy|water)(?:\s+(?:consumption|usage|use))?(?:\s+is)?",
        facility_name or "",
        re.IGNORECASE,
    )
    if generic_metric_name:
        facility_name = None

    reduction_match = re.search(
        r"(?:reduce|reduces|decrease|decreases|lower|lowers).*?(\d+(?:\.\d+)?)\s*%",
        question,
        re.IGNORECASE,
    )
    if not reduction_match:
        return {"message": "Specify a reduction percentage to run a simulation."}, ""

    reduction_pct = float(reduction_match.group(1))
    if not 0 < reduction_pct < 100:
        return {
            "message": "The simulated reduction must be greater than 0% and less than 100%."
        }, ""

    data = context.get("data", {})
    if metric == "water":
        water_rows = data.get("water", [])
        if facility_name:
            water_rows = [
                row
                for row in water_rows
                if facility_name.casefold()
                in str(row.get("facility_name", "")).casefold()
            ]

        if not water_rows:
            return {"message": "No current water data is available for this simulation."}, ""

        baseline_row = water_rows[0] if facility_name else None
        if baseline_row:
            baseline_value = baseline_row.get("water_consumption_liters") or 0
            scenario_facility = baseline_row.get("facility_name")
        else:
            baseline_value = sum(
                row.get("water_consumption_liters") or 0 for row in water_rows
            )
            scenario_facility = "All facilities"

        simulated_value = round(
            baseline_value * (1 - reduction_pct / 100),
            2,
        )
        return {
            "scenario_type": "water_reduction",
            "facility_name": scenario_facility,
            "baseline_value": baseline_value,
            "simulated_value": simulated_value,
            "estimated_change_pct": -reduction_pct,
            "unit": "litres",
            "status": "SIMULATED",
            "assumptions": [
                "Applies the requested reduction to the latest water reading; "
                "this is not a forecast."
            ],
        }, "water_readings"

    energy_rows = data.get("energy", [])
    if not facility_name:
        if not energy_rows:
            return {"message": "No current energy data is available for this simulation."}, ""

        baseline = {
            "facility_id": None,
            "facility_name": "All facilities",
            "energy_consumption_kwh": sum(
                row.get("energy_consumption_kwh") or 0 for row in energy_rows
            ),
        }
    else:
        baseline = next(
            (
                row
                for row in energy_rows
                if facility_name.casefold()
                in str(row.get("facility_name", "")).casefold()
            ),
            None,
        )
        if baseline is None:
            baseline = get_facility_energy_baseline(facility_name)

    if not baseline:
        return {"message": f"No latest energy data found for {facility_name}."}, "energy_readings"

    scenario = simulate_energy_reduction(
        baseline["facility_id"],
        baseline["facility_name"],
        baseline["energy_consumption_kwh"],
        reduction_pct,
    )
    return scenario, "energy_readings"


def _build_decision(route, question, context):
    """Build a deterministic decision and answer from retrieved database data."""
    data = context.get("data", {})
    normalized_question = question.casefold()
    recommendations = []
    explanations = []

    if route in {"energy", "comparison", "energy_anomaly", "water"}:
        metric = (
            "water"
            if "water" in normalized_question
            else "waste"
            if "waste" in normalized_question
            else "energy"
        )
        rows = data.get(metric, [])

        if metric == "energy":
            # Use the same M3 snapshot for both comparisons and anomaly answers.
            anomalies = find_energy_anomalies(
                _latest_m3(data.get("m3_energy", []))
            )
            highest_consumer = find_highest_energy_consumer(rows)
            problems = [
                {
                    "type": "energy_anomaly",
                    "facility_id": anomaly["facility_id"],
                    "facility_name": anomaly["facility_name"],
                    "actual_value": anomaly["actual_value"],
                    "expected_value": anomaly["expected_value"],
                    "deviation_pct": anomaly["deviation_pct"],
                    "severity": anomaly.get("severity"),
                    "message": f"Energy deviation {anomaly.get('deviation_pct')}%",
                }
                for anomaly in anomalies
            ]
            recommendations, explanations = _recommend(problems)

            if route == "energy_anomaly":
                severity_counts = Counter(
                    (anomaly.get("severity") or "UNCLASSIFIED").upper()
                    for anomaly in anomalies
                )
                decision = {
                    "comparison_type": "energy_anomaly",
                    "anomalies": anomalies,
                    "total_anomalies": len(anomalies),
                    "severity_counts": dict(severity_counts),
                    "m3_error": data.get("m3_energy_error"),
                }
                answer = create_energy_anomaly_response(
                    anomalies,
                    recommendations,
                )
                answer["explanation"] = (
                    "Severity totals are counted from the same anomaly records "
                    "shown in evidence."
                )
            else:
                decision = {
                    "comparison_type": "energy",
                    "highest_consumer": highest_consumer,
                    "anomalies": anomalies,
                    "total_anomalies": len(anomalies),
                }
                if highest_consumer:
                    answer = _answer(
                        f"{highest_consumer['facility_name']} has the highest latest "
                        f"energy use at {highest_consumer['energy_consumption_kwh']} kWh.",
                        [
                            f"Latest reading: {highest_consumer['reading_ts']}",
                            f"Detected energy anomalies: {len(anomalies)}",
                        ],
                        "Energy usage ranking is based on the latest PostgreSQL "
                        "reading per facility.",
                        "Inspect the highest-consuming facility and review any "
                        "listed anomaly.",
                        "PostgreSQL energy_readings; M3 energy intelligence",
                    )
                else:
                    answer = _answer(
                        "No current energy data is available.",
                        basis="PostgreSQL energy_readings",
                    )
        else:
            highest, anomalies, value_key, unit, table_name = _resource_answer(
                metric,
                rows,
            )
            problems = [
                {
                    "type": f"{metric}_anomaly",
                    "facility_name": anomaly.get("facility_name"),
                    "facility_id": anomaly.get("facility_id"),
                    "severity": "HIGH",
                    "message": anomaly.get("anomaly_reason")
                    or f"Recorded {metric} anomaly",
                }
                for anomaly in anomalies
            ]
            recommendations, explanations = _recommend(problems)
            result_key = "highest_consumer" if metric == "water" else "highest_producer"
            decision = {
                "comparison_type": metric,
                result_key: highest,
                "anomalies": anomalies,
                "total_anomalies": len(anomalies),
            }
            if highest:
                summary = (
                    f"{highest['facility_name']} has the highest latest {metric} "
                    f"value at {highest[value_key]} {unit}."
                )
                evidence = [f"Recorded anomalies: {len(anomalies)}"]
            else:
                summary = f"No current {metric} data is available."
                evidence = []

            answer = _answer(
                summary,
                evidence,
                "Comparison uses the latest reading per facility.",
                f"Review the {metric} reading and investigate any recorded anomalies.",
                f"PostgreSQL {table_name}",
            )

    elif route == "historical":
        metric = data.get("historical_metric", "energy")
        history = data.get("history", [])
        daily_totals = defaultdict(float)

        for row in history:
            timestamp = row.get("reading_ts")
            value = row.get("value")
            if timestamp is None or value is None:
                continue
            day = timestamp.date() if hasattr(timestamp, "date") else str(timestamp)[:10]
            daily_totals[day] += value

        daily = [
            {"date": day, "total": round(total, 2)}
            for day, total in sorted(daily_totals.items())
        ]
        valid_readings = [row for row in history if row.get("value") is not None]
        highest_reading = max(
            valid_readings,
            key=lambda row: row["value"],
            default=None,
        )
        lowest_reading = min(
            valid_readings,
            key=lambda row: row["value"],
            default=None,
        )

        trend = "insufficient data"
        if len(daily) >= 2:
            first_total = daily[0]["total"]
            last_total = daily[-1]["total"]
            if last_total > first_total:
                trend = "increased"
            elif last_total < first_total:
                trend = "decreased"
            else:
                trend = "was unchanged"

        decision = {
            "data_type": metric,
            "period_days": 7,
            "total_readings": len(history),
            "daily_totals": daily,
            "highest_reading": highest_reading,
            "lowest_reading": lowest_reading,
            "trend": trend,
        }
        summary = (
            f"{metric.title()} {trend} across the 7-day period based on "
            f"{len(history)} readings."
            if history
            else f"No {metric} readings are available for the requested period."
        )
        answer = _answer(
            summary,
            [f"Days with readings: {len(daily)}", f"Daily totals: {daily}"],
            "Trend compares the first and last daily totals.",
            "Use this trend as historical analysis, not a forecast.",
            f"PostgreSQL {metric}_readings",
        )

    elif route == "diagnostic":
        energy_rows = data.get("energy", [])
        m3_rows = _latest_m3(data.get("m3_energy", []))
        matching_facilities = [
            row.get("facility_name")
            for row in energy_rows
            if row.get("facility_name")
            and row["facility_name"].casefold() in normalized_question
        ]
        facility_name = matching_facilities[0] if matching_facilities else None
        reading = next(
            (
                row
                for row in energy_rows
                if row.get("facility_name") == facility_name
            ),
            None,
        )
        intelligence = next(
            (
                row
                for row in m3_rows
                if row.get("facility_id") == (reading or {}).get("facility_id")
            ),
            None,
        )
        finding = {
            "facility_name": facility_name,
            "latest_reading": reading,
            "energy_intelligence": intelligence,
        }

        if reading and intelligence:
            if intelligence.get("anomaly"):
                diagnosis = (
                    "M3 flags a deviation from the preceding reading for this "
                    "facility/sensor."
                )
            else:
                diagnosis = (
                    "M3 does not flag this latest reading as anomalous against "
                    "its preceding facility/sensor reading."
                )
            finding["diagnosis"] = diagnosis

            if intelligence.get("anomaly"):
                problems = [
                    {
                        "type": "energy_anomaly",
                        "facility_name": facility_name,
                        "facility_id": reading["facility_id"],
                        "actual_value": intelligence.get("actual_value"),
                        "expected_value": intelligence.get("expected_value"),
                        "deviation_pct": intelligence.get("deviation_pct"),
                        "severity": intelligence.get("severity"),
                        "message": diagnosis,
                    }
                ]
            else:
                problems = []

            recommendations, explanations = _recommend(problems)
            evidence = [
                f"Actual: {intelligence.get('actual_value')} kWh",
                f"Expected: {intelligence.get('expected_value')} kWh",
                f"Deviation: {intelligence.get('deviation_pct')}%",
                f"Severity: {intelligence.get('severity')}",
            ]
            recommended_action = (
                recommendations[0]["recommended_action"]
                if recommendations
                else "Verify the sensor reading and inspect the facility's energy systems."
            )
            answer = _answer(
                f"{facility_name}: {diagnosis}",
                evidence,
                diagnosis,
                recommended_action,
                "PostgreSQL readings analyzed by M3 energy intelligence",
            )
        else:
            answer = _answer(
                "I could not match a facility or retrieve sufficient energy evidence "
                "for a diagnosis.",
                ["Available facility names are required for facility-specific diagnosis."],
                basis="PostgreSQL energy_readings",
            )

        decision = {
            "diagnostic_type": "energy",
            "facility_name": facility_name,
            "finding": finding,
        }

    elif route == "air_quality":
        rows = data.get("air_quality", [])
        worst_reading = max(
            rows,
            key=lambda row: row.get("aqi") if row.get("aqi") is not None else -1,
            default=None,
        )
        decision = {"metric": "AQI", "worst_area": worst_reading, "readings": rows}
        if worst_reading:
            summary = (
                f"{worst_reading['facility_name']} has the highest latest AQI "
                f"at {worst_reading['aqi']}."
            )
            evidence = [worst_reading]
        else:
            summary = "No air-quality readings are available."
            evidence = []
        answer = _answer(
            summary,
            evidence,
            basis="PostgreSQL air_quality_readings",
        )

    elif route == "traffic":
        rows = data.get("traffic", [])
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        worst_reading = max(
            rows,
            key=lambda row: (
                severity_order.get((row.get("congestion_level") or "").upper(), 0),
                row.get("lane_occupancy_percent") or 0,
            ),
            default=None,
        )
        decision = {"hotspot": worst_reading, "readings": rows}
        if worst_reading:
            summary = (
                f"{worst_reading['facility_name']} has the highest recorded "
                f"congestion level ({worst_reading['congestion_level']})."
            )
            evidence = [worst_reading]
        else:
            summary = "No traffic readings are available."
            evidence = []
        answer = _answer(
            summary,
            evidence,
            basis="PostgreSQL traffic_readings",
        )

    elif route == "equipment":
        rows = data.get("equipment", [])
        decision = {
            "equipment_needing_attention": rows,
            "total": len(rows),
            "basis_note": (
                "Latest readings from public.equipment_readings; attention is "
                "flagged by status, high temperature, vibration, or utilization."
            ),
        }
        summary = (
            f"{len(rows)} equipment units need attention based on their latest telemetry."
            if rows
            else "No equipment units crossed the configured status or telemetry attention rules."
        )
        answer = _answer(
            summary,
            rows[:10],
            basis="PostgreSQL equipment_readings",
        )

    elif route == "safety":
        rows = data.get("safety_readings", [])
        critical_rows = [
            row for row in rows
            if row.get("fire_alarm") or row.get("emergency_button")
        ]
        high_rows = [
            row for row in rows
            if row.get("severity") in {"High", "Critical"}
        ]
        has_synthetic_context = any(
            row.get("synthetic_incident_context") for row in rows
        )
        data_note = (
            "Some incident labels and response times are synthetic examples, not "
            "real incident records or measured emergency response data."
            if has_synthetic_context
            else "Incident labels and response times are read from the stored safety records."
        )
        decision = {
            "safety_readings": rows,
            "latest_sensor_count": len(rows),
            "high_or_critical_count": len(high_rows),
            "fire_or_emergency_count": len(critical_rows),
            "data_note": data_note,
        }
        summary = (
            f"Latest safety telemetry covers {len(rows)} sensors; "
            f"{len(high_rows)} readings are labelled high/critical and "
            f"{len(critical_rows)} show a fire/emergency signal."
        )
        answer = _answer(
            summary,
            rows[:10],
            explanation=data_note,
            basis="PostgreSQL safety_readings (synthetic context where marked)",
        )

    elif route == "waste":
        rows = data.get("waste", [])
        highest_producer = find_highest_waste_producer(rows)
        anomalies = find_waste_anomalies(rows)
        overflow_predictions = _waste_overflow_predictions(rows)
        high_risk_bins = [
            prediction
            for prediction in overflow_predictions
            if prediction.get("overflow_risk") == "HIGH"
        ]
        medium_risk_bins = [
            prediction
            for prediction in overflow_predictions
            if prediction.get("overflow_risk") == "MEDIUM"
        ]
        if overflow_predictions:
            overflow_summary = {
                "status": "available",
                "horizon_hours": 6,
                "prediction_method": overflow_predictions[0].get("prediction_method"),
                "high_risk_bins": len(high_risk_bins),
                "medium_risk_bins": len(medium_risk_bins),
                "top_predictions": sorted(
                    overflow_predictions,
                    key=lambda item: item.get("predicted_fill_level_percent", 0),
                    reverse=True,
                )[:5],
                "probability_note": (
                    "overflow_probability is a normalized fill-risk score, "
                    "not a calibrated probability."
                ),
            }
        else:
            overflow_summary = {
                "status": "unavailable",
                "message": (
                    "Waste quantity data is available, but usable fill-level and "
                    "fill-rate telemetry is not available for overflow prediction."
                ),
            }

        decision = {
            "highest_producer": highest_producer,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "overflow_risk": overflow_summary,
        }
        if highest_producer:
            summary = (
                f"{highest_producer['facility_name']} produces the highest latest "
                f"recorded waste at {highest_producer['waste_quantity_kg']} kg."
            )
        else:
            summary = "No current waste data is available."
        if overflow_predictions:
            summary += (
                f" The six-hour model identified {len(high_risk_bins)} high-risk "
                f"and {len(medium_risk_bins)} medium-risk bin readings."
            )
        elif rows:
            summary += " Bin overflow risk is unavailable without valid fill telemetry."

        answer = _answer(
            summary,
            [*anomalies, *overflow_summary.get("top_predictions", [])],
            explanation=(
                "Overflow risk is estimated from fill level and fill rate. "
                "The score is not a calibrated probability."
                if overflow_predictions
                else None
            ),
            basis="PostgreSQL waste_readings and six-hour overflow estimator",
        )

    elif route == "scenario":
        metric = "water" if "water" in normalized_question else "energy"
        decision, basis = _scenario(question, metric, context)
        summary = (
            "Scenario simulation complete."
            if decision.get("status") == "SIMULATED"
            else decision.get("message", "Scenario could not be calculated.")
        )
        answer = _answer(
            summary,
            [decision],
            "This is a deterministic what-if calculation, not a forecast.",
            basis=basis or "PostgreSQL",
        )

    elif route in {"current_status", "action"}:
        decision = build_decision_summary(
            data.get("alerts", []),
            data.get("air_quality", []),
            data.get("traffic", []),
        )
        problems = decision.get("operational_problems", [])
        energy_anomalies = find_energy_anomalies(
            _latest_m3(data.get("m3_energy", []))
        )

        for anomaly in energy_anomalies:
            problems.append(
                {
                    "type": "energy_anomaly",
                    "facility_id": anomaly.get("facility_id"),
                    "facility_name": anomaly.get("facility_name"),
                    "severity": anomaly.get("severity"),
                    "message": f"Energy deviation {anomaly.get('deviation_pct')}%",
                }
            )

        resource_anomaly_finders = (
            ("water", data.get("water", []), find_water_anomalies, "water_anomaly"),
            ("waste", data.get("waste", []), find_waste_anomalies, "waste_anomaly"),
        )
        for metric, rows, finder, problem_type in resource_anomaly_finders:
            for anomaly in finder(rows):
                problems.append(
                    {
                        "type": problem_type,
                        "facility_id": anomaly.get("facility_id"),
                        "facility_name": anomaly.get("facility_name"),
                        "severity": "HIGH",
                        "message": anomaly.get("anomaly_reason")
                        or f"Recorded {metric} anomaly",
                    }
                )

        recommendations, explanations = _recommend(problems)
        next_action = (
            recommendations[0]["recommended_action"]
            if recommendations
            else "Continue routine monitoring."
        )
        answer = _answer(
            f"{len(problems)} operational problems are prioritized in the current status summary.",
            problems,
            "Priorities come from current alerts, air quality, and traffic readings.",
            next_action,
            "PostgreSQL alerts, air_quality_readings, traffic_readings",
        )

    elif route == "general":
        description = (
            "An industrial intelligence system combines operational data, analytics, "
            "rules, and decision support to help industrial facilities monitor "
            "resources and act on problems."
        )
        decision = {"description": description}
        answer = _answer(description, basis="General project description")

    else:
        message = (
            "I could not determine the requested analysis. Specify energy, water, "
            "waste, air quality, traffic, equipment, safety, history, or a what-if scenario."
        )
        decision = {"message": message}
        answer = _answer(message, basis="No database query performed")

    return decision, recommendations, explanations, answer


def _ollama_explain(question, decision, answer):
    """Ask the local LLM to explain trusted results without inventing figures."""
    endpoint = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    model = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    relevant_keys = (
        "comparison_type",
        "highest_consumer",
        "highest_producer",
        "total_anomalies",
        "severity_counts",
        "diagnosis",
        "trend",
        "period_days",
        "facility_name",
        "finding",
        "worst_area",
        "hotspot",
        "equipment_needing_attention",
        "safety_alerts",
        "safety_readings",
        "high_or_critical_count",
        "fire_or_emergency_count",
        "scenario_type",
        "baseline_value",
        "simulated_value",
        "status",
        "message",
        "overflow_risk",
    )
    trusted_context = {
        "decision": {
            key: decision[key]
            for key in relevant_keys
            if key in decision
        },
        "answer": answer,
    }
    prompt = build_explanation_prompt(question, trusted_context)
    serialized_context = json.dumps(
        trusted_context,
        default=str,
        ensure_ascii=False,
    )

    try:
        response = requests.post(
            endpoint,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {"num_predict": 120},
            },
            timeout=float(os.getenv("OLLAMA_TIMEOUT", "120")),
        )
        response.raise_for_status()
        generated_text = response.json().get("response", "")
        return validate_explanation(generated_text, serialized_context)
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return None


def process_question(question, use_llm=True):
    """Return a structured decision, retaining a deterministic fallback."""
    route = route_question(question)
    result = {
        "question": question,
        "route": route,
        "context": {"route": route, "data": {}},
        "decision": {},
        "recommendations": [],
        "explanations": [],
        "answer": {},
        "natural_language_response": None,
        "errors": [],
    }

    if route in {"invalid", "unknown", "general"}:
        decision, recommendations, explanations, answer = _build_decision(
            route,
            question or "",
            result["context"],
        )
    else:
        try:
            context = build_context(route, question)
            result["context"] = _context_summary(context)
            decision, recommendations, explanations, answer = _build_decision(
                route,
                question,
                context,
            )
        except Exception as exc:
            result["errors"].append(
                {
                    "stage": "data_or_decision",
                    "type": type(exc).__name__,
                    "message": str(exc),
                }
            )
            decision = {
                "status": "unavailable",
                "message": (
                    "Database or intelligence processing failed; "
                    "no numerical result is available."
                ),
            }
            recommendations = []
            explanations = []
            answer = _answer(decision["message"], basis="Unavailable")

    result.update(
        {
            "decision": decision,
            "recommendations": recommendations,
            "explanations": explanations,
            "answer": answer,
        }
    )

    if use_llm and answer:
        result["natural_language_response"] = _ollama_explain(
            question,
            decision,
            answer,
        )
        if result["natural_language_response"] is None:
            result["errors"].append(
                {
                    "stage": "ollama",
                    "message": (
                        "Local Ollama explanation unavailable or failed numeric "
                        "fidelity checks; deterministic answer retained."
                    ),
                }
            )

    return result


if __name__ == "__main__":
    example_questions = (
        "Which facility has the highest energy consumption?",
        "Which facilities currently have energy anomalies?",
        "Which facility has the highest water consumption?",
        "What are today's biggest problems?",
    )
    hidden_decision_fields = {
        "anomalies",
        "readings",
        "operational_problems",
        "data_quality_issues",
    }

    for example_question in example_questions:
        output = process_question(example_question)
        decision_summary = {
            key: value
            for key, value in output["decision"].items()
            if key not in hidden_decision_fields
        }
        printable_output = {
            "question": example_question,
            "route": output["route"],
            "decision_summary": decision_summary,
            "answer": output["answer"],
            "natural_language_response": output["natural_language_response"],
            "errors": output["errors"],
        }
        print(json.dumps(printable_output, indent=2, default=str))
