def find_highest_energy_consumer(energy_data):
    """
    Find the facility with the highest current energy consumption.
    """

    if not energy_data:
        return None

    highest = max(
        energy_data,
        key=lambda item: item["energy_consumption_kwh"]
    )

    return {
        "facility_id": highest["facility_id"],
        "facility_name": highest["facility_name"],
        "energy_consumption_kwh": highest["energy_consumption_kwh"],
        "reading_ts": highest["reading_ts"]
    }


def find_energy_anomalies(energy_data):
    """
    Find facilities where M3 has detected
    an energy anomaly.
    """

    anomalies = []

    for item in energy_data:
        if item.get("anomaly") is True:
            anomalies.append({
                "facility_id": item.get("facility_id"),
                "facility_name": item.get("facility_name"),
                "actual_value": item.get("actual_value"),
                "expected_value": item.get("expected_value"),
                "deviation_pct": item.get("deviation_pct"),
                "forecast_energy_kwh": item.get(
                    "forecast_energy_kwh"
                ),
                "severity": item.get("severity"),
                "anomaly": item.get("anomaly"),
                "timestamp": item.get("timestamp")
            })

    return anomalies

def find_highest_water_consumer(water_data):
    """
    Find the facility with the highest latest water consumption.
    """

    if not water_data:
        return None

    highest = max(
        water_data,
        key=lambda item: item["water_consumption_liters"]
    )

    return {
        "facility_id": highest["facility_id"],
        "facility_name": highest["facility_name"],
        "water_consumption_liters": highest["water_consumption_liters"],
        "reading_ts": highest["reading_ts"]
    }


def find_water_anomalies(water_data):
    """
    Find facilities where the latest water reading
    is marked as an anomaly.
    """

    anomalies = []

    for item in water_data:
        if item["anomaly_flag"]:
            anomalies.append({
                "facility_id": item["facility_id"],
                "facility_name": item["facility_name"],
                "water_consumption_liters": item["water_consumption_liters"],
                "anomaly_reason": item["anomaly_reason"],
                "reading_ts": item["reading_ts"]
            })

    return anomalies


def find_highest_waste_producer(waste_data):
    """
    Find the facility with the highest latest waste quantity.
    """

    if not waste_data:
        return None

    highest = max(
        waste_data,
        key=lambda item: item["waste_quantity_kg"]
    )

    return {
        "facility_id": highest["facility_id"],
        "facility_name": highest["facility_name"],
        "waste_quantity_kg": highest["waste_quantity_kg"],
        "waste_type": highest["waste_type"],
        "reading_ts": highest["reading_ts"]
    }


def find_waste_anomalies(waste_data):
    """
    Find facilities where the latest waste reading
    is marked as an anomaly.
    """

    anomalies = []

    for item in waste_data:
        if item["anomaly_flag"]:
            anomalies.append({
                "facility_id": item["facility_id"],
                "facility_name": item["facility_name"],
                "waste_quantity_kg": item["waste_quantity_kg"],
                "waste_type": item["waste_type"],
                "anomaly_reason": item["anomaly_reason"],
                "reading_ts": item["reading_ts"]
            })

    return anomalies


def find_air_quality_issues(air_quality_data):
    """
    Find facilities with concerning AQI conditions.

    The database already provides the AQI category,
    so this rule uses that category rather than
    inventing a new threshold.
    """

    issues = []

    for item in air_quality_data:
        category = item["aqi_category"]

        if category and category.lower() != "good":
            issues.append({
                "facility_id": item["facility_id"],
                "facility_name": item["facility_name"],
                "aqi": item["aqi"],
                "aqi_category": category,
                "reading_ts": item["reading_ts"]
            })

    return issues


def find_traffic_issues(traffic_data):
    """
    Find facilities where traffic congestion
    is not LOW.
    """

    issues = []

    for item in traffic_data:
        congestion = item["congestion_level"]

        if congestion and congestion.upper() != "LOW":
            issues.append({
                "facility_id": item["facility_id"],
                "facility_name": item["facility_name"],
                "vehicle_count": item["vehicle_count"],
                "average_speed_kmph": item["average_speed_kmph"],
                "congestion_level": congestion,
                "lane_occupancy_percent": item["lane_occupancy_percent"],
                "reading_ts": item["reading_ts"]
            })

    return issues


def find_high_priority_alerts(alerts):
    """
    Return alerts marked as HIGH or CRITICAL.
    """

    high_priority = []

    for alert in alerts:
        severity = alert["severity"]

        if severity and severity.upper() in ["HIGH", "CRITICAL"]:
            high_priority.append(alert)

    return high_priority

def diagnose_energy_facility(energy_data, facility_name):
    """
    Find the latest energy record for a facility
    and return its anomaly information.
    """

    for record in energy_data:

        if record.get("facility_name") == facility_name:

            return {
                "facility_id": record.get("facility_id"),
                "facility_name": record.get("facility_name"),
                "reading_ts": record.get("reading_ts"),
                "energy_consumption_kwh": record.get(
                    "energy_consumption_kwh"
                ),
                "peak_demand_kw": record.get(
                    "peak_demand_kw"
                ),
                "anomaly_flag": record.get(
                    "anomaly_flag"
                ),
                "anomaly_reason": record.get(
                    "anomaly_reason"
                )
            }

    return None

