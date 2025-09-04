# Aviation Edge Future Schedules API Client

## Overview

This module provides a Python client for the Aviation Edge Future Schedules API endpoint (`/flightsFuture`). The Future Schedules API is designed to provide recurring flight schedule information organized by weekdays, allowing you to query future flight patterns rather than specific dated flights.

## API Endpoint Status ⚠️

**IMPORTANT**: During implementation and testing, the `/flightsFuture` endpoint returned 404 errors, indicating:

1. **Endpoint may not be available** on the current API plan
2. **Premium subscription** may be required
3. **Endpoint may be inactive** or under development
4. **Documentation may be outdated**

The client is fully implemented based on the API documentation but cannot be tested until the endpoint becomes available.

## Features

### Core Functionality

The `AviationEdgeFutureSchedulesClient` provides the following methods:

#### Basic Queries
- `get_future_schedules()` - Raw API query with all parameters
- `search_future_routes_by_airports()` - Find routes between two airports  
- `get_airline_future_schedules()` - Get all schedules for an airline
- `get_airport_future_departures()` - Get departures from an airport
- `get_airport_future_arrivals()` - Get arrivals to an airport

#### Weekday-Specific Queries
- `get_weekday_schedules()` - Get schedules for specific weekdays
- Weekday numbers: 1=Monday, 2=Tuesday, ..., 7=Sunday

#### Flight-Specific Queries
- `get_flight_future_schedule()` - Get schedule for specific flight number

### API Parameters

The Future Schedules API supports these parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `departureIata` | string | 3-letter departure airport code |
| `departureIcao` | string | 4-letter departure airport code |
| `arrivalIata` | string | 3-letter arrival airport code |
| `arrivalIcao` | string | 4-letter arrival airport code |
| `airlineIata` | string | 2-letter airline code |
| `airlineIcao` | string | 3-letter airline code |
| `flightNumber` | string | Flight number |
| `weekday` | integer | Weekday (1-7) |

### Response Schema

According to the API documentation, responses contain:

```json
{
  "weekday": {
    "number": 1,
    "name": "Monday"
  },
  "departure": {
    "iataCode": "POM",
    "icaoCode": "AYPY", 
    "scheduledTime": "06:00"
  },
  "arrival": {
    "iataCode": "NRT",
    "icaoCode": "RJAA",
    "scheduledTime": "15:30"
  },
  "aircraft": {
    "modelText": "Boeing 737-800"
  },
  "airline": {
    "iataCode": "PR",
    "icaoCode": "PAL",
    "name": "Philippine Airlines"
  },
  "flight": {
    "number": "101"
  },
  "codeshared": {
    "airline": "...",
    "flight": "..."
  }
}
```

## Usage Examples

### Basic Usage

```python
from aviation_edge_future_client import AviationEdgeFutureSchedulesClient

# Initialize client
client = AviationEdgeFutureSchedulesClient()

# Check if endpoint is available
if not client.is_available():
    print("Future Schedules API is not available")
    exit()

# Get future routes between airports
routes = client.search_future_routes_by_airports("POM", "NRT")
print(f"Found {len(routes)} future schedule entries")
```

### Weekday-Specific Queries

```python
# Get Monday departures from Manila
monday_departures = client.get_airport_future_departures("MNL", weekday=1)

# Get Friday schedules for Philippine Airlines  
pr_friday = client.get_airline_future_schedules("PR", weekday=5)

# Get Sunday arrivals to Tokyo
sunday_arrivals = client.get_airport_future_arrivals("NRT", weekday=7)
```

### Airline and Flight Queries

```python
# Get all Philippine Airlines future schedules
pr_schedules = client.get_airline_future_schedules("PR")

# Get specific flight schedule
pr101_schedule = client.get_flight_future_schedule("PR", "101")
```

## Implementation Details

### Error Handling

The client includes comprehensive error handling:

- **404 errors**: Indicates endpoint not available
- **401/403 errors**: Authentication/authorization issues  
- **Network errors**: Connection timeouts and failures
- **JSON parsing errors**: Malformed response handling

### Endpoint Availability Check

The client automatically tests endpoint availability during initialization:

```python
client = AviationEdgeFutureSchedulesClient()
if client.is_available():
    # Proceed with API calls
    pass
else:
    # Handle unavailable endpoint
    pass
```

### Automatic Code Detection

The client automatically detects IATA vs ICAO codes:
- **3 characters**: Treated as IATA code
- **4 characters**: Treated as ICAO code  
- **2 characters**: Treated as airline IATA code
- **3+ characters**: Treated as airline ICAO code

## Testing

Use the provided test script to verify functionality:

```bash
python test_future_schedules.py
```

The test script includes:
1. Airport-to-airport route queries
2. Weekday-specific departures
3. Airline schedule queries
4. Airport arrival queries
5. Specific flight schedule queries

## Current Status

✅ **Implemented**: Full client with all documented features  
❌ **Endpoint**: Not available (404 errors)  
⚠️ **Action Required**: Contact Aviation Edge support for endpoint access

## Alternative Solutions

While waiting for Future Schedules API access, consider:

1. **Current Schedules API** (`/timetable`) - Available and working
2. **Routes API** (`/routes`) - Provides route information without schedules
3. **Database Analysis** - Pattern analysis of existing schedule data

## Support

For Future Schedules API access:
1. Contact Aviation Edge support
2. Verify API plan includes this endpoint
3. Check for premium subscription requirements
4. Confirm endpoint is currently active

## Files

- `aviation_edge_future_client.py` - Main client implementation
- `test_future_schedules.py` - Comprehensive test suite
- `test_endpoints.py` - Endpoint availability testing
- `FUTURE_SCHEDULES_API.md` - This documentation
