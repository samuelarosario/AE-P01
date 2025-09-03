#!/usr/bin/env python3
"""
Query flight schedules using Aviation Edge Flight Schedules API.
This demonstrates the /timetable endpoint functionality.
"""

from aviation_edge_schedule_client import AviationEdgeScheduleClient
from datetime import datetime

def display_schedules(schedules, title, limit=5):
    """Display schedule information in a formatted way."""
    print(f"\n{title}")
    print("=" * 60)
    
    if not schedules:
        print("No schedules found.")
        return
    
    print(f"Found {len(schedules)} schedule(s):")
    print()
    
    # Show limited number of schedules to avoid overwhelming output
    displayed_schedules = schedules[:limit] if limit else schedules
    
    for i, schedule in enumerate(displayed_schedules, 1):
        print(f"{i}. {format_schedule_display(schedule)}")
        print("-" * 40)
    
    if limit and len(schedules) > limit:
        print(f"... and {len(schedules) - limit} more schedules")
        print()

def format_schedule_display(schedule):
    """Format a single schedule for display."""
    airline = schedule.get('airline', {})
    flight = schedule.get('flight', {})
    departure = schedule.get('departure', {})
    arrival = schedule.get('arrival', {})
    
    airline_iata = airline.get('iataCode', 'N/A')
    flight_number = flight.get('number', 'N/A')
    
    dep_airport = departure.get('iataCode', 'N/A')
    dep_time = departure.get('scheduledTime', 'N/A')
    dep_terminal = departure.get('terminal', '')
    
    arr_airport = arrival.get('iataCode', 'N/A')
    arr_time = arrival.get('scheduledTime', 'N/A')
    arr_terminal = arrival.get('terminal', '')
    
    status = schedule.get('status', 'Unknown')
    flight_type = schedule.get('type', 'Unknown')
    
    result = f"{airline_iata} {flight_number}\n"
    result += f"   Route: {dep_airport} → {arr_airport}\n"
    result += f"   Time: {dep_time} → {arr_time}\n"
    result += f"   Status: {status} | Type: {flight_type}\n"
    
    if dep_terminal:
        result += f"   Dep Terminal: {dep_terminal}"
    if arr_terminal:
        result += f" | Arr Terminal: {arr_terminal}"
    if dep_terminal or arr_terminal:
        result += "\n"
    
    # Check for codeshare
    if schedule.get('codeshared'):
        codeshare = schedule.get('codeshared', {})
        cs_airline = codeshare.get('airline', {}).get('name', '')
        cs_flight = codeshare.get('flight', {}).get('number', '')
        if cs_airline and cs_flight:
            result += f"   Codeshare: {cs_airline} {cs_flight}\n"
    
    return result

def query_airport_schedules():
    """Query flight schedules for specific airports."""
    try:
        # Initialize the schedule client
        client = AviationEdgeScheduleClient()
        
        print("Aviation Edge Flight Schedules API Query")
        print("=" * 50)
        print("Querying flight schedules using /timetable endpoint")
        print()
        
        # Query schedules for Manila (MNL) - both departures and arrivals
        print("1. Manila (MNL) Airport Schedules")
        mnl_schedules = client.get_all_schedules("MNL")
        
        # Display MNL departures
        display_schedules(mnl_schedules['departures'], "MNL Departures", limit=3)
        
        # Display MNL arrivals
        display_schedules(mnl_schedules['arrivals'], "MNL Arrivals", limit=3)
        
        # Query schedules for Port Moresby (POM)
        print("\n2. Port Moresby (POM) Airport Schedules")
        pom_schedules = client.get_all_schedules("POM")
        
        # Display POM departures
        display_schedules(pom_schedules['departures'], "POM Departures", limit=3)
        
        # Display POM arrivals
        display_schedules(pom_schedules['arrivals'], "POM Arrivals", limit=3)
        
        # Filter by specific airline (Philippine Airlines)
        print("\n3. Philippine Airlines (PR) Schedules at MNL")
        pr_departures = client.filter_by_airline(mnl_schedules['departures'], 'PR')
        display_schedules(pr_departures, "Philippine Airlines Departures from MNL", limit=5)
        
        # Filter by status
        print("\n4. Active Flights at MNL")
        active_departures = client.filter_by_status(mnl_schedules['departures'], 'active')
        display_schedules(active_departures, "Active Departures from MNL", limit=3)
        
        # Summary statistics
        print("\n" + "=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)
        print(f"MNL Departures: {len(mnl_schedules['departures'])}")
        print(f"MNL Arrivals: {len(mnl_schedules['arrivals'])}")
        print(f"POM Departures: {len(pom_schedules['departures'])}")
        print(f"POM Arrivals: {len(pom_schedules['arrivals'])}")
        print(f"Philippine Airlines flights from MNL: {len(pr_departures)}")
        print(f"Active departures from MNL: {len(active_departures)}")
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your API key configuration.")
    except Exception as e:
        print(f"An error occurred: {e}")

def query_specific_airport():
    """Interactive query for a specific airport."""
    try:
        client = AviationEdgeScheduleClient()
        
        print("\n" + "=" * 60)
        print("CUSTOM AIRPORT QUERY")
        print("=" * 60)
        
        # For demo purposes, let's query a specific airport
        airport_code = "SYD"  # Sydney as an example
        print(f"Querying schedules for {airport_code} airport...")
        
        # Get all schedules
        all_schedules = client.get_all_schedules(airport_code)
        
        print(f"\n{airport_code} Airport Schedule Summary:")
        print(f"Departures: {len(all_schedules['departures'])}")
        print(f"Arrivals: {len(all_schedules['arrivals'])}")
        
        # Show sample departures
        if all_schedules['departures']:
            display_schedules(all_schedules['departures'], f"{airport_code} Sample Departures", limit=2)
        
        # Show sample arrivals
        if all_schedules['arrivals']:
            display_schedules(all_schedules['arrivals'], f"{airport_code} Sample Arrivals", limit=2)
            
    except Exception as e:
        print(f"Error in custom query: {e}")

if __name__ == "__main__":
    query_airport_schedules()
    query_specific_airport()
