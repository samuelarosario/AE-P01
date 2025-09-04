#!/usr/bin/env python3
"""
Aviation Edge Comprehensive Data Collection Plan
Calculate API calls needed for complete routes and schedules data.
"""

from aviation_edge_client import AviationEdgeClient
from aviation_edge_schedule_client import AviationEdgeScheduleClient
from aviation_database import AviationDatabase

def analyze_current_data():
    """Analyze current database to plan comprehensive collection."""
    with AviationDatabase() as db:
        cursor = db.conn.cursor()
        
        # Get all unique airports
        cursor.execute('SELECT DISTINCT iata_code FROM airports ORDER BY iata_code')
        all_airports = [row[0] for row in cursor.fetchall()]
        
        # Get airports with existing schedule data
        cursor.execute('SELECT DISTINCT departure_iata FROM flight_schedules WHERE departure_iata IS NOT NULL')
        dep_covered = set(row[0] for row in cursor.fetchall())
        
        cursor.execute('SELECT DISTINCT arrival_iata FROM flight_schedules WHERE arrival_iata IS NOT NULL')
        arr_covered = set(row[0] for row in cursor.fetchall())
        
        # Get routes coverage
        cursor.execute('SELECT DISTINCT departure_iata, arrival_iata FROM routes')
        routes_covered = set(cursor.fetchall())
        
        return {
            'all_airports': all_airports,
            'total_airports': len(all_airports),
            'dep_covered': dep_covered,
            'arr_covered': arr_covered,
            'routes_covered': routes_covered,
            'schedule_coverage': len(dep_covered.union(arr_covered)),
            'route_coverage': len(routes_covered)
        }

def calculate_routes_api_calls(analysis):
    """Calculate API calls needed for comprehensive routes data."""
    
    print("🛫 ROUTES API CALL CALCULATION")
    print("=" * 60)
    
    # Routes API strategies:
    # 1. Query by departure airport for each airport
    # 2. Query by arrival airport for each airport  
    # 3. Query by major airlines
    # 4. General queries without filters
    
    airports = analysis['all_airports']
    major_airports = ['SYD', 'MNL', 'MEL', 'BNE', 'PER', 'ADL', 'DRW', 'CNS', 'OOL', 'HKG', 'SIN', 'BKK', 'NRT', 'ICN', 'PVG']
    major_airlines = ['QF', 'VA', 'JQ', 'TT', '5J', 'PR', 'Z2', 'DG', 'SQ', 'CX', 'MH', 'TG', 'CI', 'BR', 'NH', 'JL']
    
    routes_calls = 0
    
    # Strategy 1: Query routes from major airports (most likely to have data)
    routes_calls += len([apt for apt in major_airports if apt in airports])
    print(f"Major departure airports: {len([apt for apt in major_airports if apt in airports])} calls")
    
    # Strategy 2: Query routes for major airlines
    routes_calls += len(major_airlines)
    print(f"Major airlines: {len(major_airlines)} calls")
    
    # Strategy 3: Sample other airports (every 5th airport to avoid API limits)
    other_airports = [apt for apt in airports if apt not in major_airports]
    sample_airports = other_airports[::5]  # Every 5th airport
    routes_calls += len(sample_airports)
    print(f"Sample other airports: {len(sample_airports)} calls")
    
    print(f"Total Routes API calls: {routes_calls}")
    return routes_calls

def calculate_schedules_api_calls(analysis):
    """Calculate API calls needed for comprehensive schedules data."""
    
    print("\n📅 SCHEDULES API CALL CALCULATION")
    print("=" * 60)
    
    airports = analysis['all_airports']
    dep_covered = analysis['dep_covered']
    arr_covered = analysis['arr_covered']
    
    schedules_calls = 0
    
    # Major international airports (full coverage)
    major_intl = ['SYD', 'MEL', 'BNE', 'PER', 'ADL', 'DRW', 'CNS', 'OOL', 'MNL', 'CEB', 'DVO', 'ILO', 'CRK', 
                  'HKG', 'SIN', 'BKK', 'NRT', 'ICN', 'PVG', 'LAX', 'SFO', 'LHR', 'CDG', 'FRA', 'AMS', 'DXB']
    
    major_intl_in_db = [apt for apt in major_intl if apt in airports]
    
    # Each airport needs 2 calls (departures + arrivals)
    schedules_calls += len(major_intl_in_db) * 2
    print(f"Major international airports: {len(major_intl_in_db)} airports × 2 = {len(major_intl_in_db) * 2} calls")
    
    # Regional airports (sample coverage)
    regional_airports = [apt for apt in airports if apt not in major_intl_in_db]
    # Sample every 3rd regional airport to get good coverage without overwhelming API
    sample_regional = regional_airports[::3]
    schedules_calls += len(sample_regional) * 2
    print(f"Regional airports (sample): {len(sample_regional)} airports × 2 = {len(sample_regional) * 2} calls")
    
    # Uncovered airports from current data
    uncovered_deps = [apt for apt in airports if apt not in dep_covered and apt not in major_intl_in_db and apt not in sample_regional]
    uncovered_arrs = [apt for apt in airports if apt not in arr_covered and apt not in major_intl_in_db and apt not in sample_regional]
    
    # Add departures for uncovered departure airports
    additional_deps = uncovered_deps[:10]  # Limit to 10 to avoid API overload
    schedules_calls += len(additional_deps)
    print(f"Additional departure airports: {len(additional_deps)} calls")
    
    # Add arrivals for uncovered arrival airports  
    additional_arrs = uncovered_arrs[:10]  # Limit to 10 to avoid API overload
    schedules_calls += len(additional_arrs)
    print(f"Additional arrival airports: {len(additional_arrs)} calls")
    
    print(f"Total Schedules API calls: {schedules_calls}")
    return schedules_calls