if __name__ == "__main__":

    # -------------------------
    # 1. Energy test
    # -------------------------

    energy_data = [
        {
            "facility_id": 1,
            "facility_name": "Factory A",
            "energy_consumption_kwh": 1500,
            "anomaly_flag": False,
            "anomaly_reason": None,
            "reading_ts": "2026-09-30 23:00"
        },
        {
            "facility_id": 2,
            "facility_name": "Factory B",
            "energy_consumption_kwh": 2200,
            "anomaly_flag": True,
            "anomaly_reason": "High energy consumption",
            "reading_ts": "2026-09-30 23:00"
        },
        {
            "facility_id": 3,
            "facility_name": "Factory C",
            "energy_consumption_kwh": 1800,
            "anomaly_flag": False,
            "anomaly_reason": None,
            "reading_ts": "2026-09-30 23:00"
        }
    ]

    print("\n1. Highest Energy Consumer")
    print(find_highest_energy_consumer(energy_data))

    print("\n2. Energy Anomalies")
    print(find_energy_anomalies(energy_data))


    # -------------------------
    # 2. Water test
    # -------------------------

    water_data = [
        {
            "facility_id": 1,
            "facility_name": "Factory A",
            "water_consumption_liters": 12000,
            "anomaly_flag": False,
            "anomaly_reason": None,
            "reading_ts": "2026-09-30 23:00"
        },
        {
            "facility_id": 2,
            "facility_name": "Factory B",
            "water_consumption_liters": 18500,
            "anomaly_flag": True,
            "anomaly_reason": "Abnormal water usage",
            "reading_ts": "2026-09-30 23:00"
        },
        {
            "facility_id": 3,
            "facility_name": "Factory C",
            "water_consumption_liters": 15000,
            "anomaly_flag": False,
            "anomaly_reason": None,
            "reading_ts": "2026-09-30 23:00"
        }
    ]

    print("\n3. Highest Water Consumer")
    print(find_highest_water_consumer(water_data))

    print("\n4. Water Anomalies")
    print(find_water_anomalies(water_data))


    # -------------------------
    # 3. Waste test
    # -------------------------

    waste_data = [
        {
            "facility_id": 1,
            "facility_name": "Factory A",
            "waste_quantity_kg": 500,
            "waste_type": "GENERAL",
            "anomaly_flag": False,
            "anomaly_reason": None,
            "reading_ts": "2026-09-30 23:00"
        },
        {
            "facility_id": 2,
            "facility_name": "Factory B",
            "waste_quantity_kg": 900,
            "waste_type": "HAZARDOUS",
            "anomaly_flag": True,
            "anomaly_reason": "Unusual waste generation",
            "reading_ts": "2026-09-30 23:00"
        },
        {
            "facility_id": 3,
            "facility_name": "Factory C",
            "waste_quantity_kg": 700,
            "waste_type": "GENERAL",
            "anomaly_flag": False,
            "anomaly_reason": None,
            "reading_ts": "2026-09-30 23:00"
        }
    ]

    print("\n5. Highest Waste Producer")
    print(find_highest_waste_producer(waste_data))

    print("\n6. Waste Anomalies")
    print(find_waste_anomalies(waste_data))


    # -------------------------
    # 4. Air quality test
    # -------------------------

    air_quality_data = [
        {
            "facility_id": 1,
            "facility_name": "Factory A",
            "aqi": 45,
            "aqi_category": "Good",
            "reading_ts": "2026-09-30 23:00"
        },
        {
            "facility_id": 2,
            "facility_name": "Factory B",
            "aqi": 139,
            "aqi_category": "Unhealthy for Sensitive Groups",
            "reading_ts": "2026-09-30 23:00"
        },
        {
            "facility_id": 3,
            "facility_name": "Factory C",
            "aqi": 99,
            "aqi_category": "Moderate",
            "reading_ts": "2026-09-30 23:00"
        }
    ]

    print("\n7. Air Quality Issues")
    print(find_air_quality_issues(air_quality_data))


    # -------------------------
    # 5. Traffic test
    # -------------------------

    traffic_data = [
        {
            "facility_id": 1,
            "facility_name": "Factory A",
            "vehicle_count": 100,
            "average_speed_kmph": 45,
            "congestion_level": "LOW",
            "lane_occupancy_percent": 30,
            "reading_ts": "2026-09-30 23:00"
        },
        {
            "facility_id": 2,
            "facility_name": "Factory B",
            "vehicle_count": 500,
            "average_speed_kmph": 18,
            "congestion_level": "HIGH",
            "lane_occupancy_percent": 85,
            "reading_ts": "2026-09-30 23:00"
        }
    ]

    print("\n8. Traffic Issues")
    print(find_traffic_issues(traffic_data))


    # -------------------------
    # 6. Alert test
    # -------------------------

    alerts = [
        {
            "alert_id": 1,
            "facility_id": 1,
            "facility_name": "Factory A",
            "severity": "LOW",
            "message": "Minor issue"
        },
        {
            "alert_id": 2,
            "facility_id": 2,
            "facility_name": "Factory B",
            "severity": "HIGH",
            "message": "High energy consumption"
        },
        {
            "alert_id": 3,
            "facility_id": 3,
            "facility_name": "Factory C",
            "severity": "CRITICAL",
            "message": "Critical equipment issue"
        }
    ]

    print("\n9. High Priority Alerts")
    print(find_high_priority_alerts(alerts))

    # -------------------------
    # 7. Energy diagnostic test
    # -------------------------

    print("\n10. Energy Diagnostic")

    diagnostic = diagnose_energy_facility(
        energy_data,
        "Factory B"
    )

    print(diagnostic)