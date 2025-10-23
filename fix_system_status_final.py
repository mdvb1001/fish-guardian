#!/usr/bin/env python3
"""
System Status fix - Use simple count and let Grafana reduce it
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

# Find and fix the System Status panel
found = False
for panel in dashboard['dashboard']['panels']:
    if panel['id'] == 4:
        print("Found System Status panel, applying REAL fix...")
        found = True

        # Use simple count query - return all fish_ids
        # Grafana will handle reducing to single value
        panel['targets'] = [{
            "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
            "query": """from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> count()""",
            "refId": "A"
        }]

        # Update field config to handle multiple series
        panel['fieldConfig']['defaults']['mappings'] = [
            {"type": "special", "match": "null", "text": "❌ Offline"},
            {"type": "special", "match": "empty", "text": "❌ Offline"},
            {"type": "range", "from": 1, "to": 999999, "text": "✅ Online"}
        ]

        # Configure panel to SUM all series and show if > 0
        panel['type'] = 'stat'
        panel['options'] = {
            "reduceOptions": {
                "values": False,
                "fields": "",
                "calcs": ["sum"]  # Sum all the fish_id counts
            },
            "textMode": "value_and_name",
            "graphMode": "none",
            "orientation": "auto",
            "colorMode": "background",
            "text": {}
        }

        # Color thresholds
        panel['fieldConfig']['defaults']['thresholds'] = {
            "mode": "absolute",
            "steps": [
                {"color": "red", "value": None},      # null/0 = offline (red)
                {"color": "green", "value": 1}        # >= 1 = online (green)
            ]
        }

        panel['fieldConfig']['defaults']['unit'] = 'none'
        panel['fieldConfig']['defaults']['decimals'] = 0

        break

if not found:
    print("❌ Could not find System Status panel (ID 4)")
    exit(1)

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
    print("✅ System Status panel ACTUALLY FIXED!")
    print()
    print("The fix:")
    print("  • Returns count of records per fish_id (multiple values)")
    print("  • Grafana reduces with SUM to get total activity")
    print("  • If sum >= 1: ✅ Online (green)")
    print("  • If sum = 0 or null: ❌ Offline (red)")
    print()
    print("Refresh your dashboard - it should now show '✅ Online'!")
else:
    print(f"❌ Failed to update: {response.text}")
