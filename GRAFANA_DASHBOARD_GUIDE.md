# Grafana Dashboard Guide
**Fish Guardian - Activity Monitoring**

## Quick Access

**URL:** http://localhost:3000  
**Username:** admin  
**Password:** admin (or your custom password)

**Dashboard URL:**  
http://localhost:3000/d/fa5750fb-5765-4eed-8fd2-4c3b88e30c46/fish-guardian-activity-monitoring

---

## Dashboard Overview

The Fish Guardian dashboard provides real-time monitoring of your goldfish activity with automatic visual alerts.

### Panel Layout

```
┌─────────────────────────────────┬─────────────────────────────────┐
│  Fish Movement (Distance)       │  Fish Activity Index (%)        │
│  Time series graph              │  Time series graph              │
│  Shows pixels moved per fish    │  Shows % of time active         │
└─────────────────────────────────┴─────────────────────────────────┘
┌──────────────┬──────────────┬──────────────┬────────────────────┐
│ ⚠️ Low       │ 🐠 Active    │ 📊 System    │ Recent Fish        │
│ Activity     │ Fish Count   │ Health       │ Activity Table     │
│ Alert        │              │              │                    │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```

---

## Panel Descriptions

### 1. Fish Movement (Distance)
**Type:** Time series graph  
**Metric:** `distance_px` - Total pixels moved per minute  
**Time Range:** Configurable (default: Last 6 hours)  
**Auto-refresh:** Every 5 seconds

**Color Thresholds:**
- 🔴 **RED** (0-300 px): Very low movement - fish may be sleeping or sick
- 🟡 **YELLOW** (300-1000 px): Low movement - normal resting behavior
- 🟢 **GREEN** (1000+ px): Active swimming

**Query:**
```flux
from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
```

---

### 2. Fish Activity Index (%)
**Type:** Time series graph  
**Metric:** `activity_index` - Percentage of frames with motion (0-100%)  
**Interpretation:** Higher % = more continuous movement

**Color Thresholds:**
- 🔴 **RED** (0-10%): Minimal activity
- 🟡 **YELLOW** (10-20%): Moderate activity
- 🟢 **GREEN** (20%+): High activity

**Query:**
```flux
from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "activity_index")
```

---

### 3. ⚠️ Low Activity Alert
**Type:** Stat panel with background color  
**Purpose:** Visual alert for abnormally low fish activity  
**Time Window:** Last 10 minutes (average)

**Alert Levels:**
- 🔴 **DARK RED** (0-300 px avg): **CRITICAL** - Check fish health immediately
- 🟠 **DARK ORANGE** (300-800 px avg): **WARNING** - Monitor closely
- 🟢 **DARK GREEN** (800+ px avg): **NORMAL** - All systems healthy

**When to Act:**
- **Red background:** Check water quality, temperature, filter function
- **Orange background:** Normal during night/sleep times
- **Green background:** Healthy activity levels

**Query:**
```flux
from(bucket: "fish")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> mean()
```

---

### 4. 🐠 Active Fish Count
**Type:** Stat panel with background color  
**Purpose:** Shows how many unique fish have been detected recently  
**Time Window:** Last 5 minutes

**Alert Levels:**
- 🔴 **DARK RED** (0-2 fish): **CRITICAL** - Most fish not moving
- 🟡 **DARK YELLOW** (3-4 fish): **WARNING** - Some fish inactive
- 🟢 **DARK GREEN** (5+ fish): **NORMAL** - Healthy activity

**Note:** Due to goldfish pausing behavior, this count may fluctuate. Values of 5-15 are normal.

**Query:**
```flux
from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> keep(columns: ["fish_id"])
  |> distinct(column: "fish_id")
  |> count()
```

---

### 5. 📊 System Health
**Type:** Stat panel  
**Purpose:** Monitors if Fish Guardian service is running and logging data  
**Time Window:** Last 2 minutes

**Status:**
- ✅ **"ONLINE"** (GREEN): System receiving data - everything working
- ⚠️ **"NO DATA"** (RED): System stopped or camera issue

**Troubleshooting NO DATA:**
```bash
# Check if service is running
sudo systemctl status fish-guardian

# Restart service
sudo systemctl restart fish-guardian

# View recent logs
sudo journalctl -u fish-guardian -n 50
```

**Query:**
```flux
from(bucket: "fish")
  |> range(start: -2m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> count()
```

---

### 6. Recent Fish Activity Table
**Type:** Table with gradient bars  
**Purpose:** Shows which fish moved most recently and how much  
**Time Window:** Last 1 hour (latest value per fish)

**Columns:**
- **Fish ID:** Unique identifier for each detected fish
- **Distance (px):** Last recorded movement distance
- **Gradient Bar:** Visual representation of movement intensity

**Sorting:** Automatically sorted by distance (most active at top)

**Query:**
```flux
from(bucket: "fish")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group(columns: ["fish_id"])
  |> last()
  |> group()
  |> sort(columns: ["_value"], desc: true)
```

---

## Dashboard Settings

### Time Range Controls
- **Location:** Top-right corner of dashboard
- **Quick Options:** Last 5m, 15m, 1h, 6h, 24h, 7d
- **Custom Range:** Click to set specific start/end times
- **Relative Time:** Use "now-6h to now" syntax

