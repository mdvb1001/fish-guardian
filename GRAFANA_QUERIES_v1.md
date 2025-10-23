# Fish Guardian - Grafana Dashboard Queries v1.0

**Generated:** October 20, 2025
**Based on:** baselines_v1.json (90,304 records, 5.85 days)

---

## Dashboard Overview

This dashboard provides:
1. **Tank-Wide Activity** - Total population monitoring
2. **Baseline Overlays** - P10/Median/P90 bands
3. **Alert Indicators** - Visual warnings for anomalies
4. **Day/Night Analysis** - Light cycle awareness
5. **Individual Fish Tracking** - Top active fish

---

## 1. Tank-Wide Activity (Main Panel)

### Query 1A: Total Activity (Last 24h)
```flux
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> yield(name: "total_activity")
```

**Panel Settings:**
- Type: Time series
- Title: "Total Tank Activity (All Fish)"
- Y-axis: "Distance (pixels/min)"
- Unit: none
- Color: Blue gradient

### Query 1B: Fish Count Per Minute
```flux
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: count, createEmpty: false)
  |> yield(name: "fish_count")
```

**Panel Settings:**
- Type: Time series
- Title: "Active Fish Count"
- Y-axis: "Number of Fish"
- Color: Green
- Expected: 7 fish (may vary due to ID churn)

---

## 2. Baseline Overlay Panels

### Query 2A: Activity with P10/P90 Bands
```flux
// Actual activity (10-min smoothed)
actual = from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> yield(name: "actual")

// Global P10 baseline (constant)
p10 = from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 168.0 }))
  |> yield(name: "p10_threshold")

// Global Median baseline
median = from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 1334.0 }))
  |> yield(name: "median_baseline")

// Global P90 baseline
p90 = from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({ r with _value: 3530.0 }))
  |> yield(name: "p90_threshold")
```

**Panel Settings:**
- Type: Time series
- Title: "Activity vs Baselines (10-min avg)"
- Series overrides:
  - `actual`: Line (blue, width 2)
  - `median_baseline`: Dashed line (green, width 1)
  - `p10_threshold`: Dashed line (yellow, width 1)
  - `p90_threshold`: Dashed line (red, width 1)
- Fill: Between P10 and P90 (opacity 0.1)

---

## 3. Alert Detection Panels

### Query 3A: Low Activity Alert (Below P10 for 10+ min)
```flux
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({
      r with
      _value: if r._value < 168.0 then 1.0 else 0.0
    }))
  |> yield(name: "low_activity_alert")
```

**Panel Settings:**
- Type: State timeline
- Title: "Low Activity Alert"
- Thresholds:
  - 0: Green ("Normal")
  - 1: Red ("Alert: Activity Below P10")

### Query 3B: Severe Inactivity (Near Zero for 20+ min)
```flux
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 20m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({
      r with
      _value: if r._value < 50.0 then 1.0 else 0.0
    }))
  |> yield(name: "severe_inactivity")
```

**Panel Settings:**
- Type: State timeline
- Title: "Severe Inactivity Warning"
- Thresholds:
  - 0: Green ("Active")
  - 1: Red ("ALERT: Near-zero activity")

---

## 4. Day/Night Analysis

### Query 4A: Activity by Hour-of-Day (Heatmap)
```flux
from(bucket: "fish")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)
  |> yield(name: "hourly_activity")
```

**Panel Settings:**
- Type: Heatmap
- Title: "Activity Heatmap (7 days)"
- Color scheme: Blue-Yellow-Red
- Expected pattern: Higher during day (8 AM - 12 AM), lower at night (1 AM - 7 AM)

### Query 4B: Day vs Night Comparison
```flux
import "date"

// Daytime (8 AM - 12 AM)
daytime = from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> filter(fn: (r) => {
      hour = date.hour(t: r._time)
      return hour >= 8 or hour == 0
    })
  |> aggregateWindow(every: 10m, fn: sum, createEmpty: false)
  |> yield(name: "daytime")

// Nighttime (1 AM - 7 AM)
nighttime = from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> filter(fn: (r) => {
      hour = date.hour(t: r._time)
      return hour >= 1 and hour < 8
    })
  |> aggregateWindow(every: 10m, fn: sum, createEmpty: false)
  |> yield(name: "nighttime")
```

**Panel Settings:**
- Type: Time series
- Title: "Day vs Night Activity"
- Series colors:
  - Daytime: Yellow
  - Nighttime: Blue
- Expected: ~2.7x daytime ratio

---

## 5. Individual Fish Tracking

### Query 5A: Top 10 Most Active Fish (Last Hour)
```flux
from(bucket: "fish")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> group(columns: ["fish_id"])
  |> sum()
  |> group()
  |> sort(columns: ["_value"], desc: true)
  |> limit(n: 10)
  |> yield(name: "top_active")
```

**Panel Settings:**
- Type: Bar chart (horizontal)
- Title: "Top 10 Most Active Fish (Last Hour)"
- X-axis: "Distance (px)"
- Color: Gradient

### Query 5B: Fish ID Churn Rate
```flux
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1h, fn: (tables=<-, column) =>
      tables |> distinct(column: "fish_id") |> count()
    , createEmpty: false)
  |> yield(name: "unique_ids_per_hour")
```

**Panel Settings:**
- Type: Time series
- Title: "Unique Fish IDs Per Hour (Churn Indicator)"
- Y-axis: "Count"
- Expected: ~60-100/hour (high due to motion-based tracking)
- Note: Should drop to ~7-10/hour after Phase 2 AI upgrade

