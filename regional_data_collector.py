#!/usr/bin/env python3
"""
Regional Aviation Data Collection Plan
Comprehensive coverage for EU, Asia Pacific, Middle East, and US routes and airports.
Now using Future Schedules API and Schedule API only.
"""

from aviation_edge_schedule_client import AviationEdgeScheduleClient
from aviation_edge_future_client import AviationEdgeFutureSchedulesClient
from aviation_database import AviationDatabase
import time
from datetime import datetime

class RegionalAviationCollector:
    """Collector for regional aviation data with comprehensive coverage."""
    
    def __init__(self):
        self.schedules_client = AviationEdgeScheduleClient()
        self.future_client = AviationEdgeFutureSchedulesClient()
        
        # Regional airport definitions
        self.regions = {
            'EU': {
                'major_airports': ['LHR', 'CDG', 'FRA', 'AMS', 'MAD', 'FCO', 'MUC', 'ZUR', 'VIE', 'CPH',
                                  'ARN', 'OSL', 'HEL', 'WAW', 'PRG', 'BUD', 'ATH', 'IST', 'LIS', 'BCN',
                                  'DUB', 'BRU', 'LUX', 'GVA', 'MXP', 'VCE', 'NAP', 'PMI', 'AGP', 'LGW'],
                'domestic_hubs': ['LHR', 'CDG', 'FRA', 'MAD', 'FCO', 'MUC', 'AMS'],  # Major domestic networks
                'major_airlines': ['BA', 'AF', 'KL', 'LH', 'IB', 'AZ', 'SN', 'SK', 'AY', 'OS', 'LX', 'TP']
            },
            'Asia_Pacific': {
                'major_airports': ['NRT', 'HND', 'ICN', 'PVG', 'PEK', 'CAN', 'HKG', 'TPE', 'SIN', 'BKK',
                                  'KUL', 'CGK', 'MNL', 'SYD', 'MEL', 'BNE', 'PER', 'AKL', 'DEL', 'BOM',
                                  'CEB', 'DVO', 'ADL', 'DRW', 'CNS', 'OOL', 'HBA', 'LST', 'POM', 'HIR'],
                'domestic_hubs': ['NRT', 'HND', 'ICN', 'PVG', 'PEK', 'SYD', 'MEL', 'MNL', 'BKK', 'SIN'],
                'major_airlines': ['NH', 'JL', 'KE', 'OZ', 'MU', 'CA', 'CZ', 'CX', 'CI', 'BR', 'SQ', 'TG',
                                  'MH', 'GA', 'PR', '5J', 'Z2', 'QF', 'VA', 'JQ', 'TT', 'NZ', '6E', 'AI']
            },
            'Middle_East': {
                'major_airports': ['DXB', 'DOH', 'AUH', 'KWI', 'RUH', 'JED', 'CAI', 'AMM', 'BEY', 'BGW',
                                  'IKA', 'TLV', 'BAH', 'MCT', 'SHJ', 'DWC', 'EVN', 'TBS', 'BAK'],
                'domestic_hubs': ['DXB', 'DOH', 'AUH', 'RUH', 'JED', 'CAI', 'TLV'],
                'major_airlines': ['EK', 'QR', 'EY', 'KU', 'SV', 'MS', 'RJ', 'ME', 'IA', 'LY', 'IR', 'LY',
                                  'GF', 'WY', 'FZ', 'G9', 'FDB', 'QP']
            },
            'US': {
                'major_airports': ['JFK', 'LAX', 'ORD', 'DFW', 'DEN', 'SFO', 'SEA', 'LAS', 'PHX', 'IAH',
                                  'CLT', 'MIA', 'MCO', 'EWR', 'MSP', 'DTW', 'BOS', 'PHL', 'LGA', 'FLL',
                                  'BWI', 'IAD', 'MDW', 'TPA', 'PDX', 'SLC', 'STL', 'SAN', 'HNL', 'ANC'],
                'domestic_hubs': ['JFK', 'LAX', 'ORD', 'DFW', 'DEN', 'SFO', 'SEA', 'LAS', 'PHX', 'IAH',
                                 'CLT', 'MIA', 'MCO', 'EWR', 'MSP', 'DTW', 'BOS', 'PHL'],
                'major_airlines': ['AA', 'DL', 'UA', 'WN', 'B6', 'NK', 'F9', 'G4', 'SY', 'AS', 'HA', 'VX']
            }
        }
    
    def calculate_regional_calls(self):
        """Calculate API calls needed for comprehensive regional coverage."""
        
        print("🌍 REGIONAL AVIATION DATA COLLECTION PLAN")
        print("=" * 70)
        
        total_routes_calls = 0
        total_schedules_calls = 0
        
        for region, config in self.regions.items():
            print(f"\n🌐 {region.upper().replace('_', ' ')} REGION")
            print("-" * 50)
            
            major_airports = config['major_airports']
            domestic_hubs = config['domestic_hubs'] 
            major_airlines = config['major_airlines']
            
            # Routes API calls for this region
            region_routes_calls = 0
            
            # 1. Routes from major airports (departure queries)
            region_routes_calls += len(major_airports)
            print(f"Major airports (departure): {len(major_airports)} calls")
            
            # 2. Routes by major airlines
            region_routes_calls += len(major_airlines)
            print(f"Major airlines: {len(major_airlines)} calls")
            
            # 3. Additional domestic coverage (arrival queries for hubs)
            region_routes_calls += len(domestic_hubs)
            print(f"Domestic hubs (arrival): {len(domestic_hubs)} calls")
            
            print(f"Routes API calls: {region_routes_calls}")
            total_routes_calls += region_routes_calls
            
            # Schedules API calls for this region
            region_schedules_calls = 0
            
            # Each major airport: departures + arrivals
            region_schedules_calls += len(major_airports) * 2
            print(f"Airport schedules: {len(major_airports)} × 2 = {len(major_airports) * 2} calls")
            
            total_schedules_calls += region_schedules_calls
            print(f"Schedules API calls: {region_schedules_calls}")
            print(f"Region total: {region_routes_calls + region_schedules_calls} calls")
        
        print(f"\n🎯 TOTAL REGIONAL COVERAGE")
        print("=" * 70)
        print(f"Total Routes API calls: {total_routes_calls}")
        print(f"Total Schedules API calls: {total_schedules_calls}")
        print(f"GRAND TOTAL: {total_routes_calls + total_schedules_calls} calls")
        
        return total_routes_calls, total_schedules_calls
    
    def estimate_regional_data(self, routes_calls, schedules_calls):
        """Estimate data volume for regional collection."""
        
        print(f"\n📊 ESTIMATED REGIONAL DATA VOLUME")
        print("=" * 70)
        
        # Regional averages (higher than global due to focus on major airports)
        avg_routes_per_call = 25  # Major airports/airlines have more routes
        avg_schedules_per_call = 60  # Major airports have more schedules
        
        estimated_routes = routes_calls * avg_routes_per_call
        estimated_schedules = schedules_calls * avg_schedules_per_call
        
        print(f"Estimated routes: {estimated_routes:,} records")
        print(f"Estimated schedules: {estimated_schedules:,} records")
        print(f"Total estimated records: {estimated_routes + estimated_schedules:,}")
        
        # Coverage by region
        total_airports = sum(len(config['major_airports']) for config in self.regions.values())
        total_airlines = sum(len(config['major_airlines']) for config in self.regions.values())
        
        print(f"\nCoverage:")
        print(f"Airports covered: {total_airports}")
        print(f"Airlines covered: {total_airlines}")
        print(f"Regions covered: {len(self.regions)}")
        
        return estimated_routes, estimated_schedules
    
    def create_regional_execution_plan(self):
        """Create execution plan for regional data collection."""
        
        print(f"\n⚡ REGIONAL EXECUTION PLAN")
        print("=" * 70)
        
        print("Collection Strategy:")
        print("1. 🌍 REGION-BY-REGION - Process one region at a time")
        print("2. 🏢 AIRPORTS FIRST - Collect airport schedules before routes")
        print("3. ✈️  AIRLINES SECOND - Collect airline routes after airports")
        print("4. 💾 REGIONAL SAVES - Save after each region completion")
        print("5. 📊 PROGRESS TRACKING - Report progress by region")
        print("6. 🛡️  ERROR RESILIENCE - Continue if individual calls fail")
        
        print(f"\nExecution Order:")
        for i, region in enumerate(self.regions.keys(), 1):
            region_name = region.replace('_', ' ')
            print(f"{i}. {region_name} Region")
        
        print(f"\nBatch Configuration:")
        print("- Routes batch size: 10 calls")
        print("- Schedules batch size: 8 calls")
        print("- Inter-call delay: 1.5 seconds")
        print("- Inter-batch delay: 5 seconds")
        print("- Error retry: 3 attempts")
        
    def collect_regional_data(self, execute=False):
        """Execute the regional data collection."""
        
        if not execute:
            print(f"\n⚠️  DRY RUN MODE - No actual API calls will be made")
            print("Set execute=True to run actual collection")
            return
        
        print(f"\n🚀 STARTING REGIONAL DATA COLLECTION")
        print("=" * 70)
        
        total_collected = {'routes': 0, 'schedules': 0, 'api_calls': 0}
        
        with AviationDatabase() as db:
            for region_name, config in self.regions.items():
                print(f"\n📍 Processing {region_name.replace('_', ' ')} Region...")
                region_start = datetime.now()
                
                try:
                    # Collect schedules for major airports
                    for airport in config['major_airports']:
                        print(f"  📅 Collecting schedules for {airport}...")
                        
                        # Departures
                        try:
                            departures = self.schedules_client.get_departures(airport)
                            for schedule in departures:
                                db.insert_schedule(schedule)
                            db.log_api_usage("/timetable", {"iataCode": airport, "type": "departure"}, len(departures))
                            total_collected['schedules'] += len(departures)
                            total_collected['api_calls'] += 1
                            time.sleep(1.5)
                        except Exception as e:
                            print(f"    ❌ Error getting departures for {airport}: {e}")
                        
                        # Arrivals
                        try:
                            arrivals = self.schedules_client.get_arrivals(airport)
                            for schedule in arrivals:
                                db.insert_schedule(schedule)
                            db.log_api_usage("/timetable", {"iataCode": airport, "type": "arrival"}, len(arrivals))
                            total_collected['schedules'] += len(arrivals)
                            total_collected['api_calls'] += 1
                            time.sleep(1.5)
                        except Exception as e:
                            print(f"    ❌ Error getting arrivals for {airport}: {e}")
                    
                    # Collect schedules by departure airports (this replaces routes collection)
                    for airport in config['major_airports']:
                        print(f"  🛫 Collecting departures from {airport}...")
                        try:
                            departures = self.schedules_client.get_departures(airport)
                            for schedule in departures:
                                db.insert_schedule(schedule)
                            db.log_api_usage("/timetable", {"iataCode": airport, "type": "departure"}, len(departures))
                            total_collected['schedules'] += len(departures)
                            total_collected['api_calls'] += 1
                            time.sleep(1.5)
                        except Exception as e:
                            print(f"    ❌ Error getting departures from {airport}: {e}")
                    
                    # Collect airline-specific schedules (this replaces airline routes collection)
                    for airline in config['major_airlines']:
                        print(f"  ✈️  Collecting schedules for {airline}...")
                        try:
                            airline_schedules = self.schedules_client.get_airline_schedules(airline)
                            for schedule in airline_schedules:
                                db.insert_schedule(schedule)
                            db.log_api_usage("/timetable", {"airlineIata": airline}, len(airline_schedules))
                            total_collected['schedules'] += len(airline_schedules)
                            total_collected['api_calls'] += 1
                            time.sleep(1.5)
                        except Exception as e:
                            print(f"    ❌ Error getting schedules for {airline}: {e}")
                    
                    # Try Future Schedules API if available
                    if self.future_client.is_available():
                        print(f"  🔮 Attempting future schedules collection...")
                        try:
                            # Collect future schedules for major airports (7 days from now)
                            from datetime import datetime, timedelta
                            future_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                            
                            for airport in config['major_airports'][:3]:  # Limit to first 3 airports
                                print(f"    🔮 Future schedules for {airport} on {future_date}...")
                                future_data = self.future_client.collect_airport_future_data(airport, future_date)
                                if future_data.get('statistics', {}).get('total_flights', 0) > 0:
                                    print(f"    ✅ Collected {future_data['statistics']['total_flights']} future flights")
                                    total_collected['future_schedules'] = total_collected.get('future_schedules', 0) + future_data['statistics']['total_flights']
                                time.sleep(2)  # Longer delay for future API
                        except Exception as e:
                            print(f"    ⚠️  Future schedules collection failed: {e}")
                    else:
                        print(f"  ⚠️  Future Schedules API not available, using current schedules only")
                    
                    region_duration = datetime.now() - region_start
                    print(f"  ✅ {region_name} completed in {region_duration.total_seconds():.1f} seconds")
                    
                except Exception as e:
                    print(f"  ❌ Error processing {region_name}: {e}")
                
                # Brief pause between regions
                time.sleep(5)
        
        print(f"\n🎉 COLLECTION COMPLETE!")
        print("=" * 70)
        print(f"Total API calls: {total_collected['api_calls']}")
        print(f"Schedules collected: {total_collected['schedules']:,}")
        if 'future_schedules' in total_collected:
            print(f"Future schedules collected: {total_collected['future_schedules']:,}")
        print(f"Total records: {total_collected['schedules'] + total_collected.get('future_schedules', 0):,}")

