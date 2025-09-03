# Aviation Edge Database Schema Documentation

## Overview
This SQLite database stores comprehensive aviation data from Aviation Edge API endpoints. The schema is optimized for efficient querying of routes, schedules, airlines, and airports with proper indexing and foreign key relationships.

## Database Statistics
- **Total Records**: 2,157
- **API Endpoints**: 2 (/routes, /timetable)
- **Total API Calls**: 7
- **Airlines**: 105 unique carriers
- **Airports**: 154 unique airports

## Schema Design

### 1. Core Entity Tables

#### `airlines` Table
Stores airline information with IATA/ICAO codes.
```sql
- id (INTEGER PRIMARY KEY)
- iata_code (TEXT UNIQUE) - 2-letter IATA code
- icao_code (TEXT UNIQUE) - 3-letter ICAO code  
- name (TEXT) - Full airline name
- created_at/updated_at (TIMESTAMP)
```
**Records**: 105 airlines

#### `airports` Table
Stores airport information with IATA/ICAO codes.
```sql
- id (INTEGER PRIMARY KEY)
- iata_code (TEXT UNIQUE) - 3-letter IATA code
- icao_code (TEXT UNIQUE) - 4-letter ICAO code
- name (TEXT) - Full airport name
- created_at/updated_at (TIMESTAMP)
```
**Records**: 154 airports

### 2. Data Tables

#### `routes` Table
Static route information from /routes endpoint.
```sql
- id (INTEGER PRIMARY KEY)
- airline_iata/icao (TEXT) - Operating airline
- departure_iata/icao (TEXT) - Origin airport
- departure_terminal/time (TEXT) - Departure details
- arrival_iata/icao (TEXT) - Destination airport
- arrival_terminal/time (TEXT) - Arrival details
- flight_number (TEXT) - Flight identifier
- reg_number (TEXT) - Aircraft registrations (comma-separated)
- codeshares (TEXT) - JSON array of codeshare info
- created_at (TIMESTAMP)
```
**Records**: 2 routes (POM ↔ MNL)

#### `flight_schedules` Table
Real-time schedule data from /timetable endpoint.
```sql
- id (INTEGER PRIMARY KEY)
- airline_iata/icao/name (TEXT) - Operating airline
- flight_number (TEXT) - Flight identifier
- departure_iata/icao/terminal (TEXT) - Origin details
- departure_scheduled_time/actual_time (TEXT) - Timing
- arrival_iata/icao/terminal (TEXT) - Destination details
- arrival_scheduled_time/actual_time (TEXT) - Timing
- status (TEXT) - active, landed, scheduled, cancelled, unknown
- flight_type (TEXT) - departure, arrival
- codeshare_airline/flight (TEXT) - Partnership details
- aircraft_registration/gate (TEXT) - Operational details
- delay_minutes (INTEGER) - Delay information
- query_timestamp/created_at (TIMESTAMP)
```
**Records**: 1,891 schedules

### 3. Tracking Tables

#### `api_usage` Table
Tracks API calls for monitoring and analytics.
```sql
- id (INTEGER PRIMARY KEY)
- endpoint (TEXT) - API endpoint used
- query_params (TEXT) - JSON parameters
- response_count (INTEGER) - Records returned
- query_timestamp (TIMESTAMP)
```
**Records**: 7 API calls tracked

## Indexing Strategy

Performance indexes on frequently queried columns:
- `idx_routes_departure` on routes(departure_iata)
- `idx_routes_arrival` on routes(arrival_iata)
- `idx_routes_airline` on routes(airline_iata)
- `idx_schedules_departure` on flight_schedules(departure_iata)
- `idx_schedules_arrival` on flight_schedules(arrival_iata)
- `idx_schedules_airline` on flight_schedules(airline_iata)
- `idx_schedules_status` on flight_schedules(status)
- `idx_schedules_type` on flight_schedules(flight_type)

## Data Insights

### Route Analysis
- **POM-MNL Route**: 2 airlines (Philippine Airlines PR 216, Air Niugini PX 10)
- **Flight Duration**: ~3.5 hours
- **Aircraft**: Multiple registrations tracked per route

### Schedule Analysis
- **Flight Status Distribution**:
  - Active: 702 flights (37%)
  - Scheduled: 590 flights (31%)
  - Landed: 551 flights (29%)
  - Unknown: 36 flights (2%)
  - Cancelled: 12 flights (1%)

- **Peak Times**:
  - Morning (06-11): 665 flights (71%)
  - Afternoon (12-17): 135 flights (14%)
  - Night (00-05): 110 flights (12%)
  - Evening (18-23): 28 flights (3%)

- **Route Types**:
  - International: 689 flights (36%)
  - Domestic Philippines: 616 flights (33%)
  - Domestic Australia: 586 flights (31%)

### Hub Analysis
- **Major Hubs** (>50 movements):
  - SYD: 586 movements (primary hub)
  - MNL: 321 movements (secondary hub)
  - MEL: 102 movements
  - BNE: 66 movements
  - SIN: 56 movements

### Connectivity
- **MNL**: 76 destinations (highest connectivity)
- **SYD**: 69 destinations
- **POM**: 17 destinations

### Codeshare Networks
- **Top Partnerships**:
  - Emirates ↔ Qantas: 43 shared flights
  - Air New Zealand ↔ Qantas: 41 shared flights
  - Malaysia Airlines ↔ Philippine Airlines: 36 shared flights

## Query Examples

### Search Functions
```python
# Find flights by route
db.search_flights(departure_iata="POM", arrival_iata="MNL")

# Find airline operations
db.search_flights(airline_iata="PR")

# Find active flights
db.search_flights(status="active")
```

### Analytics
```python
# Airport traffic summary
db.get_airport_traffic(limit=10)

# Airline activity
db.get_airline_activity(limit=10)

# API usage tracking
db.get_api_usage_summary()
```

## Data Quality Features

1. **Foreign Key Relationships**: Maintain referential integrity
2. **Unique Constraints**: Prevent duplicate airline/airport codes
3. **Automatic Timestamps**: Track data creation and updates
4. **JSON Storage**: Flexible codeshare and parameter data
5. **Index Optimization**: Fast queries on common search patterns
6. **Data Type Handling**: Automatic conversion of arrays to strings

## Future Enhancements

1. **Additional Endpoints**: Aircraft, airlines, airports detail APIs
2. **Historical Tracking**: Time-series analysis capabilities
3. **Data Validation**: Enhanced constraint checking
4. **Partitioning**: Date-based partitioning for large datasets
5. **Views**: Pre-computed analytics views
6. **Triggers**: Automatic data consistency maintenance

This schema provides a solid foundation for aviation data analytics with room for expansion as more API endpoints are integrated.
