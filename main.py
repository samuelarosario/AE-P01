from aviation_edge_client import AviationEdgeClient

def main():
    """Main function to demonstrate Aviation Edge API usage."""
    try:
        # Initialize the client
        client = AviationEdgeClient()
        
        print("Aviation Edge API Client Demo")
        print("=" * 40)
        
        # Example 1: Get routes from OTP airport (Bucharest)
        print("\n1. Routes from OTP (Bucharest):")
        routes = client.get_routes(departure_iata="OTP")
        if routes:
            print(f"Found {len(routes)} routes")
            # Display first route as example
            if isinstance(routes, list) and len(routes) > 0:
                route = routes[0]
                print(f"Sample route: {route.get('airlineIata', 'N/A')} {route.get('flightNumber', 'N/A')}")
                print(f"  {route.get('departureIata', 'N/A')} -> {route.get('arrivalIata', 'N/A')}")
                print(f"  Departure: {route.get('departureTime', 'N/A')}")
                print(f"  Arrival: {route.get('arrivalTime', 'N/A')}")
        else:
            print("No routes found")
        
        # Example 2: Search for specific airline routes
        print("\n2. Wizz Air (W6) routes:")
        routes = client.get_airline_routes("W6")
        if routes:
            print(f"Found {len(routes)} Wizz Air routes")
        else:
            print("No Wizz Air routes found")
        
        # Example 3: Routes between specific airports
        print("\n3. Routes from OTP to TRF:")
        routes = client.search_routes_by_airports("OTP", "TRF")
        if routes:
            print(f"Found {len(routes)} routes between OTP and TRF")
            for route in routes[:3]:  # Show first 3 routes
                print(f"  {route.get('airlineIata', 'N/A')} {route.get('flightNumber', 'N/A')} - {route.get('departureTime', 'N/A')} to {route.get('arrivalTime', 'N/A')}")
        else:
            print("No routes found between OTP and TRF")
            
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please make sure to set your API key in the .env file")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
