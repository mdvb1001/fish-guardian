#!/usr/bin/env python3
"""
Final fix for System Status panel - Force single value result
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
        print("Found System Status panel, applying final fix...")
        found = True

        # Use the simplest possible query that returns a single value
        panel['targets'] = [{
            "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
            "query": """from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> limit(n: 1)
  |> count()
  |> group()
  |> sum()
  |> map(fn: (r) => ({_value: if r._value > 0 then 1.0 else 0.0}))
  |> yield(name: "status")""",
            "refId": "A"
        }]

        # Update mappings
        panel['fieldConfig']['defaults']['mappings'] = [
            {"type": "value", "value": "null", "text": "❓ Unknown"},
            {"type": "value", "value": "0", "text": "❌ Offline"},
            {"type": "value", "value": "0.0", "text": "❌ Offline"},
            {"type": "value", "value": "1", "text": "✅ Online"},
            {"type": "value", "value": "1.0", "text": "✅ Online"}
        ]

        # Make sure it's configured as a stat panel
        panel['type'] = 'stat'
        panel['options'] = {
            "reduceOptions": {
                "values": False,
                "fields": "",
                "calcs": ["lastNotNull"]
            },
            "textMode": "value",
            "graphMode": "none",
            "orientation": "auto",
            "colorMode": "background"
        }

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
    print("✅ System Status panel FIXED!")
    print()
    print("The fix:")
    print("  • Added group() and sum() to force single result")
    print("  • Maps to 1.0 (Online) or 0.0 (Offline)")
    print("  • Should now display ✅ Online or ❌ Offline")
    print()
    print("Refresh your dashboard to see the status!")
else:
    print(f"❌ Failed to update: {response.text}")