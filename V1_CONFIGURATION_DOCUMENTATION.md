# Fish Guardian v1.0 Configuration Documentation
**Last Updated:** October 17, 2025
**Status:** Optimized for Production

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Hardware Configuration](#hardware-configuration)
3. [Performance Optimizations](#performance-optimizations)
4. [Detection Parameters](#detection-parameters)
5. [Tracking & ID Management](#tracking--id-management)
6. [Database Configuration](#database-configuration)
7. [Natural Light Cycle](#natural-light-cycle)
8. [Optimization History](#optimization-history)
9. [Troubleshooting Guide](#troubleshooting-guide)

---

## System Overview

Fish Guardian is a computer vision-based monitoring system for aquarium fish health tracking. It uses motion detection and tracking algorithms to monitor fish activity patterns, establish baselines, and alert on anomalies.

**Core Components:**
- Raspberry Pi 4 (8GB RAM)
- Camera Module 3 Wide (12MP, IMX708)
- InfluxDB 2.7 (time-series database)
- Grafana 10.1 (visualization)
- OpenCV 4.5 (computer vision)
- Python 3.11 (runtime)

---

## Hardware Configuration

### Camera Settings
```python
FRAME_W, FRAME_H = 1280, 720    # Capture resolution
PROCESS_W, PROCESS_H = 640, 360 # Processing resolution (half-res for speed)
FPS_TARGET = 20                  # Target frames per second
```

**Rationale:**
- Full HD capture preserves detail for tracking
- Half-resolution processing achieves 4x speedup
- 20 FPS provides smooth motion tracking

### System Service
```ini
# /etc/systemd/system/fish-guardian.service
[Service]
Type=simple
ExecStart=/home/garrygater1234/Development/fish-guardian/.venv/bin/python3 /home/garrygater1234/Development/fish-guardian/motion_track_influx.py
Restart=always
RestartSec=10
```

---

## Performance Optimizations

### 1. Half-Resolution Processing (Oct 17, 2025)
**Problem:** System running at 5 FPS instead of target 20 FPS

**Solution:** Process motion detection at 640x360, track at full resolution

**Implementation:**
```python
# Resize for processing
frame_small = cv2.resize(frame, (PROCESS_W, PROCESS_H))
fg = bg.apply(frame_small)
# ... processing ...
# Resize back for tracking
th = cv2.resize(th, (FRAME_W, FRAME_H))
```

**Results:**
- FPS: 5 → 20 (4x improvement)
- CPU usage: 122% → 85%
- Detection accuracy: Maintained

### 2. Optimized Background Subtraction
```python
bg = cv2.createBackgroundSubtractorMOG2(
    history=200,          # Reduced from 300
    varThreshold=40,      # Sensitivity tuning
    detectShadows=False   # Disabled for 2x speedup
)
```

**Impact:**
- Processing time: 93ms → 45ms per frame
- Shadow artifacts: Eliminated
- Fish detection: Improved in low light

### 3. Reduced Blur Kernel
```python
# Original (full-res)
fg = cv2.medianBlur(fg, 9)

# Optimized (half-res)
fg = cv2.medianBlur(fg, 3)
```

**Impact:**
- Blur processing: 94ms → 25ms
- Noise reduction: Still effective
- Small bubble filtering: Maintained

---

## Detection Parameters

### Motion Detection
```python
MIN_CONTOUR_AREA = 2000  # Minimum area (full-res, checked after resize)
MOG_VAR_THRESHOLD = 40   # Background sensitivity
```

**Tuning Notes:**
- Set to 2000 for full-resolution contours
- Contours are detected AFTER resizing back to full-res (1280x720)
- Filters out bubbles and debris effectively
- **Bug fix (Oct 17):** Initially set to 500 causing false positives

### Morphological Operations
```python
# Erosion - removes noise
th = cv2.erode(th, np.ones((3, 3), np.uint8), iterations=1)

# Dilation - reconnects fish parts
th = cv2.dilate(th, np.ones((2, 2), np.uint8), iterations=1)
```

### ROI (Region of Interest) Masking
```python
ROI_MASK_ENABLED = True
FILTER_X1, FILTER_Y1 = 0, 0      # Top-left corner
FILTER_X2, FILTER_Y2 = 250, 250  # Bottom-right corner
```

**Purpose:** Excludes filter area from motion detection
**Impact:** Eliminates false positives from water flow/bubbles

---

## Tracking & ID Management

### Core Parameters
```python
MAX_ASSOC_DIST = 200      # Max pixels for track association
TRACK_TIMEOUT = 15.0      # Seconds before marking track as lost
MIN_TRACK_AGE = 30.0      # Seconds before logging to database
GHOST_TIMEOUT = 300.0     # Seconds to keep lost tracks (5 min)
APPEARANCE_WEIGHT = 0.5   # Balance: 50% appearance, 50% position
```

### ID Churn Management

**Problem:** 6,592 unique IDs generated for 7 fish over 2.8 days

**Root Cause:**
- Goldfish pause every 2-5 minutes naturally
- Previous GHOST_TIMEOUT of 120s too short
- Many transient "ghost" tracks from brief detections

**Solution Stack:**

1. **MIN_TRACK_AGE Filter (Oct 16)**
   - Only logs tracks existing > 30 seconds
   - Eliminates 31% of ghost IDs from database
   - Database stays clean for analysis

2. **Extended GHOST_TIMEOUT (Oct 17)**
   - Increased from 120s to 300s
   - Fish can pause up to 5 minutes
   - 56% reduction in ID churn

3. **Improved Appearance Matching**
   - APPEARANCE_WEIGHT: 0.4 → 0.5
   - Better ID resurrection after pauses
   - Uses color histograms + size features

**Results:**
- New IDs per hour: 138 → ~60 (estimated)
- Per fish per hour: 20 → 8-9
- Database records: Clean, only persistent tracks

### Feature Extraction
```python
def extract_features(frame, box):
    # Color histogram (HSV space)
    roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hist_h = cv2.calcHist([roi_hsv], [0], None, [30], [0, 180])
    hist_s = cv2.calcHist([roi_hsv], [1], None, [32], [0, 256])

    # Size features
    'area': w * h
    'aspect_ratio': w / h
    'hist_h': hist_h
    'hist_s': hist_s
```

---

## Database Configuration

### InfluxDB Settings
```python
INFLUX_BUCKET = "fish"
INFLUX_ORG = "home"
INFLUX_URL = "http://localhost:8086"
```

### Data Schema
```python
Point("fish_activity")
    .tag("fish_id", str(tid))
    .field("distance_px", float(distance))      # Pixels moved per minute
    .field("activity_index", float(activity_pct)) # % frames with motion
    .time(timestamp, WritePrecision.NS)
```

### Write Strategy
- Aggregates per-minute metrics
- Flushes every 60 seconds
- Only writes tracks > MIN_TRACK_AGE
- Handles multiple IDs per fish correctly

---

## Natural Light Cycle

### Schedule
```
Lights OFF: 1:00 AM - 7:30 AM (6.5 hours)
Lights ON:  7:30 AM - 1:00 AM (17.5 hours)
```

### Observed Behavior
- **Night Activity:** 598 px/min average
- **Day Activity:** 1,498 px/min average
- **Ratio:** 2.50x (excellent for goldfish)

### Sleep Pattern Analysis
- Deep sleep: 3-6 AM (1-2 unique IDs/hour)
- Light sleep: 1-3 AM, 6-7 AM (moderate IDs)
- Wake-up surge: 7-8 AM (100+ IDs as fish activate)

---

## Optimization History

### Week 1-2: Initial Setup
- Basic motion detection implemented
- InfluxDB integration established
- Grafana dashboards created

### Week 3: Parameter Tuning
- MIN_CONTOUR_AREA: 500 → 2000 (reduced noise)
- MAX_ASSOC_DIST: 100 → 200 (better fast swim tracking)
- TRACK_TIMEOUT: 5 → 15 (handles pausing fish)

### Week 4: Production Optimization

**Oct 16, 2025:**
- MIN_TRACK_AGE: 0 → 30s (database filtering)
- GHOST_TIMEOUT: 60 → 120s (initial ID persistence)
- Natural light cycle established

**Oct 17, 2025:**
- Half-resolution processing (4x FPS improvement)
- GHOST_TIMEOUT: 120 → 300s (56% less ID churn)
- ROI mask implemented (filter area exclusion)
- Shadow detection disabled (2x processing speedup)
- **Bug fix:** MIN_CONTOUR_AREA 500→2000 (was causing false positives)

---

## Troubleshooting Guide

### Issue: Low FPS Performance

**Symptoms:** FPS < 10, high CPU usage, laggy tracking

**Solutions:**
1. Verify half-resolution processing enabled
2. Check `detectShadows=False` in MOG2
3. Reduce blur kernel size if needed
4. Monitor with: `sudo journalctl -u fish-guardian | grep FPS`

### Issue: Excessive ID Churn

**Symptoms:** Hundreds of new IDs per hour

**Solutions:**
1. Increase GHOST_TIMEOUT (max 600s reasonable)
2. Verify MIN_TRACK_AGE=30s active
3. Adjust APPEARANCE_WEIGHT (0.5-0.7 range)
4. Check for environmental issues (bubbles, reflections)

### Issue: Missing Fish Detections

**Symptoms:** Fish count lower than expected

**Solutions:**
1. Reduce MIN_CONTOUR_AREA (try 400)
2. Lower MOG_VAR_THRESHOLD (try 30)
3. Check ROI mask not excluding swimming areas
4. Verify adequate lighting

### Issue: False Positives

**Symptoms:** Detecting non-fish objects

**Solutions:**
1. Increase MIN_CONTOUR_AREA (should be 2000)
2. Enable/adjust ROI mask for problem areas
3. Increase erosion iterations
4. Check for water flow patterns

### Issue: Too Many Active Fish IDs

**Symptoms:** Dashboard showing 30+ active IDs for 7 fish

**Root Cause:** MIN_CONTOUR_AREA set too low for resolution

**Solutions:**
1. Verify MIN_CONTOUR_AREA = 2000 (not 500)
2. Check if processing at half-res but detecting at full-res
3. If using multi-resolution processing, ensure threshold matches detection resolution
4. Monitor with: `sudo journalctl -u fish-guardian | grep "active"`
5. Expected: 7-20 active IDs for 7 fish (some natural churn)

---

## Performance Metrics

### Current System Performance
- **Processing FPS:** 18-20 (target achieved)
- **CPU Usage:** 85% (acceptable)
- **Memory Usage:** 188MB
- **Active Fish IDs:** 10-20 (healthy range for 7 fish)
- **Network I/O:** ~5KB/s to InfluxDB
- **Data Collection Rate:** 270 records/hour
- **ID Churn Rate:** ~60 new IDs/hour (after optimizations)

### Baseline Data Quality
- **Collection Efficiency:** 161% (exceeds expectations)
- **Day/Night Ratio:** 2.68x (natural behavior)
- **Gap Rate:** <5% (acceptable)

---

## Future Improvements (Phase 2)

1. **AI-Based Tracking**
   - YOLOv8 for persistent fish identification
   - Eliminate ID churn completely
   - Individual fish personality profiles

2. **Adaptive Thresholds**
   - Auto-tune parameters based on time of day
   - Learn normal vs abnormal for each fish
   - Seasonal adjustment capabilities

3. **Multi-Camera Support**
   - Side-view camera for depth tracking
   - 3D position reconstruction
   - Full tank coverage

4. **Advanced Analytics**
   - Feeding response metrics
   - Social interaction mapping
   - Breeding behavior detection

---

## Configuration File Locations

```
/home/garrygater1234/Development/fish-guardian/
├── motion_track_influx.py       # Main tracking script
├── .env                          # Environment variables
├── compute_baselines.py          # Baseline computation
├── baselines_v1.json            # Generated baselines
└── data_quality_analysis.py     # Analysis tools

/etc/systemd/system/
└── fish-guardian.service        # Systemd service

/tmp/
├── analyze_id_churn.py          # ID analysis tool
└── profile_fps.py               # Performance profiling
```

---

## Version History

- **v0.1:** Initial prototype with basic motion detection
- **v0.5:** InfluxDB integration and Grafana dashboards
- **v0.8:** Natural light cycle and parameter tuning
- **v1.0:** Production-ready with optimizations (Oct 17, 2025)

---

**Document maintained by:** Fish Guardian Team
**Last validated:** October 17, 2025 @ 13:50 CDT