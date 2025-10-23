#!/usr/bin/env python3
"""
Fish Guardian - Per-Fish Baseline Computation
Generates median, P10, and P90 activity baselines per fish per hour-of-day
Outputs JSON configuration for dynamic alerting
"""
from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import numpy as np
from collections import defaultdict

load_dotenv('/home/garrygater1234/Development/fish-guardian/.env')
client = InfluxDBClient(url=os.getenv("INFLUX_URL"), token=os.getenv("INFLUX_TOKEN"), org=os.getenv("INFLUX_ORG"))
query_api = client.query_api()

print("=" * 80)
print("FISH GUARDIAN - BASELINE COMPUTATION")
print("=" * 80)

# Check data availability
query_check = """
from(bucket: "fish")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> count()
"""

tables = query_api.query(query_check)
total_records = 0
for table in tables:
    for record in table.records:
        total_records = record.get_value()

print(f"\n1. DATA AVAILABILITY CHECK")
print(f"   Total records (last 7 days): {total_records:,}")

if total_records < 1000:
    print(f"\n⚠️  WARNING: Only {total_records} records found")
    print("   Recommended: 5-7 days of data (~7,000-10,000 records)")
    print("   Continuing anyway, but baselines may not be robust...")
    print()

# Fetch all data for last 7 days
print("\n2. FETCHING DATA FROM INFLUXDB")
query_all = """
from(bucket: "fish")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px" or r._field == "activity_index")
"""

tables = query_api.query(query_all)

# Organize data: {fish_id: {hour: {distance_px: [...], activity_index: [...]}}}
fish_data = defaultdict(lambda: defaultdict(lambda: {'distance_px': [], 'activity_index': []}))

record_count = 0
for table in tables:
    for record in table.records:
        timestamp = record.get_time()
        fish_id = record.values.get('fish_id')
        field = record.get_field()
        value = record.get_value()

        # Convert to local hour (UTC-5 for CDT)
        local_hour = (timestamp.hour - 5) % 24

        fish_data[fish_id][local_hour][field].append(value)
        record_count += 1

print(f"   Processed {record_count:,} records")
print(f"   Unique fish IDs: {len(fish_data)}")

# Compute baselines per fish per hour
print("\n3. COMPUTING PER-FISH HOURLY BASELINES")
baselines = {}

for fish_id, hourly_data in fish_data.items():
    baselines[fish_id] = {}

    for hour in range(24):
        if hour not in hourly_data:
            # No data for this hour, use global median as fallback
            baselines[fish_id][hour] = {
                'distance_px': {'median': None, 'p10': None, 'p90': None, 'count': 0},
                'activity_index': {'median': None, 'p10': None, 'p90': None, 'count': 0}
            }
            continue

        hour_data = hourly_data[hour]

        # Calculate statistics for distance_px
        if hour_data['distance_px']:
            dist_values = np.array(hour_data['distance_px'])
            baselines[fish_id][hour] = {
                'distance_px': {
                    'median': float(np.median(dist_values)),
                    'p10': float(np.percentile(dist_values, 10)),
                    'p90': float(np.percentile(dist_values, 90)),
                    'count': len(dist_values)
                }
            }
        else:
            baselines[fish_id][hour]['distance_px'] = {
                'median': None, 'p10': None, 'p90': None, 'count': 0
            }

        # Calculate statistics for activity_index
        if hour_data['activity_index']:
            activity_values = np.array(hour_data['activity_index'])
            baselines[fish_id][hour]['activity_index'] = {
                'median': float(np.median(activity_values)),
                'p10': float(np.percentile(activity_values, 10)),
                'p90': float(np.percentile(activity_values, 90)),
                'count': len(activity_values)
            }
        else:
            baselines[fish_id][hour]['activity_index'] = {
                'median': None, 'p10': None, 'p90': None, 'count': 0
            }

print("   ✅ Baselines computed for all fish")

# Compute global fallback baselines
print("\n4. COMPUTING GLOBAL FALLBACK BASELINES")
all_distance = []
all_activity = []

for fish_id, hourly_data in fish_data.items():
    for hour, data in hourly_data.items():
        all_distance.extend(data['distance_px'])
        all_activity.extend(data['activity_index'])

global_baselines = {
    'distance_px': {
        'median': float(np.median(all_distance)) if all_distance else 0,
        'p10': float(np.percentile(all_distance, 10)) if all_distance else 0,
        'p90': float(np.percentile(all_distance, 90)) if all_distance else 0
    },
    'activity_index': {
        'median': float(np.median(all_activity)) if all_activity else 0,
        'p10': float(np.percentile(all_activity, 10)) if all_activity else 0,
        'p90': float(np.percentile(all_activity, 90)) if all_activity else 0
    }
}

print(f"   Global distance_px median: {global_baselines['distance_px']['median']:.1f}")
print(f"   Global activity_index median: {global_baselines['activity_index']['median']:.1f}%")

# Create output configuration
output = {
    'generated_at': datetime.utcnow().isoformat() + 'Z',
    'data_range': '7 days',
    'total_records': record_count,
    'unique_fish_ids': len(fish_data),
    'global_baselines': global_baselines,
    'per_fish_baselines': baselines
}

# Save to JSON file
output_file = '/home/garrygater1234/Development/fish-guardian/baselines_v1.json'
with open(output_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n5. OUTPUT SAVED")
print(f"   File: {output_file}")
print(f"   Size: {os.path.getsize(output_file) / 1024:.1f} KB")

# Display sample baselines for a few fish
print("\n6. SAMPLE BASELINES (FIRST 3 FISH)")
print("=" * 80)

sample_fish = list(baselines.keys())[:3]
for fish_id in sample_fish:
    print(f"\n   Fish ID: {fish_id}")
    print("   Hour | Distance (px/min)         | Activity Index (%)")
    print("        | P10    Median    P90      | P10    Median    P90")
    print("   " + "-" * 70)

    for hour in [0, 6, 12, 18]:  # Sample 4 hours
        dist = baselines[fish_id][hour]['distance_px']
        act = baselines[fish_id][hour]['activity_index']

        if dist['median'] is not None and act['median'] is not None:
            print(f"   {hour:2d}:00 | {dist['p10']:6.0f} {dist['median']:6.0f} {dist['p90']:6.0f}    | "
                  f"{act['p10']:5.1f} {act['median']:6.1f} {act['p90']:6.1f}")
        else:
            print(f"   {hour:2d}:00 | No data")

# Generate alert thresholds recommendation
print("\n" + "=" * 80)
print("7. RECOMMENDED ALERT THRESHOLDS")
print("=" * 80)

print("\nDaytime Hours (8 AM - 12 AM):")
print("   Low Activity Alert: < P10 for 2+ consecutive hours")
print("   High Activity Alert: > P90 for 2+ consecutive hours")

print("\nNighttime Hours (1 AM - 7 AM):")
print("   Low Activity Alert: < P10 for 4+ consecutive hours")
print("   Note: Expect very low activity during deep sleep (3-6 AM)")

print("\nPer-Fish Specific:")
print("   Alert if fish deviates > 50% from their personal median")
print("   Compare current hour against that fish's historical hour median")

print("\n✅ BASELINE COMPUTATION COMPLETE")
print("=" * 80)

client.close()
