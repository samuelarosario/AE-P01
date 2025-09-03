#!/usr/bin/env python3
"""
Aviation Database Query Tool
Interactive tool to explore the aviation database.
"""

from aviation_database import AviationDatabase
from datetime import datetime
import sqlite3

def display_table_info(db: AviationDatabase):
    """Display information about all tables in the database."""
    cursor = db.conn.cursor()
    
    print("DATABASE SCHEMA INFORMATION")
    print("=" * 60)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        print(f"\n📊 {table.upper()} ({count} records)")
        print("-" * 40)
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

def advanced_route_analysis(db: AviationDatabase):
    """Perform advanced analysis on route data."""
    cursor = db.conn.cursor()
    
    print("\n🛫 ROUTE ANALYSIS")
    print("=" * 60)
    
    # All routes with detailed information
    cursor.execute('''
        SELECT 
            airline_iata,
            flight_number,
            departure_iata,
            departure_time,
            arrival_iata,
            arrival_time,
            reg_number
        FROM routes
        ORDER BY airline_iata, flight_number
    ''')
    
    routes = cursor.fetchall()
    for route in routes:
        duration = "N/A"
        if route[3] and route[5]:  # If both times are available
            try:
                dep_time = datetime.strptime(route[3], "%H:%M:%S")
                arr_time = datetime.strptime(route[5], "%H:%M:%S")
                # Handle day change
                if arr_time < dep_time:
                    arr_time = arr_time.replace(day=arr_time.day + 1)
                duration_delta = arr_time - dep_time
                hours, remainder = divmod(duration_delta.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                duration = f"{hours}h {minutes}m"
            except:
                pass
        
        print(f"✈️  {route[0]} {route[1]}: {route[2]} ({route[3]}) → {route[4]} ({route[5]}) [{duration}]")
        if route[6]:
            print(f"   Aircraft: {route[6]}")

def advanced_schedule_analysis(db: AviationDatabase):
    """Perform advanced analysis on schedule data."""
    cursor = db.conn.cursor()
    
    print("\n📅 SCHEDULE ANALYSIS")
    print("=" * 60)
    
    # Flight status distribution
    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM flight_schedules
        GROUP BY status
        ORDER BY count DESC
    ''')
    
    print("Flight Status Distribution:")
    status_data = cursor.fetchall()
    for status, count in status_data:
        print(f"  {status or 'Unknown'}: {count}")
    
    # Peak departure hours
    cursor.execute('''
        SELECT 
            CASE 
                WHEN substr(departure_scheduled_time, 12, 2) BETWEEN '00' AND '05' THEN 'Night (00-05)'
                WHEN substr(departure_scheduled_time, 12, 2) BETWEEN '06' AND '11' THEN 'Morning (06-11)'
                WHEN substr(departure_scheduled_time, 12, 2) BETWEEN '12' AND '17' THEN 'Afternoon (12-17)'
                ELSE 'Evening (18-23)'
            END as time_period,
            COUNT(*) as flight_count
        FROM flight_schedules
        WHERE departure_scheduled_time IS NOT NULL
            AND flight_type = 'departure'
        GROUP BY time_period
        ORDER BY flight_count DESC
    ''')
    
    print("\nDeparture Time Distribution:")
    time_data = cursor.fetchall()
    for period, count in time_data:
        print(f"  {period}: {count} flights")
    
    # International vs Domestic (rough classification)
    cursor.execute('''
        SELECT 
            CASE 
                WHEN departure_iata IN ('SYD', 'MEL', 'BNE', 'PER', 'ADL', 'DRW', 'CNS', 'OOL')
                     AND arrival_iata IN ('SYD', 'MEL', 'BNE', 'PER', 'ADL', 'DRW', 'CNS', 'OOL')
                     THEN 'Domestic (Australia)'
                WHEN departure_iata LIKE 'RPXX' OR arrival_iata LIKE 'RPXX'
                     OR departure_iata IN ('MNL', 'CEB', 'DVO', 'ILO', 'TAG', 'CRK')
                     OR arrival_iata IN ('MNL', 'CEB', 'DVO', 'ILO', 'TAG', 'CRK')
                     THEN 'Domestic (Philippines)'
                ELSE 'International'
            END as route_type,
            COUNT(*) as count
        FROM flight_schedules
        WHERE departure_iata IS NOT NULL AND arrival_iata IS NOT NULL
        GROUP BY route_type
        ORDER BY count DESC
    ''')
    
    print("\nRoute Classification:")
    route_data = cursor.fetchall()
    for route_type, count in route_data:
        print(f"  {route_type}: {count} flights")

def codeshare_analysis(db: AviationDatabase):
    """Analyze codeshare partnerships."""
    cursor = db.conn.cursor()
    
    print("\n🤝 CODESHARE ANALYSIS")
    print("=" * 60)
    
    cursor.execute('''
        SELECT 
            airline_iata,
            airline_name,
            codeshare_airline,
            COUNT(*) as codeshare_count
        FROM flight_schedules
        WHERE codeshare_airline IS NOT NULL
        GROUP BY airline_iata, airline_name, codeshare_airline
        ORDER BY codeshare_count DESC
        LIMIT 10
    ''')
    
    codeshares = cursor.fetchall()
    if codeshares:
        print("Top Codeshare Partnerships:")
        for airline, name, partner, count in codeshares:
            print(f"  {airline} ({name}) ↔ {partner}: {count} shared flights")
    else:
        print("No codeshare data found.")

def airport_connectivity(db: AviationDatabase):
    """Analyze airport connectivity."""
    cursor = db.conn.cursor()
    
    print("\n🌐 AIRPORT CONNECTIVITY")
    print("=" * 60)
    
    # Airports with most destinations
    cursor.execute('''
        SELECT 
            departure_iata,
            COUNT(DISTINCT arrival_iata) as destinations
        FROM flight_schedules
        WHERE departure_iata IS NOT NULL AND arrival_iata IS NOT NULL
        GROUP BY departure_iata
        ORDER BY destinations DESC
        LIMIT 10
    ''')
    
    print("Airports with Most Destinations:")
    connectivity = cursor.fetchall()
    for airport, dest_count in connectivity:
        print(f"  {airport}: {dest_count} destinations")
    
    # Hub analysis - airports with both high departures and arrivals
    cursor.execute('''
        SELECT 
            airport_code,
            departure_count,
            arrival_count,
            (departure_count + arrival_count) as total_movements
        FROM (
            SELECT 
                departure_iata as airport_code,
                COUNT(*) as departure_count,
                0 as arrival_count
            FROM flight_schedules
            WHERE departure_iata IS NOT NULL
            GROUP BY departure_iata
            
            UNION ALL
            
            SELECT 
                arrival_iata as airport_code,
                0 as departure_count,
                COUNT(*) as arrival_count
            FROM flight_schedules
            WHERE arrival_iata IS NOT NULL
            GROUP BY arrival_iata
        )
        GROUP BY airport_code
        HAVING total_movements > 50
        ORDER BY total_movements DESC
        LIMIT 10
    ''')
    
    print("\nMajor Hub Airports (>50 movements):")
    hubs = cursor.fetchall()
    for airport, dep, arr, total in hubs:
        print(f"  {airport}: {total} movements ({dep} dep, {arr} arr)")

def main():
    """Main function to run database analysis."""
    print("Aviation Database Analysis Tool")
    print("=" * 50)
    
    try:
        with AviationDatabase() as db:
            display_table_info(db)
            advanced_route_analysis(db)
            advanced_schedule_analysis(db)
            codeshare_analysis(db)
            airport_connectivity(db)
            
            print(f"\n✅ Analysis completed!")
            print(f"Database: {db.db_path}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()
