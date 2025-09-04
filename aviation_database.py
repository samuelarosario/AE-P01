import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import bcrypt
import uuid

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
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_uuid TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Mission Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mission_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_uuid TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                departure_airport TEXT,
                arrival_airport TEXT,
                departure_date DATE,
                return_date DATE,
                passenger_count INTEGER DEFAULT 1,
                aircraft_type TEXT,
                special_requirements TEXT,
                budget_amount DECIMAL(10,2),
                currency TEXT DEFAULT 'USD',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (departure_airport) REFERENCES airports(iata_code),
                FOREIGN KEY (arrival_airport) REFERENCES airports(iata_code)
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
        
        # New table indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_uuid ON users(user_uuid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mission_orders_user ON mission_orders(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mission_orders_uuid ON mission_orders(order_uuid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mission_orders_status ON mission_orders(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mission_orders_priority ON mission_orders(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mission_orders_departure_date ON mission_orders(departure_date)')
        
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
    
    # ===========================================
    # USER MANAGEMENT METHODS
    # ===========================================
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, email: str, password: str, first_name: str = None, last_name: str = None, is_admin: bool = False):
        """Create a new user with secure password hashing."""
        cursor = self.conn.cursor()
        
        # Check if email already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            raise ValueError(f"User with email {email} already exists")
        
        # Generate UUID and hash password
        user_uuid = str(uuid.uuid4())
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (user_uuid, email, password_hash, first_name, last_name, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_uuid, email, password_hash, first_name, last_name, is_admin))
        
        self.conn.commit()
        user_id = cursor.lastrowid
        
        # Return user info (without password hash)
        return {
            'id': user_id,
            'user_uuid': user_uuid,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'is_admin': is_admin
        }
    
    def authenticate_user(self, email: str, password: str):
        """Authenticate user and update last login."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT id, user_uuid, email, password_hash, first_name, last_name, is_active, is_admin
            FROM users WHERE email = ? AND is_active = 1
        ''', (email,))
        
        user = cursor.fetchone()
        if not user:
            return None
        
        if not self.verify_password(password, user['password_hash']):
            return None
        
        # Update last login
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
        self.conn.commit()
        
        # Return user info (without password hash)
        return {
            'id': user['id'],
            'user_uuid': user['user_uuid'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'is_admin': user['is_admin']
        }
    
    def get_user_by_id(self, user_id: int):
        """Get user by ID."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, user_uuid, email, first_name, last_name, is_active, is_admin, created_at, last_login
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        return dict(user) if user else None
    
    def get_user_by_uuid(self, user_uuid: str):
        """Get user by UUID."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, user_uuid, email, first_name, last_name, is_active, is_admin, created_at, last_login
            FROM users WHERE user_uuid = ?
        ''', (user_uuid,))
        
        user = cursor.fetchone()
        return dict(user) if user else None
    
    def update_user(self, user_id: int, **kwargs):
        """Update user information."""
        cursor = self.conn.cursor()
        
        allowed_fields = ['email', 'first_name', 'last_name', 'is_active', 'is_admin']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    def change_password(self, user_id: int, new_password: str):
        """Change user password."""
        cursor = self.conn.cursor()
        password_hash = self.hash_password(new_password)
        
        cursor.execute('''
            UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (password_hash, user_id))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def list_users(self, active_only: bool = True):
        """List all users."""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT id, user_uuid, email, first_name, last_name, is_active, is_admin, created_at, last_login
            FROM users
        '''
        
        if active_only:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    # ===========================================
    # MISSION ORDER MANAGEMENT METHODS
    # ===========================================
    
    def create_mission_order(self, user_id: int, title: str, **kwargs):
        """Create a new mission order."""
        cursor = self.conn.cursor()
        
        # Verify user exists
        cursor.execute('SELECT id FROM users WHERE id = ? AND is_active = 1', (user_id,))
        if not cursor.fetchone():
            raise ValueError(f"User ID {user_id} not found or inactive")
        
        # Generate UUID
        order_uuid = str(uuid.uuid4())
        
        # Allowed fields for mission orders
        allowed_fields = {
            'description': kwargs.get('description'),
            'priority': kwargs.get('priority', 'medium'),
            'status': kwargs.get('status', 'pending'),
            'departure_airport': kwargs.get('departure_airport'),
            'arrival_airport': kwargs.get('arrival_airport'),
            'departure_date': kwargs.get('departure_date'),
            'return_date': kwargs.get('return_date'),
            'passenger_count': kwargs.get('passenger_count', 1),
            'aircraft_type': kwargs.get('aircraft_type'),
            'special_requirements': kwargs.get('special_requirements'),
            'budget_amount': kwargs.get('budget_amount'),
            'currency': kwargs.get('currency', 'USD')
        }
        
        cursor.execute('''
            INSERT INTO mission_orders (
                order_uuid, user_id, title, description, priority, status,
                departure_airport, arrival_airport, departure_date, return_date,
                passenger_count, aircraft_type, special_requirements,
                budget_amount, currency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_uuid, user_id, title,
            allowed_fields['description'], allowed_fields['priority'], allowed_fields['status'],
            allowed_fields['departure_airport'], allowed_fields['arrival_airport'],
            allowed_fields['departure_date'], allowed_fields['return_date'],
            allowed_fields['passenger_count'], allowed_fields['aircraft_type'],
            allowed_fields['special_requirements'], allowed_fields['budget_amount'],
            allowed_fields['currency']
        ))
        
        self.conn.commit()
        order_id = cursor.lastrowid
        
        return {
            'id': order_id,
            'order_uuid': order_uuid,
            'user_id': user_id,
            'title': title,
            **allowed_fields
        }
    
    def get_mission_order_by_id(self, order_id: int):
        """Get mission order by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM mission_orders WHERE id = ?', (order_id,))
        
        order = cursor.fetchone()
        return dict(order) if order else None
    
    def get_mission_order_by_uuid(self, order_uuid: str):
        """Get mission order by UUID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM mission_orders WHERE order_uuid = ?', (order_uuid,))
        
        order = cursor.fetchone()
        return dict(order) if order else None
    
    def get_user_mission_orders(self, user_id: int, status: str = None):
        """Get all mission orders for a user."""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM mission_orders WHERE user_id = ?"
        params = [user_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_mission_order(self, order_id: int, **kwargs):
        """Update mission order."""
        cursor = self.conn.cursor()
        
        allowed_fields = [
            'title', 'description', 'priority', 'status', 'departure_airport',
            'arrival_airport', 'departure_date', 'return_date', 'passenger_count',
            'aircraft_type', 'special_requirements', 'budget_amount', 'currency'
        ]
        
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        # Handle completion
        if kwargs.get('status') == 'completed':
            updates.append("completed_at = CURRENT_TIMESTAMP")
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(order_id)
        
        query = f"UPDATE mission_orders SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    def list_mission_orders(self, status: str = None, priority: str = None, limit: int = None):
        """List mission orders with optional filters."""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT mo.*, u.email, u.first_name, u.last_name
            FROM mission_orders mo
            JOIN users u ON mo.user_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if status:
            query += " AND mo.status = ?"
            params.append(status)
        
        if priority:
            query += " AND mo.priority = ?"
            params.append(priority)
        
        query += " ORDER BY mo.created_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_mission_order_statistics(self):
        """Get mission order statistics."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total orders
        cursor.execute('SELECT COUNT(*) as total FROM mission_orders')
        stats['total_orders'] = cursor.fetchone()['total']
        
        # Orders by status
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM mission_orders
            GROUP BY status
        ''')
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Orders by priority
        cursor.execute('''
            SELECT priority, COUNT(*) as count
            FROM mission_orders
            GROUP BY priority
        ''')
        stats['by_priority'] = {row['priority']: row['count'] for row in cursor.fetchall()}
        
        # Recent orders (last 30 days)
        cursor.execute('''
            SELECT COUNT(*) as recent
            FROM mission_orders
            WHERE created_at >= datetime('now', '-30 days')
        ''')
        stats['recent_orders'] = cursor.fetchone()['recent']
        
        return stats
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
