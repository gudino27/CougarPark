"""
Test all parking lots to ensure API predictions work without errors

This script tests each lot/zone to identify which ones cause 500 errors
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time

API_URL = "http://localhost:5000"

def test_lot(zone_name, datetime_str, duration=2):
    """Test a single lot prediction"""
    try:
        response = requests.post(
            f"{API_URL}/api/parking/recommend",
            json={
                "zone": zone_name,
                "datetime": datetime_str,
                "duration": duration
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "status": "OK",
                "occupancy": data.get('occupancy_prediction'),
                "enforcement": data.get('enforcement_prediction'),
                "error": None
            }
        else:
            return {
                "status": "ERROR",
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

def main():
    print("="*80)
    print("Testing All Parking Lots")
    print("="*80)
    print()

    # Load lot mapping to get all zones
    df = pd.read_csv('data/lot_mapping_enhanced_with_coords.csv')

    # Get unique zones
    zones = df['Zone_Name'].unique()
    zones = sorted([z for z in zones if pd.notna(z)])

    print(f"Found {len(zones)} unique zones to test")
    print()

    # Test datetime: tomorrow at 2 PM
    test_time = datetime.now() + timedelta(days=1)
    test_time = test_time.replace(hour=14, minute=0, second=0, microsecond=0)
    test_datetime = test_time.isoformat()

    print(f"Test datetime: {test_time.strftime('%B %d, %Y at 2:00 PM')}")
    print()
    print("="*80)
    print()

    results = []

    for i, zone in enumerate(zones, 1):
        print(f"[{i}/{len(zones)}] Testing: {zone}...", end=" ")

        result = test_lot(zone, test_datetime)
        result['zone'] = zone
        results.append(result)

        if result['status'] == 'OK':
            print(f"[OK] (Occupancy: {result['occupancy']}, Enforcement: {result['enforcement']})")
        else:
            print(f"[FAILED]")
            print(f"    Error: {result['error']}")

        # Small delay to avoid overwhelming the API
        time.sleep(0.1)

    print()
    print("="*80)
    print("Summary")
    print("="*80)

    successful = [r for r in results if r['status'] == 'OK']
    failed = [r for r in results if r['status'] == 'ERROR']

    print(f"Total zones tested: {len(results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    print()

    if failed:
        print("Failed Zones:")
        print("-" * 80)
        for r in failed:
            print(f"  {r['zone']}")
            print(f"    Error: {r['error'][:100]}")
        print()

        # Save failed zones to file
        failed_df = pd.DataFrame(failed)
        failed_df.to_csv('data/failed_zones_test.csv', index=False)
        print(f"Saved failed zones to: data/failed_zones_test.csv")
    else:
        print("All zones working!")

    print()

    # Save all results
    results_df = pd.DataFrame(results)
    results_df.to_csv('data/all_zones_test_results.csv', index=False)
    print(f"Saved all results to: data/all_zones_test_results.csv")

if __name__ == "__main__":
    main()