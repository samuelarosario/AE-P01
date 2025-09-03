#!/usr/bin/env python3
"""
Import all Aviation Edge API data into the database.
This script will re-run our queries and store the data in SQLite.
"""

from aviation_edge_client import AviationEdgeClient
from aviation_edge_schedule_client import AviationEdgeScheduleClient
from aviation_database import AviationDatabase
import json

def import_routes_data(db: AviationDatabase, routes_client: AviationEdgeClient):
    """Import routes data into the database."""
    print("Importing Routes Data...")
    print("-" * 40)
    
    # Re-query the POM to MNL route that we found earlier
    routes = routes_client.search_routes_by_airports("POM", "MNL")
    
    if routes:
        for route in routes:
            route_id = db.insert_route(route)
            print(f"Inserted route: {route.get('airlineIata')} {route.get('flightNumber')} "
                  f"({route.get('departureIata')} → {route.get('arrivalIata')}) - ID: {route_id}")
        
        # Log API usage
        db.log_api_usage("/routes", {"departureIata": "POM", "arrivalIata": "MNL"}, len(routes))
    
    print(f"Routes imported: {len(routes)}")
    print()

def import_schedules_data(db: AviationDatabase, schedules_client: AviationEdgeScheduleClient):
    """Import flight schedules data into the database."""
    print("Importing Flight Schedules Data...")
    print("-" * 40)
    
    airports = ["MNL", "POM", "SYD"]
    total_imported = 0
    
    for airport in airports:
        print(f"Processing {airport} airport schedules...")
        
        # Get departures
        departures = schedules_client.get_departures(airport)
        for schedule in departures:
            db.insert_schedule(schedule)
        
        # Get arrivals
        arrivals = schedules_client.get_arrivals(airport)
        for schedule in arrivals:
            db.insert_schedule(schedule)
        
        # Log API usage
        db.log_api_usage("/timetable", {"iataCode": airport, "type": "departure"}, len(departures))
        db.log_api_usage("/timetable", {"iataCode": airport, "type": "arrival"}, len(arrivals))
        
        airport_total = len(departures) + len(arrivals)
        total_imported += airport_total
        print(f"  {airport}: {len(departures)} departures + {len(arrivals)} arrivals = {airport_total} total")
    
    print(f"Total schedules imported: {total_imported}")
    print()

def display_database_summary(db: AviationDatabase):
    """Display comprehensive database statistics."""
    print("DATABASE SUMMARY")
    print("=" * 60)
    
    # Routes summary
    routes_stats = db.get_routes_summary()
    print("Routes Data:")
    print(f"  Total Routes: {routes_stats['total_routes']}")
    print(f"  Unique Airlines: {routes_stats['unique_airlines']}")
    print(f"  Departure Airports: {routes_stats['unique_departure_airports']}")
    print(f"  Arrival Airports: {routes_stats['unique_arrival_airports']}")
    print()
    
    # Schedules summary
    schedules_stats = db.get_schedules_summary()
    print("Flight Schedules Data:")
    print(f"  Total Schedules: {schedules_stats['total_schedules']}")
    print(f"  Unique Airlines: {schedules_stats['unique_airlines']}")
    print(f"  Departure Airports: {schedules_stats['unique_departure_airports']}")
    print(f"  Arrival Airports: {schedules_stats['unique_arrival_airports']}")
    print(f"  Active Flights: {schedules_stats['active_flights']}")
    print(f"  Landed Flights: {schedules_stats['landed_flights']}")
    print(f"  Scheduled Flights: {schedules_stats['scheduled_flights']}")
    print(f"  Departures: {schedules_stats['departures']}")
    print(f"  Arrivals: {schedules_stats['arrivals']}")
    print()
    
    # API usage summary
    api_stats = db.get_api_usage_summary()
    print("API Usage Statistics:")
    for stat in api_stats:
        print(f"  {stat['endpoint']}: {stat['call_count']} calls, {stat['total_records']} records")
    print()
    
    # Top airports by traffic
    top_airports = db.get_airport_traffic(limit=5)
    print("Top 5 Busiest Airports:")
    for i, airport in enumerate(top_airports, 1):
        print(f"  {i}. {airport['airport_code']}: {airport['flight_count']} flights "
              f"({airport['departures']} dep, {airport['arrivals']} arr)")
    print()
    
    # Top airlines by activity
    top_airlines = db.get_airline_activity(limit=5)
    print("Top 5 Most Active Airlines:")
    for i, airline in enumerate(top_airlines, 1):
        name = airline['airline_name'] or 'Unknown'
        print(f"  {i}. {airline['airline_iata']} ({name}): {airline['flight_count']} flights "
              f"({airline['active_flights']} active)")
    print()

def demonstrate_search_capabilities(db: AviationDatabase):
    """Demonstrate database search capabilities."""
    print("SEARCH CAPABILITIES DEMO")
    print("=" * 60)
    
    # Search flights from POM
    pom_flights = db.search_flights(departure_iata="POM")
    print(f"Flights departing from POM: {len(pom_flights)}")
    if pom_flights:
        for flight in pom_flights[:3]:  # Show first 3
            print(f"  {flight['airline_iata']} {flight['flight_number']}: "
                  f"{flight['departure_iata']} → {flight['arrival_iata']} "
                  f"at {flight['departure_scheduled_time']} ({flight['status']})")
    print()
    
    # Search Philippine Airlines flights
    pr_flights = db.search_flights(airline_iata="PR")
    print(f"Philippine Airlines flights: {len(pr_flights)}")
    if pr_flights:
        for flight in pr_flights[:3]:  # Show first 3
            print(f"  PR {flight['flight_number']}: "
                  f"{flight['departure_iata']} → {flight['arrival_iata']} "
                  f"at {flight['departure_scheduled_time']} ({flight['status']})")
    print()
    
    # Search active flights
    active_flights = db.search_flights(status="active")
    print(f"Currently active flights: {len(active_flights)}")
    print()

def main():
    """Main function to import all data and display summary."""
    print("Aviation Edge Data Import")
    print("=" * 50)
    print()
    
    try:
        # Initialize clients and database
        routes_client = AviationEdgeClient()
        schedules_client = AviationEdgeScheduleClient()
        
        with AviationDatabase() as db:
            # Import data
            import_routes_data(db, routes_client)
            import_schedules_data(db, schedules_client)
            
            # Display comprehensive summary
            display_database_summary(db)
            
            # Demonstrate search capabilities
            demonstrate_search_capabilities(db)
            
            print("✅ Data import completed successfully!")
            print(f"Database saved as: {db.db_path}")
            
    except Exception as e:
        print(f"❌ Error during import: {e}")

if __name__ == "__main__":
    main()
