# Fish Guardian - Ship's Log

## Session Dates: October 14-15, 2025

---

## CURRENT STATUS: 🟢 WEEK 4 BASELINE COLLECTION + ID OPTIMIZATION

**Latest Development (Oct 16):**
Optimized tracking parameters to reduce database ID churn by 80-85%. Extended ghost timeout to 120s (from 60s) for better ID persistence, and increased minimum logging lifetime to 30s to filter out brief ghost tracks. Dashboard v6 deployed with improved health monitoring panels. Week 4 baseline data collection ongoing.

**What's Working:**
- ✅ Week 2 implementation complete
- ✅ InfluxDB v2 configured and receiving data
- ✅ Grafana running and ready
- ✅ Camera Module 3 capturing at 1280x720
- ✅ Motion tracking code functional
- ✅ systemd service created and enabled
- ✅ Python environment with all dependencies
- ✅ Camera mount stabilized (user completed)
- ✅ Fish detection working (picks up fish, minimal noise)
- ✅ **Appearance-based tracking** - fish identified by color + size
- ✅ **Ghost track resurrection** - fish can reclaim their IDs after pausing
- ✅ Track persistence filtering - only stable tracks logged to database

**Current Status:**
- ✅ ID resurrection working (10+ successful resurrections observed)
- ⚠️ Fish pause behavior creates ~20-26 IDs for 7 fish (expected with motion-only tracking)
- ✅ Database filtering ensures clean metrics (MIN_TRACK_AGE = 5s)
- Note: Perfect persistent IDs require AI upgrade (Phase 2 - YOLOv8)

---

## FISH TANK SPECIFICATIONS

**Goldfish Details:**
- Count: 7 goldfish
- Size range: 1 inch (smallest) to 2.5 inches (largest)
- Approximate pixel sizes at 1280x720: 1500-5000 pixels

**Tank Setup:**
- Filter location: Top-left corner (creates constant motion/bubbles)
- Plants: Present (swaying detected as motion)
- Lighting: Fixed overhead

---

## CURRENT PARAMETER SETTINGS

**File:** `motion_track_influx.py` & `motion_track.py`

```python
# Detection Parameters
MIN_CONTOUR_AREA = 2000          # Tuned for goldfish (filters bubbles)
MOG_HISTORY = 300                # Background learning frames
MOG_VAR_THRESHOLD = 40           # Motion sensitivity (higher = less sensitive)
FRAME_W, FRAME_H = 1280, 720     # Resolution
FPS_TARGET = 20                  # Processing speed (influx version only)

# Tracking Parameters (Oct 16 - Optimized for ID Churn)
MAX_ASSOC_DIST = 200             # Max pixel distance for track association
TRACK_TIMEOUT = 15.0             # Seconds before moving track to ghost (increased for pausing fish)
MIN_TRACK_AGE = 30.0             # Only log tracks older than 30s to InfluxDB (was 5.0s)
GHOST_TIMEOUT = 120.0            # Keep ghost tracks for resurrection (was 60.0s)
APPEARANCE_WEIGHT = 0.4          # 40% appearance, 60% position matching

# Image processing pipeline:
- Median blur: 9x9 kernel
- Threshold: 200
- Erosion: 5x5 kernel, 1 iteration
- Dilation: 3x3 kernel, 1 iteration

# Appearance Features Extracted:
- HSV color histogram (Hue + Saturation, 16+8 bins)
- Bounding box area (fish size)
- Aspect ratio (body shape)
```

---

## TUNING HISTORY

### Initial Deployment (16:25 CDT)
- MIN_CONTOUR_AREA: 200
- MOG_VAR_THRESHOLD: 16
- Result: Detected 500+ objects (extreme noise)

### First Tuning Pass (16:30 CDT)
- MIN_CONTOUR_AREA: 200 → 800
- MOG_VAR_THRESHOLD: 16 → 25
- Result: Still too many detections (~100+ objects)

### Second Tuning Pass (Approved by user, 21:30+ CDT)
- MIN_CONTOUR_AREA: 800 → 2000
- MOG_VAR_THRESHOLD: 25 → 40
- Median blur: 5 → 9
- Added erosion step: 5x5 kernel
- Dilation iterations: 2 → 1
- Result: Better, but still detecting plants/filter/bubbles due to camera movement

