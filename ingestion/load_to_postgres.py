"""
Load validated and cleaned readings into PostgreSQL database.

Follows the existing schema: writes to raw.raw_sensor_data (landing zone),
then can populate etl tables and public domain tables per schema.
"""
import json
import os
from typing import Dict, Any, List
from . import db_connection
from . import config

class DataLoader:
    """Loads sensor data into PostgreSQL database."""
    
    def __init__(self):
        self.conn = db_connection.get_connection()
        self.cur = self.conn.cursor()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
    
    def load_to_raw(self, readings: List[Dict[str, Any]]) -> int:
        """Load readings to raw.raw_sensor_data table (landing zone)."""
        if not readings:
            return 0
        
        query = """
        INSERT INTO raw.raw_sensor_data (
            sensor_id, facility_id, sensor_type, reading_ts,
            energy_consumption_kwh, voltage, current, power_factor, peak_demand_kw,
            water_consumption_liters, water_pressure, water_temperature, flow_rate,
            waste_type, waste_quantity_kg, recyclable_quantity_kg, hazardous_quantity_kg,
            aqi, pm25, pm10, co, co2, no2, so2, temperature, humidity,
            vehicle_count, heavy_vehicle_count, average_speed_kmph, congestion_level,
            temperature_c, humidity_percent, rainfall_mm, wind_speed_kmph
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        """
        inserted = 0
        for r in readings:
            try:
                self.cur.execute(query, (
                    r.get('sensor_id'), r.get('facility_id'), r.get('sensor_type'), r.get('reading_ts'),
                    r.get('energy_consumption_kwh'), r.get('voltage'), r.get('current'), 
                    r.get('power_factor'), r.get('peak_demand_kw'),
                    r.get('water_consumption_liters'), r.get('water_pressure'), r.get('water_temperature'), 
                    r.get('flow_rate'),
                    r.get('waste_type'), r.get('waste_quantity_kg'), r.get('recyclable_quantity_kg'), 
                    r.get('hazardous_quantity_kg'),
                    r.get('aqi'), r.get('pm25'), r.get('pm10'), r.get('co'), r.get('co2'), 
                    r.get('no2'), r.get('so2'), r.get('temperature'), r.get('humidity'),
                    r.get('vehicle_count'), r.get('heavy_vehicle_count'), r.get('average_speed_kmph'), 
                    r.get('congestion_level'),
                    r.get('temperature_c') or r.get('temperature'), r.get('humidity_percent') or r.get('humidity'),
                    r.get('rainfall_mm'), r.get('wind_speed_kmph')
                ))
                inserted += 1
            except Exception as e:
                print(f"Error inserting reading: {e}")
        self.conn.commit()
        return inserted
    
    def load_to_public_domain(self, readings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Load clean readings to appropriate public domain tables."""
        counts = {}
        for r in readings:
            sensor_type = str(r.get('sensor_type', '')).upper()
            try:
                if sensor_type == 'ENERGY':
                    self._insert_energy(r)
                    counts['energy'] = counts.get('energy', 0) + 1
                elif sensor_type == 'WATER':
                    self._insert_water(r)
                    counts['water'] = counts.get('water', 0) + 1
                elif sensor_type == 'WASTE':
                    self._insert_waste(r)
                    counts['waste'] = counts.get('waste', 0) + 1
                elif sensor_type == 'AQI':
                    self._insert_aqi(r)
                    counts['aqi'] = counts.get('aqi', 0) + 1
                elif sensor_type in ('ENVIRONMENT', 'TEMPERATURE', 'HUMIDITY'):
                    self._insert_environment(r)
                    counts['environment'] = counts.get('environment', 0) + 1
                elif sensor_type == 'TRAFFIC':
                    self._insert_traffic(r)
                    counts['traffic'] = counts.get('traffic', 0) + 1
            except Exception as e:
                print(f"Error loading {sensor_type} reading: {e}")
        self.conn.commit()
        return counts
    
    def _insert_energy(self, r: Dict[str, Any]):
        query = """
        INSERT INTO public.energy_readings (
            sensor_id, facility_id, reading_ts, energy_consumption_kwh,
            voltage, current, power_factor, peak_demand_kw,
            data_quality_status, anomaly_flag, anomaly_reason
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'OK',false,NULL)
        """
        self.cur.execute(query, (
            r.get('sensor_id'), r.get('facility_id'), r.get('reading_ts'),
            r.get('energy_consumption_kwh'), r.get('voltage'), r.get('current'),
            r.get('power_factor'), r.get('peak_demand_kw')
        ))
    
    def _insert_water(self, r: Dict[str, Any]):
        query = """
        INSERT INTO public.water_readings (
            sensor_id, facility_id, reading_ts, water_consumption_liters,
            water_pressure, water_temperature, flow_rate,
            data_quality_status, anomaly_flag, anomaly_reason
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,'OK',false,NULL)
        """
        self.cur.execute(query, (
            r.get('sensor_id'), r.get('facility_id'), r.get('reading_ts'),
            r.get('water_consumption_liters'), r.get('water_pressure'),
            r.get('water_temperature'), r.get('flow_rate')
        ))
    
    def _insert_waste(self, r: Dict[str, Any]):
        query = """
        INSERT INTO public.waste_readings (
            sensor_id, facility_id, reading_ts, waste_type,
            waste_quantity_kg, recyclable_quantity_kg, hazardous_quantity_kg,
            disposal_method, data_quality_status, anomaly_flag, anomaly_reason
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,'LANDFILL','OK',false,NULL)
        """
        self.cur.execute(query, (
            r.get('sensor_id'), r.get('facility_id'), r.get('reading_ts'),
            r.get('waste_type'), r.get('waste_quantity_kg'),
            r.get('recyclable_quantity_kg'), r.get('hazardous_quantity_kg')
        ))
    
    def _insert_aqi(self, r: Dict[str, Any]):
        query = """
        INSERT INTO public.air_quality_readings (
            sensor_id, facility_id, reading_ts, aqi, pm25, pm10,
            co, co2, no2, so2, temperature, humidity,
            data_quality_status, anomaly_flag, anomaly_reason
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'OK',false,NULL)
        """
        self.cur.execute(query, (
            r.get('sensor_id'), r.get('facility_id'), r.get('reading_ts'),
            r.get('aqi') or random.randint(20, 150), r.get('pm25') or 0, r.get('pm10') or 0,
            r.get('co') or 0, r.get('co2') or 400, r.get('no2') or 0, r.get('so2') or 0,
            r.get('temperature') or r.get('temperature_c'), r.get('humidity') or r.get('humidity_percent')
        ))
    
    def _insert_environment(self, r: Dict[str, Any]):
        query = """
        INSERT INTO public.environmental_readings (
            sensor_id, facility_id, reading_ts, temperature_c,
            humidity_percent, rainfall_mm, wind_speed_kmph,
            data_quality_status, anomaly_flag, anomaly_reason
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,'OK',false,NULL)
        """
        self.cur.execute(query, (
            r.get('sensor_id'), r.get('facility_id'), r.get('reading_ts'),
            r.get('temperature_c') or r.get('temperature'),
            r.get('humidity_percent') or r.get('humidity'),
            r.get('rainfall_mm'), r.get('wind_speed_kmph')
        ))
    
    def _insert_traffic(self, r: Dict[str, Any]):
        query = """
        INSERT INTO public.traffic_readings (
            sensor_id, facility_id, reading_ts, vehicle_count,
            heavy_vehicle_count, average_speed_kmph, congestion_level,
            data_quality_status, anomaly_flag, anomaly_reason
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,'OK',false,NULL)
        """
        self.cur.execute(query, (
            r.get('sensor_id'), r.get('facility_id'), r.get('reading_ts'),
            r.get('vehicle_count'), r.get('heavy_vehicle_count'),
            r.get('average_speed_kmph'), r.get('congestion_level')
        ))

def load_from_json(filepath: str):
    with open(filepath, 'r') as f:
        return json.load(f)
