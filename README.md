# Aviation Edge API Client

A Python client for querying Aviation Edge API routes data.

## Assistant Instructions

**IMPORTANT**: When working with this project, always ask for confirmation before making any changes, including:
- Editing files
- Running terminal commands
- Installing packages
- Creating new files
- Deleting files
- Making any modifications to the project

**DATABASE SEARCH POLICY**: For all future flight searches, use ONLY the `flight_schedules` table. Do NOT use the `routes` table for flight search operations. This instruction applies to all search scripts and database queries going forward.

**TEMPORARY SCRIPTS POLICY**: All scripts created temporarily for testing, data analysis, or one-time operations should be deleted after successful execution. Only keep production-ready files in the project directory.

## Features

- Query flight routes by departure/arrival airports
- Filter by airline codes
- Search by flight numbers
- Flight schedules and timetable data
- **Future Schedules API support** (when available)
- Secure API key management via environment variables
- Timezone-aware flight search with connecting flights
- Comprehensive database storage and querying

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
from aviation_edge_schedule_client import AviationEdgeScheduleClient
from aviation_edge_future_client import AviationEdgeFutureSchedulesClient

# Routes API
routes_client = AviationEdgeClient()
routes = routes_client.get_routes(departure_iata="OTP")

# Schedules API  
schedule_client = AviationEdgeScheduleClient()
schedules = schedule_client.get_schedules(iata_code="MNL", type="departure")

# Future Schedules API (when available)
future_client = AviationEdgeFutureSchedulesClient()
if future_client.is_available():
    future_routes = future_client.search_future_routes_by_airports("POM", "NRT")
else:
    print("Future Schedules API not available on current plan")
```

## API Clients

### 1. Routes API (`aviation_edge_client.py`)
- Query flight routes between airports
- Filter by airlines and flight numbers
- Get all routes for specific airline

### 2. Schedules API (`aviation_edge_schedule_client.py`) 
- Current flight schedules and timetables
- Departure and arrival information
- Real-time flight status

### 3. Future Schedules API (`aviation_edge_future_client.py`) ⚠️
- **Status**: Endpoint not currently available (404 errors)
- **Purpose**: Recurring flight schedules by weekday
- **Documentation**: See `FUTURE_SCHEDULES_API.md` for details
- **Action Required**: Contact Aviation Edge for endpoint access
