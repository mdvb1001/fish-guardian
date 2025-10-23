# Quick Start: Grafana Dashboard Setup

## 🚀 Getting Started (5 Minutes)

### 1. Access Grafana
Open in your browser: **http://192.168.0.213:3000**

Login:
- Username: `admin`
- Password: `admin` (or your custom password)

---

## 2. Create Your First Dashboard (Step-by-Step)

### Option A: Start with Overview Panel

1. Click **"+"** in left sidebar → **"Dashboard"**
2. Click **"Add visualization"**
3. Select **"InfluxDB"** as data source
4. Switch query language to **"Flux"** (top dropdown)
5. Paste this query:

```flux
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> yield(name: "total_activity")
```

6. Configure panel:
   - Title: "Total Tank Activity (24h)"
   - Panel type: Time series
   - Color: Blue
7. Click **"Apply"**
8. Click **"Save dashboard"** (disk icon top right)
9. Name it: "Fish Guardian - Main Dashboard"

✅ **You now have your first panel!**

---

### Option B: Create Complete Dashboard with Baselines

Follow the same steps but use this query for a more comprehensive view:

```flux
// Actual activity
actual = from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> yield(name: "actual")

// P10 threshold
p10 = from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 168.0 }))
  |> yield(name: "p10_low_threshold")

// Median
median = from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 1334.0 }))
  |> yield(name: "median_baseline")

// P90 threshold
p90 = from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 3530.0 }))
  |> yield(name: "p90_high_threshold")
```

**Panel configuration:**
- Title: "Activity vs Baselines"
- In "Graph styles" section:
  - Set `actual` line to **width 2, blue**
  - Set baselines to **dashed, width 1**
  - `p10_low_threshold`: Yellow
  - `median_baseline`: Green
  - `p90_high_threshold`: Red

---

## 3. Add a Stat Panel (Current Activity)

1. Click **"Add"** → **"Visualization"**
2. Select **"InfluxDB"**, switch to **"Flux"**
3. Paste:

```flux
from(bucket: "fish")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> sum()
```

4. Change visualization type to **"Stat"**
5. Configure:
   - Title: "Activity (Last 10 min)"
   - In "Thresholds" section:
     - Base: Red (0)
     - Add: 168 → Yellow
     - Add: 1334 → Green
     - Add: 3530 → Orange
6. Click **"Apply"**

---

## 4. Add Fish Count Panel

1. Add another visualization
2. Query:

```flux
from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> distinct(column: "fish_id")
  |> count()
```

3. Type: **"Stat"**
4. Title: "Active Fish (Last 5 min)"
5. Thresholds:
   - 0: Red
   - 3: Yellow
   - 5: Green
   - 15: Orange (high churn)

---

## 5. Quick Dashboard Tips

### Arrange Panels
- Drag panels by the title bar to reposition
- Resize by dragging bottom-right corner
- Use **12-column grid** (full width = 12 cols)

### Time Range
- Top-right corner: Click time range to change
- Recommended: "Last 24 hours" or "Last 7 days"
- Auto-refresh: Click refresh icon → Set to "30s" or "1m"

### Save & Share
- **Save:** Disk icon (top right)
- **Share:** Share icon → Get link
- **Export:** Dashboard settings → JSON model

---

## 6. Set Up Your First Alert

1. Go to **"Alerting"** in left sidebar
2. Click **"Alert rules"**
3. Click **"New alert rule"**
4. Name: "Low Tank Activity"
5. Query:

```flux
from(bucket: "fish")
  |> range(start: -20m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum)
  |> mean()
```

6. Condition: **IS BELOW 168**
7. Evaluate every: **1m** for **20m**
8. Add notification:
   - Contact point: (create email/Slack if desired)
   - Message: "⚠️ Low tank activity: {{ $value }}"
9. Click **"Save rule and exit"**

---

## 7. Recommended Dashboard Layout

### Row 1: Stats (Overview)
```
[Activity (10min)] [Fish Count] [Alert Status] [System Up]
     3 cols           3 cols       3 cols        3 cols
```

### Row 2: Main Chart (Full Width)
```
[Activity vs Baselines - 24h view]
            12 cols (full width)
```

### Row 3: Analysis
```
[Day vs Night Activity]  [Top 10 Active Fish]
        6 cols                  6 cols
```

### Row 4: Diagnostics
```
[ID Churn Rate]         [Activity Heatmap - 7d]
     6 cols                    6 cols
```

---

## 8. Troubleshooting

### "No data" in panels
- Check service: `ssh pi-fish 'sudo systemctl status fish-guardian'`
- Verify InfluxDB: `ssh pi-fish 'systemctl status influxdb'`
- Check time range matches your data

### Query errors
- Ensure query language is set to **"Flux"** (not InfluxQL)
- Check bucket name is **"fish"** (lowercase)
- Verify field names: `fish_activity`, `distance_px`

### Slow queries
- Reduce time range (use -6h instead of -7d)
- Use `aggregateWindow` to downsample
- Limit results with `|> limit(n: 1000)`

---

## 9. Next Steps

- ✅ Create basic dashboard (Steps 1-2)
- ✅ Add stat panels (Steps 3-4)
- ✅ Set up first alert (Step 6)
- 📖 Review full queries: `GRAFANA_QUERIES_v1.md`
- 🔧 Customize colors and thresholds
- 🚀 Wait for Phase 2 AI upgrade for stable fish IDs

---

## Quick Reference

**Baseline Values:**
- P10 (Low): 168 px/min
- Median (Normal): 1,334 px/min
- P90 (High): 3,530 px/min

**Access Points:**
- Grafana: http://192.168.0.213:3000
- InfluxDB: http://192.168.0.213:8086

**Full Query Library:**
See `GRAFANA_QUERIES_v1.md` for all 11 queries and configurations

---

**Version:** 1.0
**Last Updated:** October 20, 2025
