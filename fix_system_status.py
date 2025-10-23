#!/usr/bin/env python3
"""
Fix System Status panel in Fish Guardian dashboard
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

# Find and fix the System Status panel (id 4)
for panel in dashboard['dashboard']['panels']:
    if panel['id'] == 4 and panel['title'] == 'System Status':
        print("Found System Status panel, updating query...")

        # Replace with a working query
        panel['targets'] = [{
            "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
            "query": """from(bucket: "fish")
  |> range(start: -2m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> last()
  |> group()
  |> count()
  |> map(fn: (r) => ({_value: if r._value > 0 then 1.0 else 0.0}))
  |> yield(name: "status")""",
            "refId": "A"
        }]

        # Also update the field config
        panel['fieldConfig']['defaults']['mappings'] = [
            {"type": "value", "value": "null", "text": "❓ Unknown"},
            {"type": "value", "value": "0", "text": "❌ Offline"},
            {"type": "value", "value": "1", "text": "✅ Online"}
        ]

        break

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
    print("✅ System Status panel fixed!")
    print("   The panel should now show '✅ Online' when data is flowing")
    print("   and '❌ Offline' when no data for 2+ minutes")
else:
    print(f"❌ Failed to update: {response.text}")