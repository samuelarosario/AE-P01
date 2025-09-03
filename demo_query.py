"""
Mock demonstration of Aviation Edge API query results.
This shows what the API response would look like.
Run this after installing Python to see actual API calls.
"""

def mock_api_query():
    """Simulate what an API query would return."""
    
    # This is what a real API response from Aviation Edge would look like
    mock_response = [
        {
            "airlineIata": "W6",
            "airlineIcao": "WZZ", 
            "arrivalIata": "TRF",
            "arrivalIcao": "ENTO",
            "arrivalTerminal": None,
            "arrivalTime": "07:25:00",
            "codeshares": None,
            "departureIata": "OTP",
            "departureIcao": "LROP",
            "departureTerminal": None,
            "departureTime": "05:15:00",
            "flightNumber": "3215",
            "regNumber": "HA-LPJ, HA-LPV, HA-LPW, HA-LWF, HA-LWR, HA-LYB"
        },
        {
            "airlineIata": "RO",
            "airlineIcao": "ROT",
            "arrivalIata": "CDG",
            "arrivalIcao": "LFPG",
            "arrivalTerminal": "2F",
            "arrivalTime": "10:30:00",
            "codeshares": None,
            "departureIata": "OTP",
            "departureIcao": "LROP", 
            "departureTerminal": None,
            "departureTime": "08:45:00",
            "flightNumber": "381",
            "regNumber": "YR-BGG, YR-BGH"
        }
    ]
    
    return mock_response

def display_routes(routes, query_description):
    """Display route information in a formatted way."""
    print(f"\n{query_description}")
    print("=" * 60)
    
    if not routes:
        print("No routes found.")
        return
    
    print(f"Found {len(routes)} route(s):\n")
    
    for i, route in enumerate(routes, 1):
        print(f"{i}. {route['airlineIata']} {route['flightNumber']}")
        print(f"   Route: {route['departureIata']} → {route['arrivalIata']}")
        print(f"   Time: {route['departureTime']} → {route['arrivalTime']}")
        if route['arrivalTerminal']:
            print(f"   Arrival Terminal: {route['arrivalTerminal']}")
        print(f"   Aircraft: {route['regNumber']}")
        print()

def main():
    """Demo showing what API queries would look like."""
    print("Aviation Edge API Query Demonstration")
    print("=" * 50)
    print("Note: This is a mock demonstration showing expected API response format.")
    print("Install Python and run 'python main.py' for real API calls.\n")
    
    # Simulate different types of queries
    
    # 1. Routes from OTP (Bucharest)
    routes = mock_api_query()
    display_routes(routes, "Query: Routes from OTP (Bucharest) airport")
    
    # 2. Wizz Air routes
    wizz_routes = [route for route in routes if route['airlineIata'] == 'W6']
    display_routes(wizz_routes, "Query: Wizz Air (W6) routes")
    
    # 3. Routes to specific destination
    cdg_routes = [route for route in routes if route['arrivalIata'] == 'CDG']
    display_routes(cdg_routes, "Query: Routes to CDG (Paris) airport")
    
    print("\nTo make real API calls:")
    print("1. Install Python from Microsoft Store or python.org")
    print("2. Run: pip install requests python-dotenv")
    print("3. Run: python main.py")
    print(f"4. Your API key is already configured: 58b694-b40ef9")

if __name__ == "__main__":
    main()
