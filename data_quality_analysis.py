#!/usr/bin/env python3
"""
Fish Guardian - Data Quality Analysis
Analyzes collection patterns, gaps, and anomalies in baseline data
"""
from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

load_dotenv('/home/garrygater1234/Development/fish-guardian/.env')
client = InfluxDBClient(url=os.getenv("INFLUX_URL"), token=os.getenv("INFLUX_TOKEN"), org=os.getenv("INFLUX_ORG"))
query_api = client.query_api()

print("=" * 80)
print("FISH GUARDIAN - DATA QUALITY ANALYSIS")
print("=" * 80)

# 1. Overall Collection Statistics
print("\n1. COLLECTION OVERVIEW")
print("-" * 40)

query = """
from(bucket: "fish")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
"""

tables = query_api.query(query)
all_records = []
fish_ids = set()
timestamps = []

for table in tables:
    for record in table.records:
        all_records.append(record)
        fish_ids.add(record.values.get('fish_id'))
        timestamps.append(record.get_time())

if timestamps:
    earliest = min(timestamps)
    latest = max(timestamps)
    duration = (latest - earliest).total_seconds() / 3600  # hours

    print(f"Total Records: {len(all_records):,}")
    print(f"Unique Fish IDs: {len(fish_ids):,}")
    print(f"Data Range: {earliest.strftime('%Y-%m-%d %H:%M')} to {latest.strftime('%Y-%m-%d %H:%M')}")
    print(f"Duration: {duration:.1f} hours ({duration/24:.2f} days)")
    print(f"Average Records/Hour: {len(all_records)/duration:.1f}")

# 2. Hourly Collection Patterns
print("\n2. HOURLY COLLECTION PATTERNS")
print("-" * 40)

hourly_counts = defaultdict(list)
for ts in timestamps:
    hour = ts.hour
    hourly_counts[hour].append(ts)

print("Hour | Records | Avg/Day | Status")
print("-----|---------|---------|--------")

for hour in range(24):
    if hour in hourly_counts:
        count = len(hourly_counts[hour])
        days = duration / 24
        avg_per_day = count / days if days > 0 else 0

        # Determine status
        if 1 <= hour <= 7:
            status = "🌙 Lights OFF"
        else:
            status = "💡 Lights ON"

        print(f"{hour:2d}:00 | {count:7d} | {avg_per_day:7.1f} | {status}")
    else:
        print(f"{hour:2d}:00 |       0 |     0.0 | No data")

# 3. Data Gap Analysis
print("\n3. DATA GAP DETECTION")
print("-" * 40)

