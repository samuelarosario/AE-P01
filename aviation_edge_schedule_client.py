import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AviationEdgeScheduleClient:
    """Client for Aviation Edge Flight Schedules API (timetable endpoint)."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Aviation Edge Schedule client.
        
        Args:
            api_key: API key for Aviation Edge. If not provided, will look for 
                    AVIATION_EDGE_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('AVIATION_EDGE_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set AVIATION_EDGE_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://aviation-edge.com/v2/public/timetable"
    
    def get_schedules(self, 
                     iata_code: Optional[str] = None,
                     icao_code: Optional[str] = None,
                     type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get flight schedules from Aviation Edge API.
        
        Args:
            iata_code: Three-letter IATA code for airport
            icao_code: Four-letter ICAO code for airport
            type: Type of flights - 'departure' or 'arrival'
            
        Returns:
            List of schedule dictionaries containing flight information
        """
        params = {'key': self.api_key}
        
        # Add optional parameters
        if iata_code:
            params['iataCode'] = iata_code
        if icao_code:
            params['icaoCode'] = icao_code
        if type:
            params['type'] = type
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return []
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return []
    
    def get_departures(self, airport_code: str) -> List[Dict[str, Any]]:
        """
        Get departure schedules for a specific airport.
        
        Args:
            airport_code: IATA or ICAO code for the airport
            
        Returns:
            List of departure schedules
        """
        if len(airport_code) == 3:
            return self.get_schedules(iata_code=airport_code, type='departure')
        else:
            return self.get_schedules(icao_code=airport_code, type='departure')
    
    def get_arrivals(self, airport_code: str) -> List[Dict[str, Any]]:
        """
        Get arrival schedules for a specific airport.
        
        Args:
            airport_code: IATA or ICAO code for the airport
            
        Returns:
            List of arrival schedules
        """
        if len(airport_code) == 3:
            return self.get_schedules(iata_code=airport_code, type='arrival')
        else:
            return self.get_schedules(icao_code=airport_code, type='arrival')
    
    def get_all_schedules(self, airport_code: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get both departure and arrival schedules for an airport.
        
        Args:
            airport_code: IATA or ICAO code for the airport
            
        Returns:
            Dictionary with 'departures' and 'arrivals' keys
        """
        return {
            'departures': self.get_departures(airport_code),
            'arrivals': self.get_arrivals(airport_code)
        }
    
    def get_airline_schedules(self, airline_code: str) -> List[Dict[str, Any]]:
        """
        Get all schedules for a specific airline by searching major airports.
        Note: The timetable API doesn't support direct airline filtering,
        so this method searches multiple airports and filters results.
        
        Args:
            airline_code: IATA or ICAO airline code
            
        Returns:
            List of schedules for the specified airline
        """
        # Major airports to search for airline schedules
        major_airports = ['MNL', 'DVO', 'CEB', 'ILO', 'NRT', 'HND', 'ICN', 'BKK', 'SIN', 'HKG']
        all_schedules = []
        
        for airport in major_airports:
            try:
                # Get departures for this airport
                departures = self.get_departures(airport)
                # Filter by airline
                airline_departures = self.filter_by_airline(departures, airline_code)
                all_schedules.extend(airline_departures)
                
                # Small delay to avoid overwhelming API
                import time
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Warning: Could not get schedules for {airport}: {e}")
                continue
        
        # Remove duplicates based on flight number and departure time
        unique_schedules = []
        seen_flights = set()
        
        for schedule in all_schedules:
            flight_info = schedule.get('flight', {})
            departure_info = schedule.get('departure', {})
            key = (
                flight_info.get('number', ''),
                departure_info.get('scheduledTime', ''),
                departure_info.get('iataCode', '')
            )
            
            if key not in seen_flights:
                seen_flights.add(key)
                unique_schedules.append(schedule)
        
        return unique_schedules
    
    def filter_by_airline(self, schedules: List[Dict[str, Any]], airline_code: str) -> List[Dict[str, Any]]:
        """
        Filter schedules by airline code.
        
        Args:
            schedules: List of schedule dictionaries
            airline_code: IATA or ICAO airline code
            
        Returns:
            Filtered list of schedules for the specified airline
        """
        filtered = []
        for schedule in schedules:
            airline_info = schedule.get('airline', {})
            if (airline_info.get('iataCode') == airline_code or 
                airline_info.get('icaoCode') == airline_code):
                filtered.append(schedule)
        return filtered
    
    def filter_by_status(self, schedules: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
        """
        Filter schedules by flight status.
        
        Args:
            schedules: List of schedule dictionaries
            status: Flight status (e.g., 'scheduled', 'active', 'landed', 'cancelled', 'delayed')
            
        Returns:
            Filtered list of schedules with the specified status
        """
        return [schedule for schedule in schedules if schedule.get('status') == status]
    
    def format_schedule_info(self, schedule: Dict[str, Any]) -> str:
        """
        Format schedule information for display.
        
        Args:
            schedule: Single schedule dictionary
            
        Returns:
            Formatted string with schedule details
        """
        airline = schedule.get('airline', {})
        flight = schedule.get('flight', {})
        departure = schedule.get('departure', {})
        arrival = schedule.get('arrival', {})
        
        airline_name = airline.get('name', 'Unknown Airline')
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
        
        info = f"{airline_iata} {flight_number} - {airline_name}\n"
        info += f"Route: {dep_airport} → {arr_airport}\n"
        info += f"Schedule: {dep_time} → {arr_time}\n"
        
        if dep_terminal:
            info += f"Departure Terminal: {dep_terminal}\n"
        if arr_terminal:
            info += f"Arrival Terminal: {arr_terminal}\n"
            
        info += f"Status: {status}\n"
        info += f"Type: {flight_type}\n"
        
        if schedule.get('codeshared'):
            codeshare_info = schedule.get('codeshared', {})
            airline_name = codeshare_info.get('airline', {}).get('name', '')
            flight_num = codeshare_info.get('flight', {}).get('number', '')
            if airline_name and flight_num:
                info += f"Codeshare: {airline_name} {flight_num}\n"
        
        return info
