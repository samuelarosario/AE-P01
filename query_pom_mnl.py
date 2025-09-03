#!/usr/bin/env python3
"""
Query flight routes from POM (Port Moresby) to MNL (Manila).
"""

from aviation_edge_client import AviationEdgeClient

def query_pom_to_mnl():
    """Query routes from POM to MNL."""
    try:
        # Initialize the client
        client = AviationEdgeClient()
        
        print("Aviation Edge API - Flight Routes Query")
        print("=" * 50)
        print("Searching for routes: POM (Port Moresby) → MNL (Manila)")
        print()
        
        # Query routes from POM to MNL
        routes = client.search_routes_by_airports("POM", "MNL")
        
        if routes:
            print(f"✓ Found {len(routes)} route(s):")
            print()
            
            for i, route in enumerate(routes, 1):
                print(f"{i}. {route.get('airlineIata', 'N/A')} {route.get('flightNumber', 'N/A')}")
                print(f"   Airline: {route.get('airlineIata', 'N/A')} ({route.get('airlineIcao', 'N/A')})")
                print(f"   Route: {route.get('departureIata', 'N/A')} → {route.get('arrivalIata', 'N/A')}")
                print(f"   Departure: {route.get('departureTime', 'N/A')}")
                print(f"   Arrival: {route.get('arrivalTime', 'N/A')}")
                
                if route.get('departureTerminal'):
                    print(f"   Departure Terminal: {route.get('departureTerminal')}")
                if route.get('arrivalTerminal'):
                    print(f"   Arrival Terminal: {route.get('arrivalTerminal')}")
                    
                if route.get('regNumber'):
                    print(f"   Aircraft: {route.get('regNumber')}")
                    
                if route.get('codeshares'):
                    print(f"   Codeshares: {route.get('codeshares')}")
                    
                print()
        else:
            print("❌ No direct routes found from POM to MNL")
            print()
            print("Let me also check for routes from POM (any destination):")
            
            # Check all routes from POM
            pom_routes = client.get_routes(departure_iata="POM")
            if pom_routes:
                print(f"✓ Found {len(pom_routes)} route(s) departing from POM:")
                print()
                destinations = set()
                for route in pom_routes:
                    dest = route.get('arrivalIata', 'N/A')
                    if dest != 'N/A':
                        destinations.add(dest)
                
                print(f"Available destinations from POM: {', '.join(sorted(destinations))}")
                print()
                
                # Show first few routes as examples
                for i, route in enumerate(pom_routes[:5], 1):
                    print(f"{i}. {route.get('airlineIata', 'N/A')} {route.get('flightNumber', 'N/A')} to {route.get('arrivalIata', 'N/A')}")
                
                if len(pom_routes) > 5:
                    print(f"... and {len(pom_routes) - 5} more routes")
            else:
                print("❌ No routes found departing from POM")
                
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your API key configuration.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    query_pom_to_mnl()
