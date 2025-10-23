#!/usr/bin/env python3
"""
Fish Guardian - Activity Monitoring v7
Fixes series limit issues and improves aggregation
"""

import requests
import json

# Grafana configuration
GRAFANA_URL = "http://192.168.0.213:3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = "admin"

# Delete old dashboard
def delete_old_dashboard():
    try:
        response = requests.get(
            f"{GRAFANA_URL}/api/dashboards/uid/fish-guardian-v1",
            auth=(GRAFANA_USER, GRAFANA_PASS)
        )
        if response.status_code == 200:
            print("Deleting old dashboard...")
            requests.delete(
                f"{GRAFANA_URL}/api/dashboards/uid/fish-guardian-v1",
                auth=(GRAFANA_USER, GRAFANA_PASS)
            )
            print("✅ Old dashboard deleted")
    except:
        pass

# Dashboard with fixed queries to avoid series limit
dashboard_json = {
    "dashboard": {
        "id": None,
        "uid": "fish-guardian-v7",
        "title": "Fish Guardian - Activity Monitoring (v7)",
        "tags": ["fish", "monitoring", "aquarium", "v7"],
        "timezone": "browser",
        "schemaVersion": 30,
        "version": 1,
        "refresh": "30s",
        "time": {
            "from": "now-24h",
            "to": "now"
        },
        "panels": [
            # Row 1: Stats - These should work fine
            {
                "id": 1,
                "gridPos": {"h": 5, "w": 6, "x": 0, "y": 0},
                "type": "stat",
                "title": "Current Activity (10 min)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group()
  |> sum()""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "red", "value": None},
                                {"color": "yellow", "value": 1680},
                                {"color": "green", "value": 13340},
                                {"color": "orange", "value": 35300}
                            ]
                        },
                        "unit": "none",
                        "decimals": 0,
                        "displayName": "Total Activity"
                    }
                },
                "options": {
                    "reduceOptions": {
                        "values": False,
                        "calcs": ["lastNotNull"]
                    },
                    "textMode": "value_and_name",
                    "graphMode": "area",
                    "colorMode": "background"
                }
            },
            {
                "id": 2,
                "gridPos": {"h": 5, "w": 6, "x": 6, "y": 0},
                "type": "stat",
                "title": "Active Fish (5 min)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group()
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
                                {"color": "yellow", "value": 20},
                                {"color": "green", "value": 40},
                                {"color": "orange", "value": 100}
                            ]
                        },
                        "unit": "none",
                        "decimals": 0
                    }
                }
            },
            {
                "id": 3,
                "gridPos": {"h": 5, "w": 6, "x": 12, "y": 0},
                "type": "gauge",
                "title": "Avg Activity Level",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group()
  |> mean()""",
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
                        "unit": "none",
                        "decimals": 0,
                        "min": 0,
                        "max": 5000
                    }
                }
            },
            {
                "id": 4,
                "gridPos": {"h": 5, "w": 6, "x": 18, "y": 0},
                "type": "stat",
                "title": "System Status",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -2m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> count()
  |> map(fn: (r) => ({_value: if r._value > 0 then 1 else 0}))""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "mappings": [
                            {"type": "value", "value": "0", "text": "❌ Offline"},
                            {"type": "value", "value": "1", "text": "✅ Online"}
                        ],
                        "unit": "none"
                    }
                },
                "options": {
                    "textMode": "value",
                    "colorMode": "background",
                    "graphMode": "none"
                }
            },
            # Row 2: FIXED Activity vs Baselines - Simplified to avoid series issues
            {
                "id": 5,
                "gridPos": {"h": 10, "w": 24, "x": 0, "y": 5},
                "type": "timeseries",
                "title": "Tank Activity vs Baselines (10-min windows)",
                "targets": [
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group(columns: ["_time"])
  |> sum()
  |> group()
  |> aggregateWindow(every: 10m, fn: sum, createEmpty: true)
  |> fill(value: 0.0)
  |> yield(name: "Activity")""",
                        "refId": "A"
                    },
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> limit(n: 1)
  |> aggregateWindow(every: 10m, fn: last, createEmpty: true)
  |> map(fn: (r) => ({r with _value: 1680.0}))
  |> yield(name: "P10 Low")""",
                        "refId": "B"
                    },
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> limit(n: 1)
  |> aggregateWindow(every: 10m, fn: last, createEmpty: true)
  |> map(fn: (r) => ({r with _value: 13340.0}))
  |> yield(name: "Median")""",
                        "refId": "C"
                    },
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> limit(n: 1)
  |> aggregateWindow(every: 10m, fn: last, createEmpty: true)
  |> map(fn: (r) => ({r with _value: 35300.0}))
  |> yield(name: "P90 High")""",
                        "refId": "D"
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "custom": {
                            "drawStyle": "line",
                            "lineInterpolation": "smooth",
                            "lineWidth": 2,
                            "fillOpacity": 10,
                            "gradientMode": "opacity",
                            "spanNulls": False,
                            "showPoints": "never"
                        },
                        "unit": "none",
                        "decimals": 0
                    },
                    "overrides": [
                        {
                            "matcher": {"id": "byName", "options": "Activity"},
                            "properties": [
                                {"id": "custom.lineWidth", "value": 3},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "P10 Low"},
                            "properties": [
                                {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [10, 10]}},
                                {"id": "custom.lineWidth", "value": 1},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "yellow"}}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "Median"},
                            "properties": [
                                {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [10, 10]}},
                                {"id": "custom.lineWidth", "value": 1},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "P90 High"},
                            "properties": [
                                {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [10, 10]}},
                                {"id": "custom.lineWidth", "value": 1},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "red"}}
                            ]
                        }
                    ]
                },
                "options": {
                    "tooltip": {
                        "mode": "multi",
                        "sort": "desc"
                    },
                    "legend": {
                        "showLegend": True,
                        "displayMode": "table",
                        "placement": "right",
                        "calcs": ["min", "mean", "max"]
                    }
                }
            },
            # Row 3: FIXED Alert Timeline - Single aggregated series
            {
                "id": 6,
                "gridPos": {"h": 4, "w": 24, "x": 0, "y": 15},
                "type": "timeseries",
                "title": "Activity Status (Green=Normal, Yellow=Low, Red=Very Low)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group(columns: ["_time"])
  |> sum()
  |> group()
  |> aggregateWindow(every: 10m, fn: sum, createEmpty: false)
  |> map(fn: (r) => ({
      r with
      _value: if r._value < 1680.0 then 0.0
              else if r._value < 13340.0 then 50.0
              else 100.0
    }))
  |> yield(name: "Status")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "custom": {
                            "drawStyle": "line",
                            "lineInterpolation": "stepAfter",
                            "lineWidth": 2,
                            "fillOpacity": 50,
                            "gradientMode": "none",
                            "spanNulls": True,
                            "showPoints": "never"
                        },
                        "unit": "percent",
                        "min": 0,
                        "max": 100,
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "red", "value": None},
                                {"color": "red", "value": 0},
                                {"color": "yellow", "value": 25},
                                {"color": "green", "value": 75}
                            ]
                        }
                    }
                },
                "options": {
                    "legend": {
                        "showLegend": False
                    },
                    "tooltip": {
                        "mode": "single"
                    }
                }
            },
            # Row 4: Hourly stats and ID tracking
            {
                "id": 7,
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 19},
                "type": "barchart",
                "title": "Activity by Hour (Last 24h)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)
  |> group()
  |> yield(name: "hourly")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "unit": "none",
                        "color": {
                            "mode": "palette-classic"
                        }
                    }
                },
                "options": {
                    "orientation": "vertical"
                }
            },
            # FIXED Fish ID Tracking - Aggregated to single series
            {
                "id": 8,
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 19},
                "type": "timeseries",
                "title": "Unique Fish IDs per Hour",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> keep(columns: ["_time", "fish_id"])
  |> group(columns: ["_time"])
  |> unique(column: "fish_id")
  |> group(columns: ["_time"])
  |> count()
  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)
  |> yield(name: "unique_ids")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "custom": {
                            "drawStyle": "bars",
                            "barAlignment": 0,
                            "fillOpacity": 50
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
            # Row 5: Summary stats
            {
                "id": 9,
                "gridPos": {"h": 6, "w": 8, "x": 0, "y": 27},
                "type": "stat",
                "title": "Records Today",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: today())
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> group()
  |> count()""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "unit": "none",
                        "decimals": 0
                    }
                }
            },
            {
                "id": 10,
                "gridPos": {"h": 6, "w": 8, "x": 8, "y": 27},
                "type": "stat",
                "title": "Avg Distance per Fish",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group()
  |> mean()""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "unit": "none",
                        "decimals": 0
                    }
                }
            },
            {
                "id": 11,
                "gridPos": {"h": 6, "w": 8, "x": 16, "y": 27},
                "type": "piechart",
                "title": "Day vs Night Split",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """import "date"
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> map(fn: (r) => ({
      r with
      period: if date.hour(t: r._time) >= 1 and date.hour(t: r._time) < 8 then "Night" else "Day"
    }))
  |> group(columns: ["period"])
  |> sum()
  |> group()""",
                    "refId": "A"
                }],
                "options": {
                    "pieType": "donut"
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

    # Delete old dashboard
    delete_old_dashboard()

    # Also try to delete v7 if it exists
    try:
        requests.delete(
            f"{GRAFANA_URL}/api/dashboards/uid/fish-guardian-v7",
            auth=(GRAFANA_USER, GRAFANA_PASS)
        )
    except:
        pass

    # Create the new dashboard
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
    print("FISH GUARDIAN - ACTIVITY MONITORING v7")
    print("=" * 80)
    print()
    print("Fixes:")
    print("  • Renamed to 'Fish Guardian - Activity Monitoring v7'")
    print("  • Fixed series limit on Activity Alert panel")
    print("  • Fixed series limit on Fish ID Tracking")
    print("  • Fixed Activity vs Baselines loading issue")
    print("  • Simplified aggregation queries")
    print()

    if create_dashboard():
        print()
        print("🎉 DASHBOARD v7 DEPLOYED!")
        print()
        print("Key improvements:")
        print("  ✅ All queries now properly aggregated (no series explosion)")
        print("  ✅ Activity chart should load properly")
        print("  ✅ Alert status shown as single timeline")
        print("  ✅ Fish ID tracking aggregated by hour")
        print()
        print(f"Open in browser: {GRAFANA_URL}")
        print()
        print("All panels should now work without series limit errors!")
    else:
        print()
        print("Please check Grafana is running and try again.")

if __name__ == "__main__":
    main()