### Third Tuning Pass - Post Camera Stabilization (22:30+ CDT)
**User stabilized camera mount**
- Result: Fish detection working well, minimal false positives
- New issue: ID instability - 26 IDs for 7 fish in 60 seconds
- Cause: MAX_ASSOC_DIST too small, tracks timing out too quickly

### Tracking Persistence Improvements (Deployed 22:45+ CDT, Oct 14)
- MAX_ASSOC_DIST: 80 → 200 (allow fish to move further between frames)
- TRACK_TIMEOUT: 3.0s → 8.0s (keep tracks alive longer during occlusions)
- Added MIN_TRACK_AGE: 5.0s (only log established tracks to InfluxDB)
- Added track_birth_time tracking for age filtering
- Expected result: Stable IDs (~7-10 instead of 26+)

### Appearance-Based Tracking Implementation (Oct 15, 12:00-13:00 CDT)
**Major upgrade: Motion + Appearance hybrid tracking**
- Implemented color histogram fingerprinting (HSV: Hue + Saturation, 16+8 bins)
- Added size (bounding box area) and aspect ratio features
- Smart matching: 60% position + 40% appearance weighted scoring
- Ghost track system: Save lost tracks for 60s, enable ID resurrection
- Exponential moving average for feature stability (80% old, 20% new)
- Result: 10+ successful ID resurrections observed in testing

### Extended Timeout for Goldfish Behavior (Oct 15, 12:40 CDT)
- TRACK_TIMEOUT: 8.0s → 15.0s (goldfish pause/rest frequently)
- Observation: Fish stop moving for 15-60+ seconds regularly
- Result: Reduced ID churn, more resurrections instead of new IDs
- Database metrics remain clean via MIN_TRACK_AGE filtering

---

## NEXT STEPS (IN ORDER)

### 1. ✅ COMPLETED: Camera Stabilization
- [x] Secure camera mount (no wobbling)
- [x] User tested - fish tracking working well

### 2. ⚠️ CURRENT: Test ID Stability Improvements
**User should run these tests:**
```bash
cd ~/Development/fish-guardian
source .venv/bin/activate
python3 motion_track.py
# Watch for 60-90 seconds
# Count unique IDs shown - should see ~7-10 instead of 26+
# Press 'q' to quit
```

Expected results:
- IDs should remain stable when fish swim normally
- IDs should persist even when fish temporarily overlap/occlude
- New IDs only when fish are stationary for 8+ seconds
- InfluxDB should only log fish that have been tracked for 5+ seconds

### 3. Optional Fine-Tuning (If Needed)
- If still getting some false detections from reflections: Adjust lighting
- If filter area creating issues: Add ROI mask to exclude top-left corner
- If bubbles still detected: Increase MIN_CONTOUR_AREA further

### 4. Create Grafana Dashboard (Week 3)
- Add InfluxDB data source
- Create activity visualizations
- Set up basic alerts
- Document dashboard queries

### 5. Collect 5-7 Day Baseline (Week 4)
- Let system run continuously via systemd service
- Document normal activity patterns per fish
- Refine Grafana alerts based on baseline data

---

## SYSTEM ARCHITECTURE

**Pi Location:** 192.168.0.213 (ssh pi-fish)
**Project Path:** ~/Development/fish-guardian/
**User:** garrygater1234

**Services:**
- InfluxDB v2.7.10 (port 8086)
  - Organization: home
  - Bucket: fish
  - Token: stored in .env
- Grafana (port 3000)
  - Default login: admin/admin
- fish-guardian.service (systemd)
  - Auto-starts on boot
  - Runs motion_track_influx.py

**Python Environment:**
- venv at: ~/Development/fish-guardian/.venv
- Key packages: influxdb-client, numpy, opencv, picamera2, python-dotenv

---

## METRICS BEING LOGGED

**Measurement:** `fish_activity`
**Frequency:** Every 60 seconds
**Tags:**
- fish_id: Temporary ID (1-N, resets on service restart)

**Fields:**
- distance_px: Total pixels moved in last minute
- activity_index: % of frames with motion (0-100%)

**Note:** Fish IDs are temporary and will eventually be replaced with AI-based persistent IDs in Phase 2 (Weeks 5-10).

---

## KNOWN ISSUES & WORKAROUNDS

### Issue: Camera Movement
**Status:** IN PROGRESS - User securing mount
**Impact:** All motion detection breaks
**Workaround:** None - must fix hardware

### Issue: Filter Creating Constant Motion
**Status:** PLANNED - Will add ROI mask
**Impact:** False detections in top-left
**Workaround:** Increase MIN_CONTOUR_AREA to ignore

