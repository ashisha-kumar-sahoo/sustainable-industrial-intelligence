from ai.db import get_connection
from ml.energy.data_loader import load_data
from ml.energy.predict import run_energy_intelligence, create_energy_output


def get_resource_history(metric, days=7):
    """Fetch real readings for an allow-listed resource and period."""
    columns = {
        "energy": ("energy_readings", "energy_consumption_kwh"),
        "water": ("water_readings", "water_consumption_liters"),
        "waste": ("waste_readings", "waste_quantity_kg"),
    }
    if metric not in columns:
        raise ValueError("Unsupported history metric")
    table, value_column = columns[metric]
    days = max(1, min(int(days), 365))
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT r.facility_id, f.facility_name, r.reading_ts,
                       r.{value_column}, r.anomaly_flag
                FROM {table} r JOIN facilities f USING (facility_id)
                WHERE r.reading_ts >= NOW() - (%s * INTERVAL '1 day')
                ORDER BY r.reading_ts ASC
            """, (days,))
            return [{"facility_id": row[0], "facility_name": row[1],
                     "reading_ts": row[2], "value": float(row[3]) if row[3] is not None else None,
                     "anomaly_flag": row[4]} for row in cursor.fetchall()]
    finally:
        conn.close()


def get_equipment_health():
    """Use existing sensor health and alerts; no synthetic equipment table."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.sensor_id, s.sensor_name, s.sensor_type, s.status,
                       s.calibration_due_date, f.facility_id, f.facility_name
                FROM sensors s JOIN facilities f USING (facility_id)
                WHERE UPPER(COALESCE(s.status, '')) <> 'ACTIVE'
                   OR s.calibration_due_date <= CURRENT_DATE
                ORDER BY s.calibration_due_date NULLS LAST, f.facility_name
            """)
            return [{"sensor_id": r[0], "equipment_name": r[1], "equipment_type": r[2],
                     "status": r[3], "calibration_due_date": r[4], "facility_id": r[5],
                     "facility_name": r[6]} for r in cursor.fetchall()]
    finally:
        conn.close()


def get_facilities():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT facility_id, facility_name
            FROM facilities
            ORDER BY facility_id;
        """)

        rows = cursor.fetchall()

        facilities = []

        for row in rows:
            facilities.append({
                "facility_id": row[0],
                "facility_name": row[1]
            })

        return facilities

    finally:
        cursor.close()
        conn.close()


def get_latest_energy_data():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                e.facility_id,
                f.facility_name,
                e.reading_ts,
                e.energy_consumption_kwh,
                e.peak_demand_kw,
                e.anomaly_flag,
                e.anomaly_reason
            FROM energy_readings e
            JOIN facilities f
                ON e.facility_id = f.facility_id
            WHERE e.reading_ts = (
                SELECT MAX(e2.reading_ts)
                FROM energy_readings e2
                WHERE e2.facility_id = e.facility_id
            )
            ORDER BY e.facility_id;
        """)

        rows = cursor.fetchall()

        energy_data = []

        for row in rows:
            energy_data.append({
                "facility_id": row[0],
                "facility_name": row[1],
                "reading_ts": row[2],
                "energy_consumption_kwh": float(row[3]),
                "peak_demand_kw": float(row[4]),
                "anomaly_flag": row[5],
                "anomaly_reason": row[6]
            })

        return energy_data

    finally:
        cursor.close()
        conn.close()

def get_m3_energy_intelligence():
    """
    Run M3 energy intelligence and attach
    facility names from PostgreSQL.
    """

    data = load_data()

    result = run_energy_intelligence(data)

    output = create_energy_output(result)

    facilities = get_facilities()

    facility_names = {
        facility["facility_id"]: facility["facility_name"]
        for facility in facilities
    }

    for record in output:
        facility_id = record.get("facility_id")

        record["facility_name"] = facility_names.get(
            facility_id
        )

    return output

def get_facility_energy_baseline(facility_name):
    """
    Find the latest energy reading for a specific facility.
    """

    energy_data = get_latest_energy_data()

    for record in energy_data:
        if record["facility_name"].lower() == facility_name.lower():
            return record

    return None

def get_latest_water_data():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                w.facility_id,
                f.facility_name,
                w.reading_ts,
                w.water_consumption_liters,
                w.flow_rate,
                w.anomaly_flag,
                w.anomaly_reason
            FROM water_readings w
            JOIN facilities f
                ON w.facility_id = f.facility_id
            WHERE w.reading_ts = (
                SELECT MAX(w2.reading_ts)
                FROM water_readings w2
                WHERE w2.facility_id = w.facility_id
            )
            ORDER BY w.facility_id;
        """)

        rows = cursor.fetchall()

        water_data = []

        for row in rows:
            water_data.append({
                "facility_id": row[0],
                "facility_name": row[1],
                "reading_ts": row[2],
                "water_consumption_liters": float(row[3]),
                "flow_rate": float(row[4]),
                "anomaly_flag": row[5],
                "anomaly_reason": row[6]
            })

        return water_data

    finally:
        cursor.close()
        conn.close()

