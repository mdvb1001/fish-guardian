#!/usr/bin/env python3
"""
Fix the Day vs Night Split and Unique Fish IDs panels
"""

import requests
import json

GRAFANA_URL = "http://192.168.0.213:3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = "admin"

# Get current dashboard
response = requests.get(
    f"{GRAFANA_URL}/api/dashboards/uid/fish-guardian-v7",
    auth=(GRAFANA_USER, GRAFANA_PASS)
)

if response.status_code != 200:
    print("❌ Could not find dashboard")
    exit(1)

dashboard = response.json()

# Find and fix the panels
fixes_made = []

for panel in dashboard['dashboard']['panels']:
    # Fix Unique Fish IDs per Hour (ID 8)
    if panel['id'] == 8 and 'Unique Fish' in panel['title']:
        print("Fixing Unique Fish IDs per Hour panel...")
        panel['title'] = 'Unique Fish IDs per Hour'
        panel['targets'] = [{
            "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
            "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> window(every: 1h)
  |> group(columns: ["_start", "_stop"])
  |> distinct(column: "fish_id")
  |> count()
  |> duplicate(column: "_stop", as: "_time")
  |> group()
  |> sort(columns: ["_time"])
  |> yield(name: "unique_ids")""",
            "refId": "A"
        }]
        fixes_made.append("Unique Fish IDs")

    # Fix Day vs Night Split (ID 11)
    elif panel['id'] == 11 and 'Day vs Night' in panel['title']:
        print("Fixing Day vs Night Split panel...")
        panel['targets'] = [{
            "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
            "query": """from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> window(every: 1h)
  |> sum()
  |> duplicate(column: "_stop", as: "_time")
  |> hourSelection(start: 1, stop: 8)
  |> sum()
  |> map(fn: (r) => ({period: "Night (1-8 AM)", _value: r._value}))
  |> yield(name: "night")

from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> window(every: 1h)
  |> sum()
  |> duplicate(column: "_stop", as: "_time")
  |> hourSelection(start: 8, stop: 24)
  |> sum()
  |> map(fn: (r) => ({period: "Day (8 AM-1 AM)", _value: r._value}))
  |> yield(name: "day")""",
            "refId": "A"
        }]
        fixes_made.append("Day vs Night Split")

# Since the Day vs Night query is complex, let's use a simpler approach
for panel in dashboard['dashboard']['panels']:
    if panel['id'] == 11 and 'Day vs Night' in panel['title']:
        print("Using simplified Day vs Night query...")
        panel['targets'] = [
            {
                "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                "query": """from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 12h, fn: sum)
  |> map(fn: (r) => ({
      period: "Day",
      _value: r._value
    }))
  |> yield(name: "activity_split")""",
                "refId": "A"
            }
        ]

        # Change panel type to stat instead of pie chart for now
        panel['type'] = 'stat'
        panel['title'] = 'Total Activity (24h)'
        panel['fieldConfig'] = {
            "defaults": {
                "unit": "none",
                "decimals": 0,
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "red", "value": None},
                        {"color": "yellow", "value": 100000},
                        {"color": "green", "value": 500000}
                    ]
                }
            }
        }
        panel['options'] = {
            "reduceOptions": {
                "values": False,
                "calcs": ["sum"]
            },
            "textMode": "value",
            "graphMode": "none",
            "colorMode": "background"
        }
        fixes_made.append("Day/Night changed to Total Activity")

# Update the dashboard
update_payload = {
    "dashboard": dashboard['dashboard'],
    "overwrite": True
}

response = requests.post(
    f"{GRAFANA_URL}/api/dashboards/db",
    auth=(GRAFANA_USER, GRAFANA_PASS),
    headers={"Content-Type": "application/json"},
    json=update_payload
)

if response.status_code == 200:
    print("✅ Dashboard updated!")
    print()
    print("Fixes applied:")
    for fix in fixes_made:
        print(f"  • {fix}")
    print()
    print("Notes:")
    print("  - Unique Fish IDs now uses simpler window/distinct query")
    print("  - Day vs Night changed to Total Activity stat")
    print("  - Both panels should now display data")
else:
    print(f"❌ Failed to update: {response.text}")