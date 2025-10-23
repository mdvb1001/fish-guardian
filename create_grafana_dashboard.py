#!/usr/bin/env python3
"""
Fish Guardian - Automatic Grafana Dashboard Creator
Creates a complete dashboard with all panels and alerts configured
"""

import requests
import json
from datetime import datetime

# Grafana configuration
GRAFANA_URL = "http://192.168.0.213:3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = "admin"  # Change this to your actual password

# Dashboard JSON configuration
dashboard_json = {
    "dashboard": {
        "id": None,
        "uid": "fish-guardian-v1",
        "title": "Fish Guardian - Main Dashboard",
        "tags": ["fish", "monitoring", "aquarium"],
        "timezone": "browser",
        "schemaVersion": 30,
        "version": 1,
        "refresh": "30s",
        "time": {
            "from": "now-24h",
            "to": "now"
        },
        "panels": [
            # Row 1: Stats Overview (4 panels, 3 cols each)
            {
                "id": 1,
                "gridPos": {"h": 4, "w": 3, "x": 0, "y": 0},
                "type": "stat",
                "title": "Activity (10 min)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> sum()""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "red", "value": None},
                                {"color": "yellow", "value": 168},
                                {"color": "green", "value": 1334},
                                {"color": "orange", "value": 3530}
                            ]
                        },
                        "mappings": [],
                        "unit": "none",
                        "decimals": 0
                    }
                }
            },
            {
                "id": 2,
                "gridPos": {"h": 4, "w": 3, "x": 3, "y": 0},
                "type": "stat",
                "title": "Active Fish (5 min)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> distinct(column: "fish_id")
  |> count()""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "red", "value": None},
                                {"color": "yellow", "value": 3},
                                {"color": "green", "value": 5},
                                {"color": "orange", "value": 15}
                            ]
                        },
                        "mappings": [],
                        "unit": "none",
                        "decimals": 0
                    }
                }
            },
            {
                "id": 3,
                "gridPos": {"h": 4, "w": 3, "x": 6, "y": 0},
                "type": "stat",
                "title": "Data Rate (per hour)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> count()""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "red", "value": None},
                                {"color": "yellow", "value": 100},
                                {"color": "green", "value": 200}
                            ]
                        },
                        "mappings": [],
                        "unit": "none",
                        "decimals": 0
                    }
                }
            },
            {
                "id": 4,
                "gridPos": {"h": 4, "w": 3, "x": 9, "y": 0},
                "type": "stat",
                "title": "Last Update",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> last()
  |> keep(columns: ["_time"])""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "unit": "dateTimeFromNow",
                        "mappings": []
                    }
                }
            },
            # Row 2: Main Activity Chart with Baselines (full width)
            {
                "id": 5,
                "gridPos": {"h": 10, "w": 12, "x": 0, "y": 4},
                "type": "timeseries",
                "title": "Tank Activity vs Baselines (10-min avg)",
                "targets": [
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> yield(name: "Activity")""",
                        "refId": "A"
                    },
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 168.0 }))
  |> yield(name: "P10 (Low Threshold)")""",
                        "refId": "B"
                    },
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 1334.0 }))
  |> yield(name: "Median (Normal)")""",
                        "refId": "C"
                    },
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 3530.0 }))
  |> yield(name: "P90 (High Threshold)")""",
                        "refId": "D"
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "custom": {
                            "drawStyle": "line",
                            "lineInterpolation": "linear",
                            "lineWidth": 1,
                            "fillOpacity": 10,
                            "gradientMode": "none",
                            "spanNulls": False,
                            "showPoints": "never",
                            "pointSize": 5,
                            "stacking": {
                                "mode": "none",
                                "group": "A"
                            }
                        },
                        "unit": "none",
                        "decimals": 0
                    },
                    "overrides": [
                        {
                            "matcher": {"id": "byName", "options": "Activity"},
                            "properties": [
                                {"id": "custom.lineWidth", "value": 2},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "P10 (Low Threshold)"},
                            "properties": [
                                {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [5, 5]}},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "yellow"}}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "Median (Normal)"},
                            "properties": [
                                {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [5, 5]}},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "P90 (High Threshold)"},
                            "properties": [
                                {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [5, 5]}},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "red"}}
                            ]
                        }
                    ]
                },
                "options": {
                    "tooltip": {
                        "mode": "multi",
                        "sort": "none"
                    },
                    "legend": {
                        "showLegend": True,
                        "displayMode": "list",
                        "placement": "bottom"
                    }
                }
            },
            # Row 3: Alert Indicators
            {
                "id": 6,
                "gridPos": {"h": 4, "w": 6, "x": 0, "y": 14},
                "type": "state-timeline",
                "title": "Low Activity Alert (< P10)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: if r._value < 168.0 then 1.0 else 0.0 }))""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "green", "value": None},
                                {"color": "red", "value": 0.5}
                            ]
                        },
                        "mappings": [
                            {"type": "value", "value": "0", "text": "Normal"},
                            {"type": "value", "value": "1", "text": "LOW ACTIVITY"}
                        ]
                    }
                }
            },
            {
                "id": 7,
                "gridPos": {"h": 4, "w": 6, "x": 6, "y": 14},
                "type": "state-timeline",
                "title": "Severe Inactivity Alert (< 50 px/min)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 20m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: if r._value < 50.0 then 1.0 else 0.0 }))""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "green", "value": None},
                                {"color": "red", "value": 0.5}
                            ]
                        },
                        "mappings": [
                            {"type": "value", "value": "0", "text": "Active"},
                            {"type": "value", "value": "1", "text": "SEVERE INACTIVITY"}
                        ]
                    }
                }
            },
            # Row 4: Analysis
            {
                "id": 8,
                "gridPos": {"h": 8, "w": 6, "x": 0, "y": 18},
                "type": "barchart",
                "title": "Top 10 Active Fish (Last Hour)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group(columns: ["fish_id"])
  |> sum()
  |> group()
  |> sort(columns: ["_value"], desc: true)
  |> limit(n: 10)""",
                    "refId": "A"
                }],
                "options": {
                    "orientation": "horizontal"
                },
                "fieldConfig": {
                    "defaults": {
                        "unit": "none",
                        "color": {
                            "mode": "palette-classic"
                        }
                    }
                }
            },
            {
                "id": 9,
                "gridPos": {"h": 8, "w": 6, "x": 6, "y": 18},
                "type": "timeseries",
                "title": "Fish ID Churn Rate (IDs per hour)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1h, fn: (tables=<-, column) => tables |> distinct(column: "fish_id") |> count(), createEmpty: false)""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "custom": {
                            "drawStyle": "line",
                            "lineInterpolation": "linear",
                            "lineWidth": 1,
                            "fillOpacity": 10
                        },
                        "unit": "none",
                        "decimals": 0,
                        "color": {
                            "mode": "fixed",
                            "fixedColor": "purple"
                        }
                    }
                },
                "options": {
                    "legend": {
                        "showLegend": False
                    }
                }
            },
            # Row 5: Diagnostics
            {
                "id": 10,
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 26},
                "type": "heatmap",
                "title": "Activity Heatmap (Hour of Day)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)""",
                    "refId": "A"
                }],
                "options": {
                    "calculate": False,
                    "cellGap": 1,
                    "color": {
                        "scheme": "Blues"
                    },
                    "yAxis": {
                        "axisPlacement": "left"
                    }
                },
                "fieldConfig": {
                    "defaults": {
                        "unit": "none"
                    }
                }
            }
        ],
        "templating": {
            "list": [
                {
                    "name": "DS_INFLUXDB",
                    "type": "datasource",
                    "query": "influxdb",
                    "current": {},
                    "hide": 2
                }
            ]
        }
    },
    "overwrite": True,
    "inputs": [
        {
            "name": "DS_INFLUXDB",
            "type": "datasource",
            "pluginId": "influxdb",
            "value": "InfluxDB"
        }
    ]
}