### Issue: Bubble Detection
**Status:** PLANNED - Increase thresholds after camera stable
**Impact:** Small bubbles (500-1500px) detected as fish
**Workaround:** MIN_CONTOUR_AREA will be increased to 4000+

### Issue: Plant Movement
**Status:** WAITING - Needs stable camera first
**Impact:** Swaying plants detected
**Workaround:** Background subtractor will learn them once camera stable

---

## TESTING COMMANDS

### Visual Tracking Test (Shows video feed)
```bash
cd ~/Development/fish-guardian
source .venv/bin/activate
python3 motion_track.py
# Press 'q' to quit
```

### Production Test (Logs to InfluxDB)
```bash
python3 motion_track_influx.py
# Let run 2-3 minutes
# Ctrl+C to stop
```

### Check InfluxDB Data
```bash
/tmp/influx query 'from(bucket:"fish") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "fish_activity") | limit(n:10)' --org home
```

### Service Control
```bash
sudo systemctl restart fish-guardian    # Restart service
sudo journalctl -u fish-guardian -f     # Watch logs
sudo systemctl status fish-guardian     # Check status
```

---

## FILES IN PROJECT

```
~/Development/fish-guardian/
├── .env                             # InfluxDB credentials (SENSITIVE)
├── .venv/                           # Python virtual environment
├── README.md                        # Full project documentation
├── TESTING_CHECKLIST.md            # Step-by-step testing guide
├── TUNING_APPLIED.md               # Parameter tuning history (Oct 14)
├── SESSION_STATUS.md               # This file - current session state
├── grafana_setup.md                # Grafana configuration guide
├── cam_test.py                     # Camera verification script
├── detect_camera.py                # Camera device detection
├── motion_track.py                 # Standalone tracker (shows video)
├── motion_track_influx.py          # Production tracker (logs to DB)
└── motion_track_influx.py.backup   # Pre-tuning backup
```

---

## ROADMAP CONTEXT

**Current Phase:** Week 2 - Motion Detection & Basic Tracking ✅ COMPLETE (code)
**Next Phase:** Week 3 - Dashboard & Alerts (blocked by camera stability)
**Future:** Week 5-10 - AI Upgrade (YOLOv8, persistent IDs)

**Week 2 Objectives (ALL COMPLETE):**
- [x] OpenCV MOG2 background subtraction
- [x] Motion detection → contours → centroids
- [x] Multi-target tracker with temporary IDs
- [x] Per-minute activity metrics
- [x] InfluxDB v2 integration
- [x] systemd service
- [x] Grafana setup guide

---

## SESSION HANDOFF NOTES

**For next Claude session:**
1. Camera stabilization is the #1 priority - nothing else will work until this is fixed
2. Once stable, user will test with `python3 motion_track.py` to verify
3. If still too noisy after stabilization: increase MIN_CONTOUR_AREA to 4000
4. Consider ROI mask for filter area (top-left corner)
5. User is motivated and hands-on - expect quick iteration

**Context to provide next session:**
```
Working on fish-guardian project. Read SESSION_STATUS.md for full context.
Currently addressing camera stability before final parameter tuning.
Week 2 code complete, just need to optimize detection thresholds.
```

---

## LOG ENTRIES

### 2025-10-14 14:00 CDT - Session Start
- Reviewed Week 2 roadmap
- User has 7 goldfish in clean tank ready to monitor

### 2025-10-14 16:08 CDT - Infrastructure Complete
- SSH access configured (pi-fish alias)
- Week 1 verification passed
- Camera Module 3 tested and working
- InfluxDB v1 → v2 upgrade completed
- Python dependencies installed (venv with system-site-packages)

### 2025-10-14 16:25 CDT - Core Scripts Deployed
- motion_track.py created (standalone visual tracker)
- motion_track_influx.py created (production with InfluxDB)
- systemd service configured
- Documentation complete

### 2025-10-14 16:40 CDT - First Test Run
- Detected 500+ objects - extreme noise
- Data successfully written to InfluxDB
- System works end-to-end, just needs tuning

### 2025-10-14 21:00 CDT - Tuning Session Begin
- User viewing camera feed directly on Pi
- Identified: bubbles, plants, filter all being detected
- Applied aggressive filtering (see TUNING_APPLIED.md)

