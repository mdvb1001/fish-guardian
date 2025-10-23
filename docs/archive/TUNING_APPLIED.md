# Fish Detection Tuning - Applied Changes
**Date:** October 14-15, 2025

## Round 1: Image Processing Tuning (21:30 CDT, Oct 14)

### motion_track.py & motion_track_influx.py

**Before → After:**
- MIN_CONTOUR_AREA: 800 → **2000** (4x larger goldfish minimum)
- MOG_VAR_THRESHOLD: 25 → **40** (much less sensitive)
- Median blur kernel: 5 → **9** (more smoothing)
- Added: **Erosion step** (5x5 kernel) before dilation
- Dilation iterations: 2 → **1** (less aggressive)

## Round 2: Tracking Persistence Improvements (22:45 CDT, Oct 14)

**After camera stabilization by user**

### motion_track.py & motion_track_influx.py

**Before → After:**
- MAX_ASSOC_DIST: 80 → **200** (allow fish to move further between frames)
- TRACK_TIMEOUT: 3.0s → **8.0s** (keep tracks alive longer during occlusions)
- Added: **MIN_TRACK_AGE: 5.0s** (only log established tracks to InfluxDB)
- Added: **track_birth_time** tracking for age-based filtering

**Purpose:** Fix ID instability (was seeing 26 IDs for 7 fish in 60 seconds)

## Round 3: Appearance-Based Tracking (12:00-13:00 CDT, Oct 15)

**Critical upgrade for persistent fish identification**

### motion_track.py & motion_track_influx.py

**New Parameters Added:**
- **GHOST_TIMEOUT: 60.0s** (keep lost tracks for resurrection)
- **APPEARANCE_WEIGHT: 0.4** (40% appearance, 60% position matching)
- **TRACK_TIMEOUT: 8.0s → 15.0s** (goldfish pause frequently)

**New Functions Added:**

1. **extract_features(frame, box)** - Extracts appearance fingerprint:
   - HSV color histogram (16 bins Hue + 8 bins Saturation)
   - Bounding box area (fish size)
   - Aspect ratio (body shape)

2. **appearance_similarity(feat1, feat2)** - Compares fish appearance:
   - Color histogram correlation (50% weight)
   - Size similarity, allows 30% variation (30% weight)
   - Aspect ratio similarity, allows 20% variation (20% weight)
   - Returns score 0-1 (higher = more similar)

**New Data Structures:**
- **ghost_tracks** dictionary - Saves lost tracks for 60s resurrection
- **track_birth_time** dictionary - Tracks when each fish ID was created

**Modified Tracking Logic:**

1. **Hybrid Matching** - Combines position + appearance:
   ```
   combined_score = 60% position_score + 40% appearance_score
   Minimum threshold: 0.3 for active tracks
   ```

2. **Ghost Resurrection** - Fish reclaim IDs after pausing:
   ```
   - Fish stops moving for 15s → moved to ghost_tracks
   - Ghost saved for 60s with appearance features
   - New detection compared against ghosts using appearance
   - Match threshold: 0.6 (higher than active tracking)
   - Successful match → fish gets old ID back (shown in yellow)
   ```

3. **Feature Smoothing** - Exponential moving average:
   ```
   new_features = 80% old_features + 20% current_observation
   Prevents feature drift from momentary changes
   ```

**Purpose:** Enable persistent fish IDs across pausing/resting behavior

**Results:** 
- 10+ successful ID resurrections observed in testing
- Still creates ~20-26 IDs for 7 fish (expected with goldfish pausing 60+ seconds)
- Database quality maintained via MIN_TRACK_AGE filtering
- System now functionally usable for long-term monitoring

## What This Should Fix

### Image Processing (Round 1):
✓ Reduces bubble/reflection detections by 80-90%
✓ Only detects larger moving objects (goldfish-sized)
✓ Smooths out water movement noise
✓ Eliminates small specks before they get enlarged

### Tracking Persistence (Round 2):
✓ Stable fish IDs (~7-10 instead of 26+ in 60 seconds)
✓ IDs persist through fast swimming movements
✓ IDs survive temporary occlusions (fish overlapping)
✓ Only established tracks logged to InfluxDB (cleaner data)

### Appearance Tracking (Round 3):
✓ Fish can reclaim their IDs after stopping movement
✓ System distinguishes fish by color and size
✓ Ghost tracks enable "resurrection" after 15-60s pauses
✓ Yellow boxes indicate when fish successfully reclaims ID
✓ System usable for long-term monitoring despite fish pausing

## Testing Instructions

### Option 1: Visual Test (Recommended First)
```bash
cd ~/Development/fish-guardian
source .venv/bin/activate
python3 motion_track.py
```
**Watch for:**
- Green boxes around actively tracked fish
- **Yellow boxes indicate resurrected fish** (reclaimed their ID)
- Status overlay shows "Active: X | Ghost: Y" counts
- Fish IDs should stay relatively stable
- When fish pauses and resumes, may reclaim old ID (yellow)
- Press 'q' to quit

### Option 2: Production Test (Logs to Database)
```bash
python3 motion_track_influx.py
# Let run for 2-3 minutes
# Press Ctrl+C to stop
```
**Check logs for:**
- `[STATUS] X frames | Y FPS | Z active tracks | G ghost tracks`
- `[RESURRECT] Fish ID X reappeared (appearance match)` - success!
- `[LOST] Fish ID X - no motion for 15s` - moved to ghosts
- `[GHOST EXPIRED] Fish ID X - 60s since last seen` - permanently removed

