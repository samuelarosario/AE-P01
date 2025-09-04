from aviation_edge_schedule_client import AviationEdgeScheduleClient
from aviation_edge_future_client import AviationEdgeFutureSchedulesClient

def main():
    """Main function to demonstrate Aviation Edge API usage."""
    try:
        # Initialize the Schedule API client
        schedule_client = AviationEdgeScheduleClient()
        
        # Initialize the Future Schedules API client
        future_client = AviationEdgeFutureSchedulesClient()
        
        print("Aviation Edge API Client Demo")
        print("=" * 40)
        
        # Example 1: Get current schedules from MNL airport
        print("\n1. Current departures from MNL (Manila):")
        schedules = schedule_client.get_departures("MNL")
        if schedules:
            print(f"Found {len(schedules)} departures")
            # Display first schedule as example
            if isinstance(schedules, list) and len(schedules) > 0:
                schedule = schedules[0]
                airline = schedule.get('airline', {})
                flight = schedule.get('flight', {})
                departure = schedule.get('departure', {})
                arrival = schedule.get('arrival', {})
                print(f"Sample flight: {airline.get('name', 'N/A')} {flight.get('number', 'N/A')}")
                print(f"  {departure.get('iataCode', 'N/A')} -> {arrival.get('iataCode', 'N/A')}")
                print(f"  Departure: {departure.get('scheduledTime', 'N/A')}")
                print(f"  Status: {schedule.get('status', 'N/A')}")
        else:
            print("No schedules found")
        
        # Example 2: Search for Philippine Airlines schedules
        print("\n2. Philippine Airlines (PR) schedules:")
        pr_schedules = schedule_client.get_airline_schedules("PR")
        if pr_schedules:
            print(f"Found {len(pr_schedules)} Philippine Airlines schedules")
        else:
            print("No Philippine Airlines schedules found")
        
        # Example 3: Future Schedules API (if available)
        print("\n3. Future Schedules API Status:")
        if future_client.is_available():
            print("✅ Future Schedules API is available")
            print("   You can use future flight planning features")
            
            try:
                # Example future query (requires date after 2025-09-11)
                print("\n   Testing future schedules for MNL on 2025-09-12:")
                future_departures = future_client.get_and_save_future_schedules(
                    "MNL", "departure", "2025-09-12", save_to_db=True
                )
                print(f"   Found {len(future_departures)} future departures")
            except Exception as e:
                print(f"   Future schedules test failed: {e}")
        else:
            print("❌ Future Schedules API is not available")
            print("   Using current schedules and database for flight planning")
            
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please make sure to set your API key in the .env file")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