def get_water_history(days=7):
    """
    Retrieve water consumption readings
    for the requested number of previous days.
    """

    query = """
        SELECT
            wr.facility_id,
            f.facility_name,
            wr.reading_ts,
            wr.water_consumption_liters,
            wr.flow_rate,
            wr.anomaly_flag,
            wr.anomaly_reason
        FROM water_readings AS wr
        JOIN facilities AS f
            ON f.facility_id = wr.facility_id
        WHERE wr.reading_ts >= NOW() - INTERVAL %s
        ORDER BY wr.reading_ts DESC;
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            query,
            (f"{days} days",)
        )

        rows = cursor.fetchall()

        results = []

        for row in rows:

            results.append({
                "facility_id": row[0],
                "facility_name": row[1],
                "reading_ts": row[2],
                "water_consumption_liters": (
                    float(row[3])
                    if row[3] is not None
                    else None
                ),
                "flow_rate": (
                    float(row[4])
                    if row[4] is not None
                    else None
                ),
                "anomaly_flag": row[5],
                "anomaly_reason": row[6]
            })

        cursor.close()

        return results

    finally:
        connection.close()

def summarize_water_by_day(water_history):
    """
    Calculate total water consumption for each day.
    """

    daily_totals = {}

    for record in water_history:

        reading_ts = record.get("reading_ts")
        water_value = record.get(
            "water_consumption_liters"
        )

        if reading_ts is None or water_value is None:
            continue

        date = reading_ts.date()

        if date not in daily_totals:
            daily_totals[date] = 0.0

        daily_totals[date] += water_value

    results = []

    for date, total in sorted(
        daily_totals.items()
    ):

        results.append({
            "date": date,
            "total_water_liters": round(
                total,
                2
            )
        })

    return results

def get_latest_waste_data():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                w.facility_id,
                f.facility_name,
                w.reading_ts,
                w.waste_type,
                w.waste_quantity_kg,
                w.recyclable_quantity_kg,
                w.hazardous_quantity_kg,
                w.disposal_method,
                w.anomaly_flag,
                w.anomaly_reason
            FROM waste_readings w
            JOIN facilities f
                ON w.facility_id = f.facility_id
            WHERE w.reading_ts = (
                SELECT MAX(w2.reading_ts)
                FROM waste_readings w2
                WHERE w2.facility_id = w.facility_id
            )
            ORDER BY w.facility_id;
        """)

        rows = cursor.fetchall()

        waste_data = []

        for row in rows:
            waste_data.append({
                "facility_id": row[0],
                "facility_name": row[1],
                "reading_ts": row[2],
                "waste_type": row[3],
                "waste_quantity_kg": float(row[4]),
                "recyclable_quantity_kg": float(row[5]),
                "hazardous_quantity_kg": float(row[6]),
                "disposal_method": row[7],
                "anomaly_flag": row[8],
                "anomaly_reason": row[9]
            })

        return waste_data

    finally:
        cursor.close()
        conn.close()



def get_latest_air_quality_data():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.facility_id,
                f.facility_name,
                a.reading_ts,
                a.aqi,
                a.pm25,
                a.pm10,
                a.aqi_category
            FROM air_quality_readings a
            JOIN facilities f
                ON a.facility_id = f.facility_id
            WHERE a.reading_ts = (
                SELECT MAX(a2.reading_ts)
                FROM air_quality_readings a2
                WHERE a2.facility_id = a.facility_id
            )
            ORDER BY a.facility_id;
        """)

        rows = cursor.fetchall()

        air_quality_data = []

        for row in rows:
            air_quality_data.append({
                "facility_id": row[0],
                "facility_name": row[1],
                "reading_ts": row[2],
                "aqi": row[3],
                "pm25": float(row[4]) if row[4] is not None else None,
                "pm10": float(row[5]) if row[5] is not None else None,
                "aqi_category": row[6]
            })

        return air_quality_data

    finally:
        cursor.close()
        conn.close()


def get_latest_traffic_data():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                t.facility_id,
                f.facility_name,
                t.reading_ts,
                t.vehicle_count,
                t.heavy_vehicle_count,
                t.average_speed_kmph,
                t.congestion_level,
                t.lane_occupancy_percent
            FROM traffic_readings t
            JOIN facilities f
                ON t.facility_id = f.facility_id
            WHERE t.reading_ts = (
                SELECT MAX(t2.reading_ts)
                FROM traffic_readings t2
                WHERE t2.facility_id = t.facility_id
            )
            ORDER BY t.facility_id;
        """)

        rows = cursor.fetchall()

        traffic_data = []

        for row in rows:
            traffic_data.append({
                "facility_id": row[0],
                "facility_name": row[1],
                "reading_ts": row[2],
                "vehicle_count": row[3],
                "heavy_vehicle_count": row[4],
                "average_speed_kmph": (
                    float(row[5]) if row[5] is not None else None
                ),
                "congestion_level": row[6],
                "lane_occupancy_percent": float(row[7])
            })

        return traffic_data

    finally:
        cursor.close()
        conn.close()

def get_alerts():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.alert_id,
                a.facility_id,
                f.facility_name,
                a.sensor_id,
                a.alert_type,
                a.severity,
                a.message,
                a.value,
                a.threshold,
                a.reading_ts
            FROM alerts a
            JOIN facilities f
                ON a.facility_id = f.facility_id
            WHERE a.status = 'ACTIVE'
            ORDER BY
                CASE a.severity
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                    ELSE 5
                END,
                a.reading_ts DESC;
        """)

        rows = cursor.fetchall()

        alerts = []

        for row in rows:
            alerts.append({
                "alert_id": row[0],
                "facility_id": row[1],
                "facility_name": row[2],
                "sensor_id": row[3],
                "alert_type": row[4],
                "severity": row[5],
                "message": row[6],
                "value": float(row[7]) if row[7] is not None else None,
                "threshold": float(row[8]) if row[8] is not None else None,
                "reading_ts": row[9]
            })

        return alerts

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":

    water_history = get_water_history(7)

    daily_summary = summarize_water_by_day(
        water_history
    )

    print("\n=== DAILY WATER TOTALS ===")

    for record in daily_summary:

        print(
            record["date"],
            "|",
            record["total_water_liters"],
            "liters"
        )
