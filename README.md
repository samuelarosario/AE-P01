# Aviation Edge API Client

A Python client for querying Aviation Edge API routes data.

## Features

- Query flight routes by departure/arrival airports
- Filter by airline codes
- Search by flight numbers
- Secure API key management via environment variables

## Prerequisites

1. **Install Python**: If Python is not installed, download it from [python.org](https://www.python.org/downloads/) or install from Microsoft Store.

## Setup

1. **Install dependencies**:
```bash
pip install requests python-dotenv
```

2. **API Key Configuration**: The API key is already configured in the `.env` file:
```
AVIATION_EDGE_API_KEY=58b694-b40ef9
```

3. **Test the setup**:
```bash
python test_setup.py
```

4. **Run the application**:
```bash
python main.py
```

## API Parameters

- `departureIata`: Three-letter IATA code for departure airport
- `departureIcao`: Four-letter ICAO code for departure airport
- `arrivalIata`: Three-letter IATA code for arrival airport
- `airlineIata`: IATA code of an airline
- `airlineIcao`: ICAO code of an airline
- `flightNumber`: Flight number

## Example Usage

```python
from aviation_edge_client import AviationEdgeClient

client = AviationEdgeClient()

# Query routes from OTP airport
routes = client.get_routes(departure_iata="OTP")

# Query specific airline routes
routes = client.get_routes(airline_iata="W6")
```
