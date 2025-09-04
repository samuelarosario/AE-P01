#!/usr/bin/env python3
"""
Execute Regional Aviation Data Collection
Run the comprehensive collection with progress tracking.
"""

from regional_data_collector import RegionalAviationCollector
import sys

def main():
    """Execute the regional data collection."""
    
    print("🚀 STARTING COMPREHENSIVE REGIONAL DATA COLLECTION")
    print("=" * 70)
    print("This will collect data for:")
    print("✅ Europe (EU)")
    print("✅ Asia Pacific") 
    print("✅ Middle East")
    print("✅ United States")
    print("✅ Including domestic flights in all regions")
    print()
    print("Expected: 435 API calls, ~18,505 records, ~11 minutes")
    print("=" * 70)
    
    try:
        collector = RegionalAviationCollector()
        
        # Execute the collection
        collector.collect_regional_data(execute=True)
        
        print("\n🎉 COLLECTION COMPLETED SUCCESSFULLY!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during collection: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