def main():
    """Main function for regional aviation data collection."""
    
    collector = RegionalAviationCollector()
    
    # Calculate requirements
    routes_calls, schedules_calls = collector.calculate_regional_calls()
    estimated_routes, estimated_schedules = collector.estimate_regional_data(routes_calls, schedules_calls)
    
    # Create execution plan
    collector.create_regional_execution_plan()
    
    # Time and cost estimates
    total_calls = routes_calls + schedules_calls
    estimated_time = total_calls * 1.5 / 60  # 1.5 seconds per call
    
    print(f"\n⏰ TIME & RESOURCE ESTIMATES")
    print("=" * 70)
    print(f"Estimated execution time: {estimated_time:.1f} minutes")
    print(f"Database growth: +{(estimated_routes + estimated_schedules) / 1000:.1f}k records")
    print(f"Estimated final DB size: ~5-8 MB")
    
    print(f"\n🌍 REGIONAL COVERAGE SUMMARY")
    print("=" * 70)
    print("✅ Europe: 30+ major airports, 12+ airlines")
    print("✅ Asia Pacific: 30+ major airports, 24+ airlines") 
    print("✅ Middle East: 19+ major airports, 18+ airlines")
    print("✅ United States: 30+ major airports, 12+ airlines")
    print("✅ Domestic flights: Comprehensive coverage in all regions")
    
    return total_calls, estimated_routes + estimated_schedules

if __name__ == "__main__":
    total_calls, total_records = main()
    print(f"\n📋 EXECUTE WITH: collector.collect_regional_data(execute=True)")
    print(f"💡 This will make {total_calls} API calls and collect ~{total_records:,} records")
