#!/usr/bin/env python3
"""
Fish Guardian - Fixed Grafana Dashboard Creator
Creates a complete dashboard with properly aggregated queries
"""

import requests
import json
from datetime import datetime

# Grafana configuration
GRAFANA_URL = "http://192.168.0.213:3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = "admin"

# First delete the old dashboard
def delete_old_dashboard():
    """Delete existing dashboard if it exists"""
    try:
        response = requests.get(
            f"{GRAFANA_URL}/api/dashboards/uid/fish-guardian-v1",
            auth=(GRAFANA_USER, GRAFANA_PASS)
        )
        if response.status_code == 200:
            print("Found existing dashboard, deleting...")
            delete_response = requests.delete(
                f"{GRAFANA_URL}/api/dashboards/uid/fish-guardian-v1",
                auth=(GRAFANA_USER, GRAFANA_PASS)
            )
            if delete_response.status_code == 200:
                print("✅ Old dashboard deleted")
    except:
        pass

# Dashboard JSON with fixed queries
dashboard_json = {
    "dashboard": {
        "id": None,
        "uid": "fish-guardian-v1",
        "title": "Fish Guardian - Activity Monitor",
        "tags": ["fish", "monitoring", "aquarium"],
        "timezone": "browser",
        "schemaVersion": 30,
        "version": 1,
        "refresh": "30s",
        "time": {
            "from": "now-24h",
            "to": "now"
        },
        "annotations": {
            "list": [
                {
                    "enable": True,
                    "hide": False,
                    "name": "Lights Schedule",
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> aggregateWindow(every: 1h, fn: count)
  |> map(fn: (r) => ({
      r with
      _value: if (hour(t: r._time) >= 1 and hour(t: r._time) < 8)
              then "🌙 Lights OFF"
              else "💡 Lights ON"
    }))""",
                    "iconColor": "yellow"
                }
            ]
        },
        "panels": [
            # Row 1: Stats Overview
            {
                "id": 1,
                "gridPos": {"h": 5, "w": 6, "x": 0, "y": 0},
                "type": "stat",
                "title": "Current Activity (Last 10 min)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group()
  |> sum()
  |> yield(name: "total_activity")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "red", "value": None},
                                {"color": "red", "value": 0},
                                {"color": "yellow", "value": 1680},  # 168 * 10 minutes
                                {"color": "green", "value": 13340},  # 1334 * 10 minutes
                                {"color": "orange", "value": 35300}  # 3530 * 10 minutes
                            ]
                        },
                        "mappings": [],
                        "unit": "none",
                        "decimals": 0,
                        "displayName": "Total Pixels Moved"
                    }
                },
                "options": {
                    "reduceOptions": {
                        "values": False,
                        "fields": "",
                        "calcs": ["lastNotNull"]
                    },
                    "textMode": "value_and_name",
                    "graphMode": "area",
                    "orientation": "auto",
                    "colorMode": "background"
                }
            },
            {
                "id": 2,
                "gridPos": {"h": 5, "w": 6, "x": 6, "y": 0},
                "type": "stat",
                "title": "Active Fish Count (Last 5 min)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> keep(columns: ["fish_id"])
  |> distinct(column: "fish_id")
  |> count()
  |> yield(name: "unique_fish")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "red", "value": None},
                                {"color": "red", "value": 0},
                                {"color": "yellow", "value": 20},
                                {"color": "green", "value": 40},
                                {"color": "orange", "value": 100}
                            ]
                        },
                        "mappings": [],
                        "unit": "none",
                        "decimals": 0,
                        "displayName": "Unique Fish IDs"
                    }
                },
                "options": {
                    "reduceOptions": {
                        "values": False,
                        "fields": "",
                        "calcs": ["lastNotNull"]
                    },
                    "textMode": "value_and_name",
                    "graphMode": "none",
                    "orientation": "auto",
                    "colorMode": "background"
                }
            },
            {
                "id": 3,
                "gridPos": {"h": 5, "w": 6, "x": 12, "y": 0},
                "type": "gauge",
                "title": "Activity Level",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group()
  |> mean()
  |> yield(name: "avg_per_record")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "red", "value": None},
                                {"color": "red", "value": 0},
                                {"color": "yellow", "value": 168},
                                {"color": "green", "value": 1334},
                                {"color": "orange", "value": 3530}
                            ]
                        },
                        "mappings": [],
                        "unit": "none",
                        "decimals": 0,
                        "displayName": "Avg Activity",
                        "min": 0,
                        "max": 5000
                    }
                },
                "options": {
                    "reduceOptions": {
                        "values": False,
                        "fields": "",
                        "calcs": ["lastNotNull"]
                    },
                    "showThresholdLabels": True,
                    "showThresholdMarkers": True,
                    "orientation": "auto"
                }
            },
            {
                "id": 4,
                "gridPos": {"h": 5, "w": 6, "x": 18, "y": 0},
                "type": "stat",
                "title": "Data Collection Status",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> last()
  |> keep(columns: ["_time"])
  |> map(fn: (r) => ({_value: uint(v: now()) - uint(v: r._time)}))
  |> map(fn: (r) => ({_value: r._value / uint(v: 1000000000)}))
  |> yield(name: "seconds_ago")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "green", "value": None},
                                {"color": "green", "value": 0},
                                {"color": "yellow", "value": 120},
                                {"color": "red", "value": 300}
                            ]
                        },
                        "mappings": [
                            {
                                "type": "range",
                                "options": {
                                    "from": 0,
                                    "to": 60,
                                    "result": {"text": "✅ Live", "color": "green"}
                                }
                            },
                            {
                                "type": "range",
                                "options": {
                                    "from": 60,
                                    "to": 300,
                                    "result": {"text": "⚠️ Delayed", "color": "yellow"}
                                }
                            },
                            {
                                "type": "range",
                                "options": {
                                    "from": 300,
                                    "to": 99999,
                                    "result": {"text": "❌ Offline", "color": "red"}
                                }
                            }
                        ],
                        "unit": "s",
                        "decimals": 0,
                        "displayName": "Last Update"
                    }
                },
                "options": {
                    "reduceOptions": {
                        "values": False,
                        "fields": "",
                        "calcs": ["lastNotNull"]
                    },
                    "textMode": "value_and_name",
                    "graphMode": "none",
                    "orientation": "auto",
                    "colorMode": "background"
                }
            },
            # Row 2: Main Activity Chart with Baselines
            {
                "id": 5,
                "gridPos": {"h": 10, "w": 24, "x": 0, "y": 5},
                "type": "timeseries",
                "title": "Tank Activity vs Baselines (10-min avg)",
                "targets": [
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 10m, fn: sum, createEmpty: false)
  |> yield(name: "Total Activity")""",
                        "refId": "A"
                    },
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 10m, fn: count, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 168.0 * 10.0 }))
  |> yield(name: "P10 Baseline (Low)")""",
                        "refId": "B"
                    },
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 10m, fn: count, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 1334.0 * 10.0 }))
  |> yield(name: "Median (Normal)")""",
                        "refId": "C"
                    },
                    {
                        "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                        "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 10m, fn: count, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 3530.0 * 10.0 }))
  |> yield(name: "P90 Baseline (High)")""",
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
                            "spanNulls": True,
                            "showPoints": "never",
                            "pointSize": 5,
                            "stacking": {
                                "mode": "none"
                            },
                            "axisPlacement": "auto",
                            "axisLabel": "",
                            "scaleDistribution": {
                                "type": "linear"
                            },
                            "hideFrom": {
                                "tooltip": False,
                                "viz": False,
                                "legend": False
                            },
                            "thresholdsStyle": {
                                "mode": "off"
                            }
                        },
                        "unit": "none",
                        "decimals": 0
                    },
                    "overrides": [
                        {
                            "matcher": {"id": "byName", "options": "Total Activity"},
                            "properties": [
                                {"id": "custom.lineWidth", "value": 3},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "blue"}}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "P10 Baseline (Low)"},
                            "properties": [
                                {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [10, 10]}},
                                {"id": "custom.lineWidth", "value": 1},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "yellow"}}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "Median (Normal)"},
                            "properties": [
                                {"id": "custom.lineStyle", "value": {"fill": "dash", "dash": [10, 10]}},
                                {"id": "custom.lineWidth", "value": 1},
                                {"id": "color", "value": {"mode": "fixed", "fixedColor": "green"}}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "P90 Baseline (High)"},
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
            # Row 3: Alert Timeline
            {
                "id": 6,
                "gridPos": {"h": 4, "w": 24, "x": 0, "y": 15},
                "type": "state-timeline",
                "title": "Activity Alert Status",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 10m, fn: sum, createEmpty: false)
  |> map(fn: (r) => ({
      r with
      _value: if r._value < 1680.0 then 2.0
              else if r._value < 13340.0 then 1.0
              else 0.0
    }))
  |> yield(name: "status")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"color": "green", "value": None},
                                {"color": "green", "value": 0},
                                {"color": "yellow", "value": 1},
                                {"color": "red", "value": 2}
                            ]
                        },
                        "mappings": [
                            {"type": "value", "value": "0", "text": "Normal Activity"},
                            {"type": "value", "value": "1", "text": "Low Activity"},
                            {"type": "value", "value": "2", "text": "ALERT: Very Low"}
                        ],
                        "color": {
                            "mode": "thresholds"
                        }
                    }
                },
                "options": {
                    "mergeValues": False,
                    "showValue": "never",
                    "alignValue": "center",
                    "rowHeight": 0.9,
                    "legend": {
                        "displayMode": "hidden",
                        "showLegend": False
                    },
                    "tooltip": {
                        "mode": "single",
                        "sort": "none"
                    }
                }
            },
            # Row 4: Analysis Panels
            {
                "id": 7,
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 19},
                "type": "barchart",
                "title": "Hourly Activity Distribution (Last 24h)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """import "date"
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> map(fn: (r) => ({r with hour: date.hour(t: r._time)}))
  |> group(columns: ["hour"])
  |> sum()
  |> group()
  |> sort(columns: ["hour"])
  |> yield(name: "hourly")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "unit": "none",
                        "color": {
                            "mode": "palette-classic"
                        },
                        "displayName": "Hour ${__field.labels.hour}"
                    }
                },
                "options": {
                    "orientation": "vertical",
                    "groupWidth": 0.7,
                    "barWidth": 0.97,
                    "showValue": "auto",
                    "stacking": "none",
                    "legend": {
                        "showLegend": False
                    },
                    "tooltip": {
                        "mode": "single",
                        "sort": "none"
                    }
                }
            },
            {
                "id": 8,
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 19},
                "type": "timeseries",
                "title": "Fish ID Tracking (Unique IDs per hour)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group(columns: ["_time"])
  |> aggregateWindow(every: 1h, fn: (tables=<-, column) =>
      tables
        |> keep(columns: ["fish_id"])
        |> distinct(column: "fish_id")
        |> count()
    , createEmpty: false)
  |> yield(name: "unique_ids")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "custom": {
                            "drawStyle": "bars",
                            "lineInterpolation": "linear",
                            "barAlignment": 0,
                            "lineWidth": 1,
                            "fillOpacity": 50,
                            "gradientMode": "none",
                            "spanNulls": False,
                            "showPoints": "never"
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
                    },
                    "tooltip": {
                        "mode": "single",
                        "sort": "none"
                    }
                }
            },
            # Row 5: System Stats
            {
                "id": 9,
                "gridPos": {"h": 6, "w": 8, "x": 0, "y": 27},
                "type": "table",
                "title": "Top Active Fish (Last Hour)",
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
  |> limit(n: 10)
  |> map(fn: (r) => ({fish_id: r.fish_id, total_distance: r._value}))
  |> yield(name: "top_fish")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "unit": "none",
                        "decimals": 0
                    },
                    "overrides": [
                        {
                            "matcher": {"id": "byName", "options": "fish_id"},
                            "properties": [
                                {"id": "displayName", "value": "Fish ID"},
                                {"id": "custom.width", "value": 100}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "total_distance"},
                            "properties": [
                                {"id": "displayName", "value": "Total Distance (px)"},
                                {"id": "custom.width", "value": 150}
                            ]
                        }
                    ]
                },
                "options": {
                    "showHeader": True,
                    "footer": {
                        "show": False
                    }
                }
            },
            {
                "id": 10,
                "gridPos": {"h": 6, "w": 8, "x": 8, "y": 27},
                "type": "stat",
                "title": "Records Collected (24h)",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> group()
  |> count()
  |> yield(name: "total_records")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "unit": "none",
                        "decimals": 0,
                        "displayName": "Total Records"
                    }
                },
                "options": {
                    "reduceOptions": {
                        "values": False,
                        "fields": "",
                        "calcs": ["lastNotNull"]
                    },
                    "textMode": "value",
                    "graphMode": "none"
                }
            },
            {
                "id": 11,
                "gridPos": {"h": 6, "w": 8, "x": 16, "y": 27},
                "type": "piechart",
                "title": "Day vs Night Activity Split",
                "targets": [{
                    "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
                    "query": """import "date"
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> map(fn: (r) => ({
      r with
      period: if (date.hour(t: r._time) >= 1 and date.hour(t: r._time) < 8)
              then "Night (1-8 AM)"
              else "Day (8 AM-1 AM)"
    }))
  |> group(columns: ["period"])
  |> sum()
  |> yield(name: "day_night")""",
                    "refId": "A"
                }],
                "fieldConfig": {
                    "defaults": {
                        "unit": "none",
                        "decimals": 0,
                        "color": {
                            "mode": "palette-classic"
                        }
                    }
                },
                "options": {
                    "pieType": "donut",
                    "displayLabels": ["name", "percent"],
                    "legend": {
                        "showLegend": True,
                        "displayMode": "list",
                        "placement": "right",
                        "values": ["value"]
                    },
                    "tooltip": {
                        "mode": "single",
                        "sort": "none"
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

    # Delete old dashboard first
    delete_old_dashboard()

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
    print("FISH GUARDIAN - FIXED DASHBOARD CREATOR")
    print("=" * 80)
    print()
    print(f"Target: {GRAFANA_URL}")
    print(f"Dashboard: Fish Guardian - Activity Monitor")
    print()

    if create_dashboard():
        print()
        print("🎉 DASHBOARD CREATED!")
        print()
        print("Features:")
        print("  ✅ Current activity gauge with thresholds")
        print("  ✅ Active fish counter")
        print("  ✅ Live status indicator")
        print("  ✅ Main activity chart with baseline overlays")
        print("  ✅ Alert timeline showing activity status")
        print("  ✅ Hourly distribution bar chart")
        print("  ✅ Fish ID churn tracking")
        print("  ✅ Top 10 active fish table")
        print("  ✅ Day/Night activity pie chart")
        print()
        print(f"Open in browser: {GRAFANA_URL}")
    else:
        print()
        print("Please check Grafana is running and credentials are correct.")

if __name__ == "__main__":
    main()