import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AviationEdgeClient:
    """Client for Aviation Edge API routes endpoint."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Aviation Edge client.
        
        Args:
            api_key: API key for Aviation Edge. If not provided, will look for 
                    AVIATION_EDGE_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('AVIATION_EDGE_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set AVIATION_EDGE_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://aviation-edge.com/v2/public/routes"
    
    def get_routes(self, 
                   departure_iata: Optional[str] = None,
                   departure_icao: Optional[str] = None,
                   arrival_iata: Optional[str] = None,
                   airline_iata: Optional[str] = None,
                   airline_icao: Optional[str] = None,
                   flight_number: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get flight routes from Aviation Edge API.
        
        Args:
            departure_iata: Three-letter IATA code for departure airport
            departure_icao: Four-letter ICAO code for departure airport
            arrival_iata: Three-letter IATA code for arrival airport
            airline_iata: IATA code of an airline
            airline_icao: ICAO code of an airline
            flight_number: Flight number
            
        Returns:
            List of route dictionaries containing flight information
        """
        params = {'key': self.api_key}
        
        # Add optional parameters
        if departure_iata:
            params['departureIata'] = departure_iata
        if departure_icao:
            params['departureIcao'] = departure_icao
        if arrival_iata:
            params['arrivalIata'] = arrival_iata
        if airline_iata:
            params['airlineIata'] = airline_iata
        if airline_icao:
            params['airlineIcao'] = airline_icao
        if flight_number:
            params['flightNumber'] = flight_number
        
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
    
    def search_routes_by_airports(self, departure: str, arrival: str) -> List[Dict[str, Any]]:
        """
        Search routes between two airports.
        
        Args:
            departure: IATA or ICAO code for departure airport
            arrival: IATA or ICAO code for arrival airport
            
        Returns:
            List of routes between the airports
        """
        # Determine if codes are IATA (3 chars) or ICAO (4 chars)
        if len(departure) == 3:
            departure_param = {'departure_iata': departure}
        else:
            departure_param = {'departure_icao': departure}
            
        if len(arrival) == 3:
            arrival_param = {'arrival_iata': arrival}
        else:
            arrival_param = {'arrival_icao': arrival}
        
        return self.get_routes(**departure_param, **arrival_param)
    
    def get_airline_routes(self, airline_code: str) -> List[Dict[str, Any]]:
        """
        Get all routes for a specific airline.
        
        Args:
            airline_code: IATA or ICAO code for the airline
            
        Returns:
            List of routes for the airline
        """
        if len(airline_code) == 2:
            return self.get_routes(airline_iata=airline_code)
        else:
            return self.get_routes(airline_icao=airline_code)