### Auto-Refresh
- **Current Setting:** 5 seconds
- **How to Change:** Click refresh dropdown (⟳) next to time range
- **Options:** Off, 5s, 10s, 30s, 1m, 5m, 15m, 30m, 1h
- **Recommended:** 5-10s for live monitoring, 1m for general use

### Zoom & Pan
- **Zoom In:** Click and drag on any graph
- **Reset Zoom:** Double-click on graph
- **Pan:** Hold Shift + drag

---

## Common Tasks

### Filter to Specific Fish IDs

1. Click **"Edit"** on any panel (three dots → Edit)
2. In the query editor, modify the query:

```flux
from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> filter(fn: (r) => r.fish_id == "10" or r.fish_id == "11" or r.fish_id == "12")
```

3. Click **"Apply"**

### Compare Day vs Night Activity

1. Set time range to **"Last 24 hours"**
2. Look for patterns in the time series graphs
3. Note: Goldfish are diurnal (active during day, rest at night)

### Export Data

1. Click panel three dots (⋮)
2. Select **"Inspect" → "Data"**
3. Click **"Download CSV"**

### Add New Panel

1. Click **"Add"** (+ icon) at top
2. Select **"Visualization"**
3. Choose data source: **InfluxDB-Fish**
4. Write Flux query
5. Select visualization type
6. Click **"Apply"**

---

## Alert Threshold Reference

### Movement Distance (pixels/minute)
- **< 100 px:** Sleeping or very ill
- **100-300 px:** Resting (normal at night)
- **300-800 px:** Light activity (normal during day)
- **800-2000 px:** Active swimming (healthy)
- **2000+ px:** Very active (feeding, playing)

### Activity Index (%)
- **< 5%:** Stationary or sleeping
- **5-15%:** Intermittent movement
- **15-30%:** Normal daytime activity
- **30%+:** High activity (excited, feeding)

### Expected Normal Ranges (Daytime)
- **Distance:** 800-3000 pixels/minute per fish
- **Activity Index:** 15-40%
- **Active Fish Count:** 5-12 fish detected in 5min window

### Expected Normal Ranges (Nighttime)
- **Distance:** 100-500 pixels/minute per fish
- **Activity Index:** 5-15%
- **Active Fish Count:** 2-5 fish detected (most sleeping)

---

## Troubleshooting

### Dashboard Shows "No Data"

**Check 1: Is the service running?**
```bash
sudo systemctl status fish-guardian
```
If stopped:
```bash
sudo systemctl start fish-guardian
```

**Check 2: Is InfluxDB running?**
```bash
systemctl status influxdb
```

**Check 3: Check data exists in InfluxDB**
```bash
cd ~/Development/fish-guardian
source .venv/bin/activate
python3 /tmp/verify_influx_data.py
```

### Panel Shows Error

**Check 1: Test data source**
- Go to **⚙️ Configuration → Data sources**
- Click **InfluxDB-Fish**
- Scroll down and click **"Save & Test"**
- Should show: "datasource is working"

**Check 2: Verify query syntax**
- Edit the panel
- Look for red error messages in query editor
- Common issue: Typo in bucket name or measurement name

### Colors Not Showing Correctly

**Check threshold configuration:**
1. Edit panel
2. Right sidebar → **Field** tab
3. Scroll to **Thresholds**
4. Verify values match documentation above

---

## Data Source Configuration

**Name:** InfluxDB-Fish  
**Type:** InfluxDB  
**URL:** http://localhost:8086  
**Organization:** home  
**Default Bucket:** fish  
**Query Language:** Flux

**Configuration File:**  
`/etc/grafana/provisioning/datasources/influxdb-fish.yml`

---

## Dashboard JSON Location

**Imported via API** - Dashboard is stored in Grafana's database

**To Export:**
1. Click **Dashboard settings** (⚙️ icon at top)
2. Select **"JSON Model"**
3. Click **"Copy to Clipboard"** or **"Save to file"**

**To Re-import:**
1. Click **"+" → Import**
2. Paste JSON or upload file
3. Select **InfluxDB-Fish** as data source
4. Click **"Import"**

---

## Best Practices

### Monitoring Schedule
- **Morning:** Check dashboard for overnight anomalies
- **Evening:** Verify fish were active during the day
- **Weekly:** Review 7-day trends for pattern changes

### Baseline Establishment
- Let system run for **5-7 days** undisturbed
- Note typical daytime/nighttime activity levels
- Document any daily patterns (feeding time spikes, etc.)
- Use this as your "normal" reference

### Alert Response
1. **Red alerts:** Immediate action required
2. **Orange/Yellow alerts:** Monitor for 15-30 minutes
3. **Pattern changes:** Investigate water quality, temperature, recent changes

### Data Retention
- InfluxDB default: Unlimited retention
- Consider adding retention policy after collecting baseline
- Recommended: Keep detailed data for 30 days, downsample older data

---

## Advanced Queries

### Total Movement by Fish (Ranked)
```flux
from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group(columns: ["fish_id"])
  |> sum()
  |> group()
  |> sort(columns: ["_value"], desc: true)
```

### Hourly Average Activity
```flux
from(bucket: "fish")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
```

### Most Active Time of Day
```flux
from(bucket: "fish")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1h, fn: mean)
  |> hourSelection(start: 0, stop: 24)
```

---

**Last Updated:** October 15, 2025  
**Dashboard Version:** 2  
**Guide Version:** 1.0