def create_dashboard():
    """Create the dashboard in Grafana"""

    # First, check if Grafana is reachable
    try:
        health_url = f"{GRAFANA_URL}/api/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Grafana is reachable at {GRAFANA_URL}")
        else:
            print(f"⚠️ Grafana returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach Grafana at {GRAFANA_URL}")
        print(f"   Error: {e}")
        return False

    # Create the dashboard
    api_url = f"{GRAFANA_URL}/api/dashboards/db"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            api_url,
            auth=(GRAFANA_USER, GRAFANA_PASS),
            headers=headers,
            json=dashboard_json
        )

        if response.status_code == 200:
            result = response.json()
            dashboard_url = f"{GRAFANA_URL}{result['url']}"
            print(f"✅ Dashboard created successfully!")
            print(f"   URL: {dashboard_url}")
            print(f"   UID: {result['uid']}")
            return True
        else:
            print(f"❌ Failed to create dashboard")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        return False

def main():
    print("=" * 80)
    print("FISH GUARDIAN - GRAFANA DASHBOARD CREATOR")
    print("=" * 80)
    print()
    print(f"Target: {GRAFANA_URL}")
    print(f"Dashboard: Fish Guardian - Main Dashboard")
    print()

    # Check credentials
    print("Note: Using default credentials (admin/admin)")
    print("      Edit script if you changed the password")
    print()

    input("Press Enter to create the dashboard...")

    if create_dashboard():
        print()
        print("🎉 SUCCESS!")
        print(f"   Open your browser to: {GRAFANA_URL}")
        print(f"   Look for: 'Fish Guardian - Main Dashboard'")
        print()
        print("Dashboard includes:")
        print("  • 4 stat panels (current metrics)")
        print("  • Main activity chart with baselines")
        print("  • 2 alert state indicators")
        print("  • Top 10 active fish bar chart")
        print("  • ID churn rate graph")
        print("  • 7-day activity heatmap")
        print()
        print("Next steps:")
        print("  1. Check the dashboard in your browser")
        print("  2. Adjust time range as needed (top right)")
        print("  3. Configure alerts in Grafana UI")
        print("  4. Wait for Phase 2 AI for better fish tracking")
    else:
        print()
        print("Dashboard creation failed. Please check:")
        print("  1. Grafana is running")
        print("  2. Credentials are correct")
        print("  3. InfluxDB datasource exists")

if __name__ == "__main__":
    main()