### 2025-10-14 21:45 CDT - Root Cause Identified
- **Camera mount is unstable** - causing all static objects to appear moving
- Background subtraction cannot learn while camera moves
- User working to stabilize mount
- All parameter tuning suspended until camera fixed

### 2025-10-14 22:00 CDT - Ship's Log Created
- SESSION_STATUS.md created for session continuity
- Waiting on user to stabilize camera hardware
- Next session can resume immediately from this log

### 2025-10-14 22:30 CDT - Camera Stabilized, ID Issue Identified
- User successfully stabilized camera mount
- Fish detection working well with minimal false positives
- Discovered ID instability: 26 IDs assigned to 7 fish in 60 seconds
- Reflections detected as separate fish (minor issue, can address with lighting)

### 2025-10-14 22:45 CDT - Tracking Persistence Improvements Deployed
- Updated MAX_ASSOC_DIST: 80 → 200 pixels
- Increased TRACK_TIMEOUT: 3.0s → 8.0s
- Added MIN_TRACK_AGE filtering (5.0s) for InfluxDB logging
- Added track_birth_time tracking for age-based filtering
- Deployed to both motion_track.py and motion_track_influx.py
- Waiting for user to test ID stability

### 2025-10-15 12:00 CDT - Appearance-Based Tracking Implemented
- User identified ID instability as critical blocker for system usability
- Implemented hybrid position + appearance tracking (60/40 weighting)
- Added color histogram (HSV), size, and aspect ratio feature extraction
- Created ghost track resurrection system (60s timeout)
- Features updated with exponential moving average for stability
- Testing showed 10+ successful ID resurrections

### 2025-10-15 12:40 CDT - Extended Timeout for Goldfish Behavior
- Observed: Goldfish pause/rest for 15-60+ seconds regularly
- Increased TRACK_TIMEOUT: 8.0s → 15.0s
- Result: More resurrections, less new ID creation
- Database quality maintained via MIN_TRACK_AGE filtering
- System functionally complete for motion-based tracking

### 2025-10-15 12:42 CDT - Pipewire Camera Blocking Issue Resolved
- Discovered pipewire + chromium holding camera devices
- Created helper script to stop pipewire for manual testing
- Documented camera release procedure
- Added to testing workflow

---

**End of Current Log Entry**
*Last Updated: 2025-10-15 12:45 CDT*

### 2025-10-15 16:15 CDT - Week 3 Complete: Grafana Dashboard & Alerts
- ✅ InfluxDB data source configured in Grafana
- ✅ Comprehensive dashboard deployed with 6 panels:
  * Fish Movement (Distance) time series
  * Fish Activity Index (%) time series
  * Low Activity Alert (visual threshold panel)
  * Active Fish Count (real-time monitoring)
  * System Health status indicator
  * Recent Fish Activity table
- ✅ Visual alert system implemented using color-coded thresholds
  * Red backgrounds indicate critical issues
  * Orange/yellow indicate warnings
  * Green indicates normal operation
- ✅ Auto-refresh every 5 seconds for live monitoring
- ✅ Created GRAFANA_DASHBOARD_GUIDE.md (comprehensive documentation)
- ✅ All Week 3 objectives met

**Dashboard URL:** http://localhost:3000/d/fa5750fb-5765-4eed-8fd2-4c3b88e30c46

**Next Steps:** Week 4 - Collect 5-7 day baseline data, refine alert thresholds

### 2025-10-16 11:26 CDT - Database Optimization Deployed (Round 4)
- ✅ Identified ID churn problem: 200+ unique IDs over 30 min (59 in 5 min)
- ✅ Extended GHOST_TIMEOUT: 60s → 120s (fish reclaim IDs after 2-min pauses)
- ✅ Increased MIN_TRACK_AGE: 5s → 30s (only log established tracks to DB)
- ✅ Dashboard v6 deployed:
  * Removed misleading "Fish Below 300px" panel (counted ghosts as sick fish)
  * Improved "LEAST Active Fish" health monitoring table
  * Updated panel descriptions to explain ghost ID behavior
- ✅ Expected result: 80-85% reduction in database clutter
- ⏱️ Monitoring: Check ID counts in 1-2 hours to verify improvements
- 📊 Service restarted successfully with new settings
- 📋 Documentation updated (TUNING_APPLIED.md Round 4 added)

**Latest Dashboard:** http://192.168.0.213:3000/d/efbc61c8-2f7a-4994-98eb-805b8ecb3d9e/fish-guardian-activity-monitoring-v6

