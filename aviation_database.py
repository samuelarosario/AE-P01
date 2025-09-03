import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

class AviationDatabase:
    """Database manager for Aviation Edge API data."""
    
    def __init__(self, db_path: str = "aviation_data.db"):
        """Initialize the database connection and create tables."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary tables for aviation data."""
        cursor = self.conn.cursor()
        
        # Airlines table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS airlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                iata_code TEXT UNIQUE,
                icao_code TEXT UNIQUE,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Airports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS airports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                iata_code TEXT UNIQUE,
                icao_code TEXT UNIQUE,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Routes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                airline_iata TEXT,
                airline_icao TEXT,
                departure_iata TEXT,
                departure_icao TEXT,
                departure_terminal TEXT,
                departure_time TEXT,
                arrival_iata TEXT,
                arrival_icao TEXT,
                arrival_terminal TEXT,
                arrival_time TEXT,
                flight_number TEXT,
                reg_number TEXT,
                codeshares TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (airline_iata) REFERENCES airlines(iata_code),
                FOREIGN KEY (departure_iata) REFERENCES airports(iata_code),
                FOREIGN KEY (arrival_iata) REFERENCES airports(iata_code)
            )
        ''')
        
        # Flight schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flight_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                airline_iata TEXT,
                airline_icao TEXT,
                airline_name TEXT,
                flight_number TEXT,
                departure_iata TEXT,
                departure_icao TEXT,
                departure_terminal TEXT,
                departure_scheduled_time TEXT,
                departure_actual_time TEXT,
                arrival_iata TEXT,
                arrival_icao TEXT,
                arrival_terminal TEXT,
                arrival_scheduled_time TEXT,
                arrival_actual_time TEXT,
                status TEXT,
                flight_type TEXT,
                codeshare_airline TEXT,
                codeshare_flight TEXT,
                aircraft_registration TEXT,
                gate TEXT,
                delay_minutes INTEGER,
                query_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (airline_iata) REFERENCES airlines(iata_code),
                FOREIGN KEY (departure_iata) REFERENCES airports(iata_code),
                FOREIGN KEY (arrival_iata) REFERENCES airports(iata_code)
            )
        ''')
        
        # API usage tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                query_params TEXT,
                response_count INTEGER,
                query_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_routes_departure ON routes(departure_iata)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_routes_arrival ON routes(arrival_iata)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_routes_airline ON routes(airline_iata)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_departure ON flight_schedules(departure_iata)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_arrival ON flight_schedules(arrival_iata)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_airline ON flight_schedules(airline_iata)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_status ON flight_schedules(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_type ON flight_schedules(flight_type)')
        
        self.conn.commit()
    
    def insert_airline(self, iata_code: str, icao_code: str = None, name: str = None):
        """Insert or update airline information."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO airlines (iata_code, icao_code, name, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (iata_code, icao_code, name))
        self.conn.commit()
        return cursor.lastrowid
    
    def insert_airport(self, iata_code: str, icao_code: str = None, name: str = None):
        """Insert or update airport information."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO airports (iata_code, icao_code, name, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (iata_code, icao_code, name))
        self.conn.commit()
        return cursor.lastrowid
    
    def insert_route(self, route_data: Dict[str, Any]):
        """Insert route data from Aviation Edge routes API."""
        cursor = self.conn.cursor()
        
        # First ensure airlines and airports exist
        if route_data.get('airlineIata'):
            self.insert_airline(route_data['airlineIata'], route_data.get('airlineIcao'))
        if route_data.get('departureIata'):
            self.insert_airport(route_data['departureIata'], route_data.get('departureIcao'))
        if route_data.get('arrivalIata'):
            self.insert_airport(route_data['arrivalIata'], route_data.get('arrivalIcao'))
        
        # Convert reg_number to string if it's a list
        reg_number = route_data.get('regNumber')
        if isinstance(reg_number, list):
            reg_number = ', '.join(reg_number)
        
        cursor.execute('''
            INSERT INTO routes (
                airline_iata, airline_icao, departure_iata, departure_icao,
                departure_terminal, departure_time, arrival_iata, arrival_icao,
                arrival_terminal, arrival_time, flight_number, reg_number, codeshares
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            route_data.get('airlineIata'),
            route_data.get('airlineIcao'),
            route_data.get('departureIata'),
            route_data.get('departureIcao'),
            route_data.get('departureTerminal'),
            route_data.get('departureTime'),
            route_data.get('arrivalIata'),
            route_data.get('arrivalIcao'),
            route_data.get('arrivalTerminal'),
            route_data.get('arrivalTime'),
            route_data.get('flightNumber'),
            reg_number,
            json.dumps(route_data.get('codeshares')) if route_data.get('codeshares') else None
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def insert_schedule(self, schedule_data: Dict[str, Any]):
        """Insert flight schedule data from Aviation Edge timetable API."""
        cursor = self.conn.cursor()
        
        # Extract nested data
        airline = schedule_data.get('airline', {})
        flight = schedule_data.get('flight', {})
        departure = schedule_data.get('departure', {})
        arrival = schedule_data.get('arrival', {})
        codeshare = schedule_data.get('codeshared', {})
        
        # Ensure airlines and airports exist
        airline_iata = airline.get('iataCode')
        if airline_iata:
            self.insert_airline(airline_iata, airline.get('icaoCode'), airline.get('name'))
        
        dep_iata = departure.get('iataCode')
        if dep_iata:
            self.insert_airport(dep_iata, departure.get('icaoCode'))
        
        arr_iata = arrival.get('iataCode')
        if arr_iata:
            self.insert_airport(arr_iata, arrival.get('icaoCode'))
        
        cursor.execute('''
            INSERT INTO flight_schedules (
                airline_iata, airline_icao, airline_name, flight_number,
                departure_iata, departure_icao, departure_terminal,
                departure_scheduled_time, departure_actual_time,
                arrival_iata, arrival_icao, arrival_terminal,
                arrival_scheduled_time, arrival_actual_time,
                status, flight_type, codeshare_airline, codeshare_flight,
                aircraft_registration, gate, delay_minutes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            airline.get('iataCode'),
            airline.get('icaoCode'),
            airline.get('name'),
            flight.get('number'),
            departure.get('iataCode'),
            departure.get('icaoCode'),
            departure.get('terminal'),
            departure.get('scheduledTime'),
            departure.get('actualTime'),
            arrival.get('iataCode'),
            arrival.get('icaoCode'),
            arrival.get('terminal'),
            arrival.get('scheduledTime'),
            arrival.get('actualTime'),
            schedule_data.get('status'),
            schedule_data.get('type'),
            codeshare.get('airline', {}).get('name') if codeshare else None,
            codeshare.get('flight', {}).get('number') if codeshare else None,
            schedule_data.get('aircraft', {}).get('registration') if schedule_data.get('aircraft') else None,
            departure.get('gate'),
            departure.get('delay')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def log_api_usage(self, endpoint: str, query_params: Dict[str, Any], response_count: int):
        """Log API usage for tracking purposes."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO api_usage (endpoint, query_params, response_count)
            VALUES (?, ?, ?)
        ''', (endpoint, json.dumps(query_params), response_count))
        self.conn.commit()
    
    def get_routes_summary(self):
        """Get summary statistics for routes."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_routes,
                COUNT(DISTINCT airline_iata) as unique_airlines,
                COUNT(DISTINCT departure_iata) as unique_departure_airports,
                COUNT(DISTINCT arrival_iata) as unique_arrival_airports
            FROM routes
        ''')
        return dict(cursor.fetchone())
    
    def get_schedules_summary(self):
        """Get summary statistics for flight schedules."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_schedules,
                COUNT(DISTINCT airline_iata) as unique_airlines,
                COUNT(DISTINCT departure_iata) as unique_departure_airports,
                COUNT(DISTINCT arrival_iata) as unique_arrival_airports,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_flights,
                COUNT(CASE WHEN status = 'landed' THEN 1 END) as landed_flights,
                COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_flights,
                COUNT(CASE WHEN flight_type = 'departure' THEN 1 END) as departures,
                COUNT(CASE WHEN flight_type = 'arrival' THEN 1 END) as arrivals
            FROM flight_schedules
        ''')
        return dict(cursor.fetchone())
    
    def get_api_usage_summary(self):
        """Get API usage statistics."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                endpoint,
                COUNT(*) as call_count,
                SUM(response_count) as total_records,
                MIN(query_timestamp) as first_call,
                MAX(query_timestamp) as last_call
            FROM api_usage
            GROUP BY endpoint
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_airport_traffic(self, limit: int = 10):
        """Get busiest airports by flight count."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                COALESCE(departure_iata, arrival_iata) as airport_code,
                COUNT(*) as flight_count,
                COUNT(CASE WHEN flight_type = 'departure' THEN 1 END) as departures,
                COUNT(CASE WHEN flight_type = 'arrival' THEN 1 END) as arrivals
            FROM flight_schedules
            WHERE departure_iata IS NOT NULL OR arrival_iata IS NOT NULL
            GROUP BY COALESCE(departure_iata, arrival_iata)
            ORDER BY flight_count DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_airline_activity(self, limit: int = 10):
        """Get most active airlines by flight count."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                airline_iata,
                airline_name,
                COUNT(*) as flight_count,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_flights
            FROM flight_schedules
            WHERE airline_iata IS NOT NULL
            GROUP BY airline_iata, airline_name
            ORDER BY flight_count DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def search_flights(self, departure_iata: str = None, arrival_iata: str = None, 
                      airline_iata: str = None, status: str = None):
        """Search flights with flexible criteria."""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM flight_schedules WHERE 1=1"
        params = []
        
        if departure_iata:
            query += " AND departure_iata = ?"
            params.append(departure_iata)
        if arrival_iata:
            query += " AND arrival_iata = ?"
            params.append(arrival_iata)
        if airline_iata:
            query += " AND airline_iata = ?"
            params.append(airline_iata)
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY departure_scheduled_time"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
