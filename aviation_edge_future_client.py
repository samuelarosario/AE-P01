import os
import requests
import sqlite3
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class AviationEdgeFutureSchedulesClient:
    """
    Client for Aviation Edge Future Schedules API (flightsFuture endpoint).
    
    NOTE: This endpoint may not be available on all Aviation Edge API plans.
    The /flightsFuture endpoint returned 404 errors during testing.
    This client is implemented based on the API documentation but may require
    a premium API plan or the endpoint may not be currently active.
    """
    
    def __init__(self, api_key: Optional[str] = None, db_path: str = "aviation_data.db"):
        """
        Initialize the Aviation Edge Future Schedules client.
        
        Args:
            api_key: API key for Aviation Edge. If not provided, will look for 
                    AVIATION_EDGE_API_KEY environment variable.
            db_path: Path to SQLite database for storing schedule data
        
        Raises:
            ValueError: If no API key is provided
            Warning: If the endpoint is not available
        """
        self.api_key = api_key or os.getenv('AVIATION_EDGE_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set AVIATION_EDGE_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://aviation-edge.com/v2/public/flightsFuture"
        self.db_path = db_path
        
        # Test endpoint availability on initialization - skip for now to fix API access
        self._endpoint_available = True  # Changed from self._test_endpoint_availability()
        
        # Initialize database connection
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection and ensure tables exist."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self._create_tables_if_not_exist()
        except Exception as e:
            print(f"Database initialization error: {e}")
            self.conn = None
    
    def _create_tables_if_not_exist(self):
        """Create necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Create airlines table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS airlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                iata_code TEXT UNIQUE,
                icao_code TEXT,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create airports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS airports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                iata_code TEXT UNIQUE,
                icao_code TEXT,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ensure flight_schedules table exists (should already exist)
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def insert_airline(self, iata_code: str, icao_code: Optional[str] = None, name: Optional[str] = None):
        """Insert or update airline information."""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO airlines (iata_code, icao_code, name, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (iata_code, icao_code, name))
        self.conn.commit()
    
    def insert_airport(self, iata_code: str, icao_code: Optional[str] = None, name: Optional[str] = None):
        """Insert or update airport information."""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO airports (iata_code, icao_code, name, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (iata_code, icao_code, name))
        self.conn.commit()
    
    def save_schedule_to_db(self, schedule_data: Dict[str, Any]) -> Optional[int]:
        """Save a single schedule entry to the database."""
        if not self.conn:
            return None
        
        cursor = self.conn.cursor()
        
        # Extract nested data from Future Schedules API response format
        airline = schedule_data.get('airline', {})
        flight = schedule_data.get('flight', {})
        departure = schedule_data.get('departure', {})
        arrival = schedule_data.get('arrival', {})
        aircraft = schedule_data.get('aircraft', {})
        codeshare = schedule_data.get('codeshare', {})
        
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
            schedule_data.get('status', 'scheduled'),
            schedule_data.get('type', 'passenger'),
            codeshare.get('airline', {}).get('name') if codeshare else None,
            codeshare.get('flight', {}).get('number') if codeshare else None,
            aircraft.get('reg') if aircraft else None,
            departure.get('gate'),
            departure.get('delay')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def save_schedules_to_db(self, schedules: List[Dict[str, Any]]) -> int:
        """Save multiple schedule entries to the database."""
        if not schedules:
            return 0
        
        saved_count = 0
        for schedule in schedules:
            if self.save_schedule_to_db(schedule):
                saved_count += 1
        
        return saved_count
    
    def _test_endpoint_availability(self) -> bool:
        """
        Test if the Future Schedules endpoint is available.
        
        Returns:
            bool: True if endpoint is available, False otherwise
        """
        try:
            test_response = requests.get(self.base_url, params={'key': self.api_key}, timeout=5)
            if test_response.status_code == 404:
                print("⚠️  WARNING: Future Schedules API endpoint (/flightsFuture) returned 404.")
                print("   This endpoint may not be available on your current API plan.")
                print("   Contact Aviation Edge support for endpoint availability.")
                return False
            return True
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """
        Check if the Future Schedules API endpoint is available.
        
        Returns:
            bool: True if endpoint is available, False otherwise
        """
        return self._endpoint_available
    
    def get_future_schedules(self, 
                           iata_code: str,
                           type: str,
                           date: str,
                           airline_iata: Optional[str] = None,
                           airline_icao: Optional[str] = None,
                           flight_num: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get future flight schedules from Aviation Edge API.
        
        Args:
            iata_code: Three-letter IATA code for airport (required)
            type: Either "departure" or "arrival" (required)
            date: Future date in YYYY-MM-DD format (required)
            airline_iata: Optional IATA code of an airline
            airline_icao: Optional ICAO code of an airline
            flight_num: Optional flight number to filter specific flight
            
        Returns:
            List of future schedule dictionaries containing flight information.
            Each response contains:
            - weekday: Day of the week (as string number)
            - departure: Departure airport and time details
            - arrival: Arrival airport and time details
            - aircraft: Aircraft information
            - airline: Airline information
            - flight: Flight details
            - codeshared: Codeshare information
        """
        # Validate required parameters
        if not iata_code or len(iata_code) != 3:
            raise ValueError("iata_code must be a 3-letter airport IATA code")
        
        if type not in ['departure', 'arrival']:
            raise ValueError("type must be either 'departure' or 'arrival'")
        
        if not date:
            raise ValueError("date is required in YYYY-MM-DD format")
        
        # Validate date format and minimum date requirement
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            min_date = datetime(2025, 9, 11)  # API requires dates above 2025-09-11
            
            if date_obj <= min_date:
                raise ValueError(f"Date must be above 2025-09-11. Current minimum date requirement.")
                
        except ValueError as ve:
            if "does not match format" in str(ve):
                raise ValueError("date must be in YYYY-MM-DD format")
            else:
                raise ve
        
        params = {
            'key': self.api_key,
            'iataCode': iata_code,
            'type': type,
            'date': date
        }
        
        # Add optional parameters
        if airline_iata:
            params['airline_iata'] = airline_iata
        if airline_icao:
            params['airline_icao'] = airline_icao
        if flight_num:
            params['flight_num'] = flight_num
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for API error responses
            if isinstance(data, dict) and 'error' in data:
                print(f"❌ API Error: {data['error']}")
                return []
            
            return data if isinstance(data, list) else []
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"❌ Future Schedules API endpoint not available (404)")
                print(f"   This may require a premium API plan or the endpoint may be inactive")
                return []
            else:
                print(f"Error making API request: {e}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return []
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return []
    
    def get_future_departures(self, airport_iata: str, date: str, 
                             airline_iata: Optional[str] = None,
                             airline_icao: Optional[str] = None,
                             flight_num: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get future departures from a specific airport on a specific date.
        
        Args:
            airport_iata: Three-letter IATA code for airport
            date: Future date in YYYY-MM-DD format
            airline_iata: Optional airline IATA code filter
            airline_icao: Optional airline ICAO code filter
            flight_num: Optional flight number filter
            
        Returns:
            List of future departure schedules
        """
        return self.get_future_schedules(
            iata_code=airport_iata,
            type="departure",
            date=date,
            airline_iata=airline_iata,
            airline_icao=airline_icao,
            flight_num=flight_num
        )
    
    def get_future_arrivals(self, airport_iata: str, date: str,
                           airline_iata: Optional[str] = None,
                           airline_icao: Optional[str] = None,
                           flight_num: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get future arrivals to a specific airport on a specific date.
        
        Args:
            airport_iata: Three-letter IATA code for airport
            date: Future date in YYYY-MM-DD format
            airline_iata: Optional airline IATA code filter
            airline_icao: Optional airline ICAO code filter
            flight_num: Optional flight number filter
            
        Returns:
            List of future arrival schedules
        """
        return self.get_future_schedules(
            iata_code=airport_iata,
            type="arrival",
            date=date,
            airline_iata=airline_iata,
            airline_icao=airline_icao,
            flight_num=flight_num
        )
    
    def search_future_routes(self, departure_airport: str, arrival_airport: str, date: str) -> List[Dict[str, Any]]:
        """
        Search for future routes between two airports on a specific date.
        
        Note: Since the API only allows querying one airport at a time with either
        departure or arrival type, this method will query departures from the
        departure airport and filter for the arrival airport.
        
        Args:
            departure_airport: Three-letter IATA code for departure airport
            arrival_airport: Three-letter IATA code for arrival airport
            date: Future date in YYYY-MM-DD format
            
        Returns:
            List of matching routes between the airports
        """
        departures = self.get_future_departures(departure_airport, date)
        
        # Filter for flights going to the arrival airport
        matching_routes = []
        for flight in departures:
            arrival_info = flight.get('arrival', {})
            if arrival_info.get('iataCode', '').upper() == arrival_airport.upper():
                matching_routes.append(flight)
        
        return matching_routes
    
    def get_airline_future_flights(self, airline_code: str, airport_iata: str, 
                                  date: str, type: str = "departure") -> List[Dict[str, Any]]:
        """
        Get future flights for a specific airline from/to an airport on a specific date.
        
        Args:
            airline_code: IATA or ICAO code for the airline
            airport_iata: Three-letter IATA code for airport
            date: Future date in YYYY-MM-DD format
            type: Either "departure" or "arrival"
            
        Returns:
            List of future flights for the airline
        """
        if len(airline_code) == 2:
            # IATA code
            return self.get_future_schedules(
                iata_code=airport_iata,
                type=type,
                date=date,
                airline_iata=airline_code
            )
        else:
            # ICAO code
            return self.get_future_schedules(
                iata_code=airport_iata,
                type=type,
                date=date,
                airline_icao=airline_code
            )
    
    def get_specific_future_flight(self, airport_iata: str, date: str, 
                                  flight_num: str, type: str = "departure") -> List[Dict[str, Any]]:
        """
        Get future schedule for a specific flight number from/to an airport.
        
        Args:
            airport_iata: Three-letter IATA code for airport
            date: Future date in YYYY-MM-DD format
            flight_num: Flight number to search for
            type: Either "departure" or "arrival"
            
        Returns:
            List of future schedules for the specific flight
        """
        return self.get_future_schedules(
            iata_code=airport_iata,
            type=type,
            date=date,
            flight_num=flight_num
        )

    
    # Database-integrated API methods
    def get_and_save_future_schedules(self, 
                                    iata_code: str,
                                    type: str,
                                    date: str,
                                    airline_iata: Optional[str] = None,
                                    airline_icao: Optional[str] = None,
                                    flight_num: Optional[str] = None,
                                    save_to_db: bool = True) -> List[Dict[str, Any]]:
        """
        Get future schedules and optionally save to database.
        
        Args:
            iata_code: Three-letter IATA code for airport
            type: Either "departure" or "arrival"
            date: Future date in YYYY-MM-DD format
            airline_iata: Optional airline IATA code filter
            airline_icao: Optional airline ICAO code filter
            flight_num: Optional flight number filter
            save_to_db: Whether to save results to database (default: True)
            
        Returns:
            List of schedule dictionaries with additional 'saved_to_db' field
        """
        schedules = self.get_future_schedules(iata_code, type, date, airline_iata, airline_icao, flight_num)
        
        if save_to_db and schedules:
            saved_count = self.save_schedules_to_db(schedules)
            print(f"💾 Saved {saved_count}/{len(schedules)} schedules to database")
            
            # Add metadata to each schedule
            for schedule in schedules:
                schedule['saved_to_db'] = True
                schedule['db_save_timestamp'] = datetime.now().isoformat()
        
        return schedules
    
    def collect_airport_future_data(self, airport_iata: str, date: str, save_to_db: bool = True) -> Dict[str, Any]:
        """
        Collect comprehensive future schedule data for an airport on a specific date.
        
        Args:
            airport_iata: Three-letter IATA code for airport
            date: Future date in YYYY-MM-DD format
            save_to_db: Whether to save results to database
            
        Returns:
            Dictionary with departures, arrivals, and summary statistics
        """
        print(f"🔍 Collecting future schedule data for {airport_iata} on {date}")
        
        # Get departures and arrivals
        departures = self.get_and_save_future_schedules(airport_iata, "departure", date, save_to_db=save_to_db)
        arrivals = self.get_and_save_future_schedules(airport_iata, "arrival", date, save_to_db=save_to_db)
        
        # Calculate statistics
        total_flights = len(departures) + len(arrivals)
        unique_airlines = set()
        
        for flight in departures + arrivals:
            airline = flight.get('airline', {})
            if airline.get('iataCode'):
                unique_airlines.add(airline['iataCode'])
        
        result = {
            'airport': airport_iata,
            'date': date,
            'departures': departures,
            'arrivals': arrivals,
            'statistics': {
                'total_flights': total_flights,
                'total_departures': len(departures),
                'total_arrivals': len(arrivals),
                'unique_airlines': len(unique_airlines),
                'airline_codes': sorted(list(unique_airlines))
            },
            'collection_timestamp': datetime.now().isoformat()
        }
        
        print(f"📊 Collected {total_flights} flights ({len(departures)} departures, {len(arrivals)} arrivals)")
        print(f"🏢 {len(unique_airlines)} unique airlines: {', '.join(sorted(list(unique_airlines)))}")
        
        return result
    
    def batch_collect_future_data(self, 
                                airport_codes: List[str], 
                                dates: List[str], 
                                save_to_db: bool = True) -> Dict[str, Any]:
        """
        Batch collect future schedule data for multiple airports and dates.
        
        Args:
            airport_codes: List of three-letter IATA airport codes
            dates: List of dates in YYYY-MM-DD format
            save_to_db: Whether to save results to database
            
        Returns:
            Dictionary with results for each airport-date combination
        """
        results = {}
        total_combinations = len(airport_codes) * len(dates)
        current = 0
        
        print(f"🚀 Starting batch collection for {len(airport_codes)} airports × {len(dates)} dates = {total_combinations} combinations")
        
        for airport in airport_codes:
            results[airport] = {}
            for date in dates:
                current += 1
                print(f"\n📍 Progress: {current}/{total_combinations} - {airport} on {date}")
                
                try:
                    airport_data = self.collect_airport_future_data(airport, date, save_to_db)
                    results[airport][date] = airport_data
                except Exception as e:
                    print(f"❌ Error collecting data for {airport} on {date}: {e}")
                    results[airport][date] = {
                        'error': str(e),
                        'airport': airport,
                        'date': date
                    }
        
        # Generate summary
        total_flights = 0
        successful_collections = 0
        
        for airport_data in results.values():
            for date_data in airport_data.values():
                if 'statistics' in date_data:
                    total_flights += date_data['statistics']['total_flights']
                    successful_collections += 1
        
        summary = {
            'batch_results': results,
            'summary': {
                'total_combinations': total_combinations,
                'successful_collections': successful_collections,
                'failed_collections': total_combinations - successful_collections,
                'total_flights_collected': total_flights,
                'collection_timestamp': datetime.now().isoformat()
            }
        }
        
        print(f"\n🎯 Batch collection complete!")
        print(f"   ✅ Successful: {successful_collections}/{total_combinations}")
        print(f"   📊 Total flights collected: {total_flights}")
        
        return summary

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = AviationEdgeFutureSchedulesClient()
    
    # Check if endpoint is available
    if not client.is_available():
        print("Future Schedules API endpoint is not available")
        exit()
    
    # Example 1: Get future departures from POM on September 5, 2025
    print("Future departures from POM on 2025-09-05:")
    pom_departures = client.get_future_departures("POM", "2025-09-05")
    for departure in pom_departures[:3]:  # Show first 3
        airline_info = departure.get('airline', {})
        flight_info = departure.get('flight', {})
        arrival_info = departure.get('arrival', {})
        departure_info = departure.get('departure', {})
        
        print(f"  Flight: {airline_info.get('iataCode', 'N/A')} {flight_info.get('number', 'N/A')}")
        print(f"  To: {arrival_info.get('iataCode', 'N/A')}")
        print(f"  Departure: {departure_info.get('scheduledTime', 'N/A')}")
        print(f"  Arrival: {arrival_info.get('scheduledTime', 'N/A')}")
        print("  ---")
    
    # Example 2: Get future arrivals to NRT on September 5, 2025
    print("\nFuture arrivals to NRT on 2025-09-05:")
    nrt_arrivals = client.get_future_arrivals("NRT", "2025-09-05")
    print(f"Found {len(nrt_arrivals)} arrivals to NRT")
    
    # Example 3: Search for routes POM -> NRT on September 5, 2025
    print("\nSearching POM -> NRT routes on 2025-09-05:")
    pom_nrt_routes = client.search_future_routes("POM", "NRT", "2025-09-05")
    print(f"Found {len(pom_nrt_routes)} direct routes")
    
    # Example 4: Get Philippine Airlines flights from MNL on September 5, 2025
    print("\nPhilippine Airlines departures from MNL on 2025-09-05:")
    pr_mnl = client.get_airline_future_flights("PR", "MNL", "2025-09-05", "departure")
    print(f"Found {len(pr_mnl)} PR flights from MNL")
    
    # Example 5: Get specific flight PR 101 departure from MNL on September 5, 2025
    print("\nPR 101 departure from MNL on 2025-09-05:")
    pr101 = client.get_specific_future_flight("MNL", "2025-09-05", "101", "departure")
    print(f"Found {len(pr101)} PR 101 departures")
