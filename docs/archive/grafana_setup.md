# Grafana Setup Guide for Fish Guardian

## Step 1: Access Grafana
1. Open browser to: http://192.168.0.213:3000
2. Login with default credentials:
   - Username: `admin`
   - Password: `admin` (you'll be prompted to change it)

## Step 2: Add InfluxDB v2 Data Source
1. Click **⚙️ Configuration** → **Data Sources**
2. Click **Add data source**
3. Select **InfluxDB**
4. Configure:
   - **Name**: `Fish InfluxDB`
   - **Query Language**: `Flux`
   - **URL**: `http://localhost:8086`
   - **Access**: `Server (default)`
   - **Organization**: `home`
   - **Token**: `v0jfmkQMYxHCGjs9gNx4ulBRVgIqUdXKSUbRk3yhRgGHwz3DPL9Ffkv3OmB360uMeAx6i87LhUe3m-A1ma6t1w==`
   - **Default Bucket**: `fish`
5. Click **Save & Test** - should see green checkmark

## Step 3: Create Dashboard

### Panel 1: Overview - All Fish Activity
1. Click **+** → **Dashboard** → **Add new panel**
2. In query editor:
```flux
from(bucket: "fish")
  |> range(start: -6h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```
3. Panel settings:
   - **Title**: `Fish Activity Overview`
   - **Visualization**: `Time series`
   - **Legend**: Show
4. Click **Apply**

### Panel 2: Individual Fish - Distance Moved
For each fish, create a panel:
1. Add new panel
2. Query:
```flux
from(bucket: "fish")
  |> range(start: -6h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r.fish_id == "1")  // Change fish_id for each panel
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```
3. Title: `Fish 1 - Distance Moved`

### Panel 3: Activity Index
1. Add new panel
2. Query:
```flux
from(bucket: "fish")
  |> range(start: -6h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "activity_index")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```
3. Title: `Fish Activity Index (%)`
4. Unit: `Percent (0-100)`

### Panel 4: Current Status (Stat)
1. Add new panel
2. Query:
```flux
from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> last()
  |> group()
  |> count()
```
3. Visualization: `Stat`
4. Title: `Active Fish (last 5 min)`

## Step 4: Configure Alerts
1. Click **Alerting** → **Alert rules**
2. Create new alert rule:
   - **Name**: `Fish Inactivity Alert`
   - **Query**: 
```flux
from(bucket: "fish")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> mean()
```
   - **Condition**: When last value is below 10 (adjust as needed)
   - **For**: 10 minutes
3. Add notification channel (email, webhook, etc.)

## Step 5: Save Dashboard
1. Click **💾 Save dashboard** icon
2. Name: `Fish Guardian Monitor`
3. Click **Save**

## Useful Queries

### See all measurements:
```flux
import "influxdata/influxdb/schema"
schema.measurements(bucket: "fish")
```

### See all fish IDs:
```flux
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> keep(columns: ["fish_id"])
  |> distinct(column: "fish_id")
```

### Average activity per fish (last hour):
```flux
from(bucket: "fish")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group(columns: ["fish_id"])
  |> mean()
```