def estimate_data_volume(routes_calls, schedules_calls):
    """Estimate the volume of data we'll receive."""
    
    print("\n📊 ESTIMATED DATA VOLUME")
    print("=" * 60)
    
    # Based on our current data patterns
    avg_routes_per_call = 15  # Conservative estimate
    avg_schedules_per_call = 45  # Based on current data
    
    estimated_routes = routes_calls * avg_routes_per_call
    estimated_schedules = schedules_calls * avg_schedules_per_call
    
    print(f"Estimated new routes: {estimated_routes:,} records")
    print(f"Estimated new schedules: {estimated_schedules:,} records")
    print(f"Total estimated records: {estimated_routes + estimated_schedules:,}")
    
    # Database size estimation
    current_size_mb = 0.5  # Current DB is ~500KB
    estimated_size_mb = current_size_mb * ((estimated_routes + estimated_schedules) / 1893)
    
    print(f"Estimated database size: {estimated_size_mb:.1f} MB")
    
    return estimated_routes, estimated_schedules

def create_execution_plan():
    """Create a safe execution plan with rate limiting."""
    
    print("\n⚡ EXECUTION PLAN")
    print("=" * 60)
    
    print("Recommended approach:")
    print("1. 🔄 BATCH PROCESSING - Execute in small batches to avoid API rate limits")
    print("2. ⏱️  RATE LIMITING - 1-2 second delay between API calls")
    print("3. 💾 INCREMENTAL SAVES - Save to database after each batch")
    print("4. 📝 PROGRESS TRACKING - Log progress and handle interruptions")
    print("5. 🛡️  ERROR HANDLING - Retry failed calls and continue on errors")
    print("6. 📊 MONITORING - Track API usage and response times")
    
    print("\nBatch sizes:")
    print("- Routes API: 10 calls per batch")
    print("- Schedules API: 5 calls per batch (larger responses)")
    print("- Delay: 2 seconds between calls")
    print("- Save interval: After each batch")

def main():
    """Main function to calculate comprehensive data collection requirements."""
    
    print("Aviation Edge Comprehensive Data Collection Plan")
    print("=" * 60)
    
    try:
        # Analyze current data
        analysis = analyze_current_data()
        
        print(f"📋 CURRENT DATA ANALYSIS")
        print(f"Total airports in database: {analysis['total_airports']}")
        print(f"Airports with schedule coverage: {analysis['schedule_coverage']}")
        print(f"Route pairs covered: {analysis['route_coverage']}")
        print()
        
        # Calculate API calls needed
        routes_calls = calculate_routes_api_calls(analysis)
        schedules_calls = calculate_schedules_api_calls(analysis)
        
        total_calls = routes_calls + schedules_calls
        
        print(f"\n🎯 TOTAL API CALLS REQUIRED")
        print("=" * 60)
        print(f"Routes API calls: {routes_calls}")
        print(f"Schedules API calls: {schedules_calls}")
        print(f"TOTAL API CALLS: {total_calls}")
        
        # Estimate data volume
        est_routes, est_schedules = estimate_data_volume(routes_calls, schedules_calls)
        
        # Create execution plan
        create_execution_plan()
        
        # Time estimates
        print(f"\n⏰ TIME ESTIMATES")
        print("=" * 60)
        print(f"Estimated time: {total_calls * 2 / 60:.1f} minutes ({total_calls} calls × 2 sec)")
        print(f"With batch processing: {total_calls * 3 / 60:.1f} minutes (including saves)")
        
        # Warning
        print(f"\n⚠️  IMPORTANT CONSIDERATIONS")
        print("=" * 60)
        print("1. This will make significant API usage - ensure API limits allow")
        print("2. Some calls may return empty results (normal for smaller airports)")
        print("3. Data will be current snapshot - schedules change frequently")
        print("4. Database will grow significantly in size")
        print("5. Consider running during off-peak hours")
        
        return total_calls, est_routes + est_schedules
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        return 0, 0

if __name__ == "__main__":
    total_calls, total_records = main()
    print(f"\n🔢 SUMMARY: {total_calls} API calls → ~{total_records:,} records")