if timestamps:
    sorted_timestamps = sorted(timestamps)
    gaps = []

    for i in range(1, len(sorted_timestamps)):
        diff = (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds()
        if diff > 120:  # Gap > 2 minutes
            gaps.append({
                'start': sorted_timestamps[i-1],
                'end': sorted_timestamps[i],
                'duration_min': diff / 60
            })

    if gaps:
        print(f"Found {len(gaps)} gaps > 2 minutes:")
        print("\nTop 10 Longest Gaps:")
        gaps_sorted = sorted(gaps, key=lambda x: x['duration_min'], reverse=True)[:10]

        for i, gap in enumerate(gaps_sorted, 1):
            print(f"{i:2d}. {gap['duration_min']:.1f} min gap: "
                  f"{gap['start'].strftime('%Y-%m-%d %H:%M')} to "
                  f"{gap['end'].strftime('%H:%M')}")
    else:
        print("✅ No significant gaps detected!")

# 4. Fish ID Churn Analysis
print("\n4. FISH ID CHURN ANALYSIS")
print("-" * 40)

# Get fish IDs by hour
query_by_hour = """
from(bucket: "fish")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group(columns: ["fish_id"])
  |> count()
"""

tables = query_api.query(query_by_hour)
fish_id_counts = {}
for table in tables:
    for record in table.records:
        fish_id = record.values.get('fish_id')
        count = record.get_value()
        fish_id_counts[fish_id] = count

# Categorize fish IDs by persistence
persistent = []  # > 100 records
moderate = []    # 10-100 records
transient = []   # < 10 records

for fish_id, count in fish_id_counts.items():
    if count > 100:
        persistent.append((fish_id, count))
    elif count >= 10:
        moderate.append((fish_id, count))
    else:
        transient.append((fish_id, count))

print(f"Persistent IDs (>100 records): {len(persistent)}")
print(f"Moderate IDs (10-100 records): {len(moderate)}")
print(f"Transient IDs (<10 records): {len(transient)} (ghost tracks)")

if persistent:
    print("\nTop 10 Most Persistent Fish IDs:")
    persistent_sorted = sorted(persistent, key=lambda x: x[1], reverse=True)[:10]
    for i, (fish_id, count) in enumerate(persistent_sorted, 1):
        print(f"  {i:2d}. Fish #{fish_id}: {count:,} records")

# 5. Activity Distribution Analysis
print("\n5. ACTIVITY DISTRIBUTION")
print("-" * 40)

query_activity = """
from(bucket: "fish")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
"""

tables = query_api.query(query_activity)
all_distances = []
for table in tables:
    for record in table.records:
        value = record.get_value()
        if value is not None:
            all_distances.append(value)

if all_distances:
    distances_array = np.array(all_distances)

    print(f"Total Activity Measurements: {len(all_distances):,}")
    print(f"Min Distance: {np.min(distances_array):.1f} px/min")
    print(f"Max Distance: {np.max(distances_array):.1f} px/min")
    print(f"Mean Distance: {np.mean(distances_array):.1f} px/min")
    print(f"Median Distance: {np.median(distances_array):.1f} px/min")
    print(f"Std Dev: {np.std(distances_array):.1f} px/min")

    print("\nPercentiles:")
    for p in [10, 25, 50, 75, 90, 95, 99]:
        value = np.percentile(distances_array, p)
        print(f"  P{p:2d}: {value:7.1f} px/min")

# 6. Collection Rate Analysis
print("\n6. COLLECTION RATE BY TIME PERIOD")
print("-" * 40)

# Calculate expected vs actual records
if duration > 0:
    # With MIN_TRACK_AGE=30s, expect ~40% collection rate
    # 7 fish * 60 min/hour * 0.4 = ~168 records/hour expected
    expected_per_hour = 7 * 60 * 0.4
    actual_per_hour = len(all_records) / duration

    print(f"Expected Rate: ~{expected_per_hour:.0f} records/hour (40% with 30s filter)")
    print(f"Actual Rate: {actual_per_hour:.1f} records/hour")
    print(f"Collection Efficiency: {(actual_per_hour/expected_per_hour)*100:.1f}%")

    # Break down by day/night
    day_records = sum(len(hourly_counts[h]) for h in range(24) if h < 1 or h >= 8)
    night_records = sum(len(hourly_counts[h]) for h in range(1, 8))

    print(f"\nDay (8AM-1AM): {day_records:,} records")
    print(f"Night (1AM-8AM): {night_records:,} records")
    print(f"Day/Night Ratio: {day_records/night_records:.2f}x" if night_records > 0 else "N/A")

# 7. Recent Collection Health
print("\n7. LAST 6 HOURS HEALTH CHECK")
print("-" * 40)

query_recent = """
from(bucket: "fish")
  |> range(start: -6h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1h, fn: count)
"""

tables = query_api.query(query_recent)
recent_hours = {}
for table in tables:
    for record in table.records:
        if record.get_value() is not None:
            time = record.get_time()
            hour = time.strftime("%H:00")
            count = record.get_value()
            recent_hours[hour] = count

if recent_hours:
    print("Hour  | Records | Status")
    print("------|---------|--------")
    for hour, count in sorted(recent_hours.items()):
        status = "✅ Normal" if count > 50 else "⚠️ Low" if count > 0 else "❌ None"
        print(f"{hour} |   {count:5d} | {status}")
else:
    print("No recent data found!")

# 8. Anomaly Detection
print("\n8. ANOMALY DETECTION")
print("-" * 40)

anomalies = []

# Check for sudden drops in collection rate
if len(hourly_counts) > 0:
    for hour in range(24):
        if hour in hourly_counts:
            count = len(hourly_counts[hour])
            expected = expected_per_hour * (duration / 24)  # Adjusted for collection duration

            if count < expected * 0.5:  # Less than 50% of expected
                anomalies.append(f"Hour {hour:02d}:00 - Low collection ({count} records, expected ~{expected:.0f})")

# Check for extreme activity values
if all_distances:
    extreme_low = np.percentile(distances_array, 1)
    extreme_high = np.percentile(distances_array, 99)

    extreme_count = sum(1 for d in all_distances if d < extreme_low or d > extreme_high)
    if extreme_count > len(all_distances) * 0.05:  # More than 5% extreme values
        anomalies.append(f"High number of extreme values: {extreme_count} ({extreme_count/len(all_distances)*100:.1f}%)")

if anomalies:
    print("⚠️ Potential Issues Found:")
    for anomaly in anomalies:
        print(f"  - {anomaly}")
else:
    print("✅ No significant anomalies detected!")

print("\n" + "=" * 80)
print("DATA QUALITY REPORT COMPLETE")
print("=" * 80)

# Recommendations
print("\nRECOMMENDATIONS:")
print("-" * 40)

if len(fish_ids) > 5000:
    print("⚠️ High ID churn detected. Current settings acceptable for baseline,")
    print("   but consider AI-based tracking for production.")

if duration < 120:  # Less than 5 days
    remaining = 120 - duration
    print(f"📊 Continue collection for {remaining:.0f} more hours ({remaining/24:.1f} days)")
    print(f"   Target completion: {(datetime.now() + timedelta(hours=remaining)).strftime('%Y-%m-%d %H:%M')}")
else:
    print("✅ Sufficient data collected! Ready to compute baselines.")

if gaps:
    print(f"🔧 {len(gaps)} data gaps detected. Check service stability.")

print("\n" + "=" * 80)

client.close()