---

## 6. Statistics Panels

### Query 6A: Current Activity (Stat Panel)
```flux
from(bucket: "fish")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> sum()
  |> yield(name: "current")
```

**Panel Settings:**
- Type: Stat
- Title: "Activity (Last 10 min)"
- Unit: none
- Thresholds:
  - < 168: Red (below P10)
  - 168-1334: Yellow (below median)
  - 1334-3530: Green (normal)
  - > 3530: Orange (above P90)

### Query 6B: Active Fish Count (Stat Panel)
```flux
from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> distinct(column: "fish_id")
  |> count()
  |> yield(name: "active_count")
```

**Panel Settings:**
- Type: Stat
- Title: "Active Fish (Last 5 min)"
- Unit: none
- Thresholds:
  - < 3: Red (too few)
  - 3-5: Yellow (some missing)
  - 5-15: Green (normal range)
  - > 15: Orange (high churn)

---

## 7. Alert Rules (Grafana Alerts)

### Alert 1: Low Tank Activity
**Name:** Low Tank Activity Alert
**Condition:** Tank-wide activity below P10 (168 px/min) for 20+ minutes

**Query:**
```flux
from(bucket: "fish")
  |> range(start: -20m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum)
  |> mean()
  |> yield(name: "mean_activity")
```

**Threshold:** < 168
**Evaluation:** Every 1m for 20m
**Action:** Send notification
**Message:** "⚠️ Low tank activity detected: {value} px/min (threshold: 168)"

---

### Alert 2: Severe Inactivity
**Name:** Severe Inactivity Alert
**Condition:** Near-zero activity (< 50 px/min) for 30+ minutes

**Query:**
```flux
from(bucket: "fish")
  |> range(start: -30m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> filter(fn: (r) => r._field == "distance_px")
  |> aggregateWindow(every: 1m, fn: sum)
  |> mean()
```

**Threshold:** < 50
**Evaluation:** Every 1m for 30m
**Suppression:** During night hours (2 AM - 6 AM)
**Action:** Send notification
**Message:** "🚨 SEVERE: Tank activity nearly zero for 30+ min: {value} px/min"

---

### Alert 3: Data Collection Gap
**Name:** Data Collection Gap
**Condition:** No data received for 5+ minutes

**Query:**
```flux
from(bucket: "fish")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> count()
```

**Threshold:** == 0
**Evaluation:** Every 1m
**Action:** Send notification
**Message:** "⚠️ No data from fish-guardian service for 5+ minutes. Check system status."

---

## 8. Dashboard Layout Recommendation

### Row 1: Overview Stats
- Panel 1: Current Activity (Stat) - 3 cols
- Panel 2: Active Fish Count (Stat) - 3 cols
- Panel 3: System Status (Stat) - 3 cols
- Panel 4: Alert Indicator (State) - 3 cols

### Row 2: Main Activity Chart
- Panel 5: Activity vs Baselines (Time series) - 12 cols, full width

### Row 3: Alert Indicators
- Panel 6: Low Activity Alert (State timeline) - 6 cols
- Panel 7: Severe Inactivity (State timeline) - 6 cols

### Row 4: Analysis
- Panel 8: Day vs Night Activity (Time series) - 6 cols
- Panel 9: Top 10 Active Fish (Bar chart) - 6 cols

### Row 5: Diagnostics
- Panel 10: Fish ID Churn Rate (Time series) - 6 cols
- Panel 11: Activity Heatmap (Heatmap) - 6 cols

---

## 9. Using These Queries in Grafana

### Step 1: Access Grafana
1. Open browser: http://192.168.0.213:3000
2. Login (default: admin/admin)

### Step 2: Create Dashboard
1. Click "+" → "Dashboard"
2. Click "Add visualization"
3. Select "InfluxDB" data source
4. Switch to "Flux" query language

### Step 3: Add Panels
1. Copy queries from above
2. Configure panel settings as specified
3. Adjust time ranges as needed
4. Save dashboard

### Step 4: Configure Alerts
1. Go to "Alerting" → "Alert rules"
2. Create new alert rule
3. Copy alert queries from Section 7
4. Set notification channels (email, Slack, etc.)

---

## 10. Expected Baseline Values

Based on baselines_v1.json:

| Metric | P10 | Median | P90 |
|--------|-----|--------|-----|
| Distance (px/min) | 168 | 1,334 | 3,530 |
| Activity Index (%) | 1.6 | 13.2 | 37.8 |

**Day/Night Ratio:** 2.68x (daytime activity is 2.68x higher than nighttime)

**Light Schedule:**
- Lights ON: 7:30 AM - 1:00 AM (17.5 hours)
- Lights OFF: 1:00 AM - 7:30 AM (6.5 hours)

---

## 11. Troubleshooting Queries

### Check Data Freshness
```flux
from(bucket: "fish")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> last()
  |> yield(name: "last_record")
```

### Count Records Per Hour
```flux
from(bucket: "fish")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> aggregateWindow(every: 1h, fn: count)
  |> yield(name: "records_per_hour")
```

### List All Fish IDs (Last Hour)
```flux
from(bucket: "fish")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> distinct(column: "fish_id")
  |> yield(name: "unique_ids")
```

---

**Version:** 1.0
**Last Updated:** October 20, 2025
**Next Steps:** Configure alerts after Phase 2 AI upgrade for stable fish IDs