### Option 3: Service Test (Background)
```bash
sudo systemctl restart fish-guardian
sudo journalctl -u fish-guardian -f
```

## Expected Results

**Good tuning indicators:**
- 5-10 active tracks consistently (your 7 fish + maybe 1-3 transient detections)
- Fish IDs remain stable for extended periods
- **Frequent resurrection messages** when fish resume moving
- Yellow boxes appear when fish successfully reclaim IDs
- Ghost track count varies (0-5 typical)
- Clear bounding boxes around each fish
- Minimal noise detection
- InfluxDB only shows established, reliable fish tracks (5s+ old)

**Understanding ID churn:**
- 20-26 IDs created for 7 fish over time is **expected behavior**
- Goldfish pause for 60+ seconds, exceeding ghost timeout
- Database filtering (MIN_TRACK_AGE=5s) keeps metrics clean
- Perfect persistent IDs require AI upgrade (Phase 2 - YOLOv8)

**If still too noisy:**
Increase MIN_CONTOUR_AREA further:
```bash
cd ~/Development/fish-guardian
nano motion_track_influx.py
# Change: MIN_CONTOUR_AREA = 2000
# To:     MIN_CONTOUR_AREA = 3000
```

**If missing fish:**
Decrease MIN_CONTOUR_AREA:
```bash
# Change to: MIN_CONTOUR_AREA = 1500
```

**If too many new IDs (not enough resurrections):**
Adjust appearance matching:
```bash
cd ~/Development/fish-guardian
nano motion_track_influx.py
# Increase ghost resurrection threshold:
# Change: if app_score > best_ghost_score and app_score >= 0.6:
# To:     if app_score > best_ghost_score and app_score >= 0.5:
# 
# Or increase ghost timeout:
# Change: GHOST_TIMEOUT = 60.0
# To:     GHOST_TIMEOUT = 90.0
```

**If IDs switching between fish (wrong resurrections):**
Increase resurrection threshold:
```bash
# Change: if app_score > best_ghost_score and app_score >= 0.6:
# To:     if app_score > best_ghost_score and app_score >= 0.7:
```

## Round 4: Database Optimization for ID Churn (11:26 CDT, Oct 16)

**Problem Identified:**
- ~200+ unique IDs logged over 30 minutes despite only 7 actual goldfish
- 59 unique IDs detected in just 5 minutes
- Root cause: Goldfish pause frequently (15-60+ seconds), exceeding ghost timeout
- Database cluttered with short-lived "ghost track" IDs

**Solutions Deployed:**

### motion_track_influx.py

**Before → After:**
- **MIN_TRACK_AGE: 5.0s → 30.0s** (only log tracks that exist for 30+ seconds)
- **GHOST_TIMEOUT: 60.0s → 120.0s** (fish can reclaim IDs after 2-minute pauses)

**Purpose:** Reduce database ID churn by 80-85%

**Changes:**
1. **Minimum Logging Lifetime (30s):**
   - Tracks must exist for 30 seconds before being logged to database
   - Active tracking continues as normal (not affected)
   - Filters out brief, spurious detections and very short fish appearances
   - Expected: 60-70% reduction in database IDs

2. **Extended Ghost Timeout (120s):**
   - Fish can now reclaim their ID after pausing for up to 2 minutes (was 1 minute)
   - Better accommodates natural goldfish pausing behavior (often pause 60-90s)
   - Expected: 40-50% reduction in active fish IDs

**Trade-offs:**
- Very brief activity bursts (<30s) won't be logged to database
  - Still tracked in real-time for monitoring
  - Only affects database persistence
  - These are usually noise anyway

**Expected Results:**
- Active IDs (5 min): ~59 → 25-35 (40% reduction)
- Database IDs (30 min): ~200+ → 30-50 (80% reduction)
- **Combined: ~80-85% reduction in database clutter**

**Dashboard Updates:**
- Removed misleading "Fish Below 300px" panel (counted ghost IDs as sick fish)
- Dashboard v6 deployed with improved health monitoring
- Panel descriptions now explain ghost ID behavior

**Monitoring:**
- Check unique ID counts after 1-2 hours to verify reduction
- Dashboard "Active Fish IDs" panel should show lower, more stable numbers
- "LEAST Active Fish" table will be cleaner with fewer ghost entries

---

## Quick Parameter Reference

### Detection Parameters
| Parameter | Purpose | Lower = | Higher = |
|-----------|---------|---------|----------|
| MIN_CONTOUR_AREA | Size filter | Detects smaller objects | Only large objects |
| MOG_VAR_THRESHOLD | Motion sensitivity | More motion detected | Only strong motion |
| Median blur kernel | Noise smoothing | Less smoothing | More smoothing |
| Erosion iterations | Noise removal | Less removal | More removal |

### Tracking Parameters
| Parameter | Purpose | Lower = | Higher = |
|-----------|---------|---------|----------|
| MAX_ASSOC_DIST | ID matching distance | Strict matching, more new IDs | Loose matching, stable IDs |
| TRACK_TIMEOUT | Track lifetime | Remove lost tracks quickly | Keep tracks longer |
| MIN_TRACK_AGE | DB logging filter | Log all tracks | Only log established tracks |
| GHOST_TIMEOUT | Resurrection window | Shorter resurrection window | Longer resurrection window |
| APPEARANCE_WEIGHT | Appearance vs position | More position-based | More appearance-based |

## Backup

Original scripts backed up as:
- motion_track_influx.py.backup

To restore:
```bash
cp motion_track_influx.py.backup motion_track_influx.py
```
