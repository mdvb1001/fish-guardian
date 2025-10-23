# Fish Guardian - Project Context

**Last Updated:** October 21, 2025
**Current Phase:** Week 4 Complete ✅ → Ready for Phase 2 (AI Upgrade)
**System Status:** Production, operational, collecting data

---

## 🎯 Quick Status

| Aspect | Status | Details |
|--------|--------|---------|
| **Motion Tracking** | ✅ Running | 20 FPS, systemd service, 2+ days uptime |
| **Data Collection** | ✅ Active | InfluxDB, ~270 records/hour, 575% collection rate |
| **Baselines** | ✅ Complete | 5.85 days, 90,304 records, baselines_v1.json |
| **Dashboard** | ✅ Deployed | Grafana v7, 11 panels, baseline overlays |
| **Version Control** | ✅ Setup | Git on Pi (master), synced to local (main) |
| **Next Phase** | 🚀 Ready | Phase 2: AI-based tracking to replace motion detection |

---

## 📍 Where We Are

### Project Timeline
- **Week 1-2:** Initial setup, camera configuration, OpenCV motion detection
- **Week 3:** Performance optimization, ID management, ROI masking
- **Week 4 (Oct 14-21):** ✅ **COMPLETE**
  - Baseline data collection (5.85 days)
  - Baseline computation (baselines_v1.json)
  - Grafana dashboard creation & fixes
  - System stabilization
- **Week 5+ (Next):** Phase 2 - AI upgrade (YOLOv8/EfficientDet)

### Key Achievements (Week 4)
- ✅ Collected 5.85 days of continuous baseline data
- ✅ Generated global baselines (P10: 168px, Median: 1334px, P90: 3530px)
- ✅ Created Grafana Dashboard v7 with 11 panels
- ✅ Fixed all dashboard panel issues (series limits, aggregation, mappings)
- ✅ Generated 24-hour analysis reports
- ✅ Established version control (Git)
- ✅ Updated all documentation

---

## 🏗️ System Architecture

### Hardware
- **Computer:** Raspberry Pi 4 Model B
- **Camera:** Camera Module 3 (1280x720 @ 20 FPS)
- **Network:** 192.168.0.213 (hostname: pi-fish)
- **Tank:** 7 goldfish in aquarium with filter

### Software Stack
```
Camera Module 3
    ↓ (picamera2)
OpenCV Motion Detection (MOG2)
    ↓ (background subtraction)
Fish Tracking (motion_track_influx.py)
    ↓ (60-second aggregation)
InfluxDB 2.7 (time-series database)
    ↓ (Flux queries)
Grafana 10.1 (visualization)
    ↓ (dashboard)
User Interface (web browser)
```

### Key Components
1. **motion_track_influx.py** - Main tracking script (systemd service)
2. **InfluxDB** - Database (bucket: "fish", measurement: "fish_activity")
3. **Grafana** - Dashboard (Fish Guardian - Activity Monitoring v7)
4. **baselines_v1.json** - Computed baseline statistics (64MB)

### Access Points
- **SSH:** `ssh pi-fish` (192.168.0.213)
- **Grafana:** http://192.168.0.213:3000/d/fish-guardian-v7 (admin/admin)
- **InfluxDB:** http://192.168.0.213:8086
- **Camera Stream:** http://192.168.0.213:5000 (when active)

---

## 📊 Current Metrics & Baselines

### Global Baselines (from 5.85 days)
| Metric | P10 | Median | P90 |
|--------|-----|--------|-----|
| Distance (px) | 168 | 1,334 | 3,530 |
| Activity Index (%) | 1.6 | 13.2 | 37.8 |

**Data Period:** Oct 14-20, 2025 (90,304 records)

### Latest 24-Hour Analysis (Oct 21, 2025)
- **Total Activity:** 12,129,749 px (+6.3% vs previous day)
- **Unique Fish IDs:** 2,898 (high due to motion-based tracking)
- **Data Points:** 8,293 (575% of expected - excellent)
- **Median Distance:** 1,137 px (14.7% below baseline - normal variation)
- **Status:** System performing normally

### Performance Metrics
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| FPS | 20 | 20 | ✅ |
| CPU Usage | <90% | 85% | ✅ |
| Data Rate | ~200/hr | 270/hr | ✅ |
| ID Churn | <100/hr | ~60/hr | ✅ |
| Day/Night Ratio | 2-3x | 2.68x | ✅ |

---

## 🎨 Grafana Dashboard Details

### Dashboard Information
- **Name:** Fish Guardian - Activity Monitoring v7
- **UID:** `fish-guardian-v7`
- **URL:** http://192.168.0.213:3000/d/fish-guardian-v7
- **Panels:** 11 panels with baseline overlays

### Panel Configuration
1. **Fish Activity Status** (Panel ID: 4)
   - Shows: ✅ Online / ❌ Offline
   - Query: Checks for fish movement in last 5 minutes
   - **Important:** Shows fish activity, NOT system uptime
   - Empty tank = shows Offline (known limitation)

2. **Activity Timeline**
   - Distance tracking with P10/P90 baseline overlays
   - Time-series visualization

3. **Active Fish Count (5m)**
   - Rolling 5-minute window of unique fish detected

4. **Activity Alert**
   - Flags when activity exceeds P90 baseline (3,530px)
   - Fixed: Series aggregation to avoid "exceeded series limit"

5. **Unique Fish IDs per Hour**
   - Tracks ID churn (currently ~2,898/day)
   - Will drop to ~7 after Phase 2 AI upgrade

6. **Total Activity (24h)**
   - Cumulative distance metric
   - Stat panel showing total movement

7. **Top 5 Most Active Fish**
   - Bar chart of most active fish_ids

8. **Activity Distribution**
   - Histogram of distance values

9. **Activity Heatmap**
   - Hourly activity patterns

10. **Day vs Night Activity**
    - Pie chart (Day: 8 AM - 1 AM, Night: 1 AM - 8 AM)

11. **Activity Index Timeline**
    - Percentage-based activity tracking

### Known Dashboard Issues & Solutions

**Issue 1: "System Status" showing "No data"**
- **Root Cause:** Complex Flux aggregation (toFloat + sum + map) returning zero results
- **Fix Applied:** Use simple query returning multiple fish_id counts, let Grafana sum with `reduceOptions: sum`
- **Final Solution:** Changed to "Fish Activity Status" with clear description of limitation
- **Attempts:** 5 iterations before finding working solution

**Issue 2: "Activity Alert exceeded series limit"**
- **Root Cause:** Returning hundreds of fish_id series without aggregation
- **Fix:** Added `group()` and `sum()` to aggregate before display

**Issue 3: "Fish ID tracking exceeded series limit"**
- **Root Cause:** Complex query timing out
- **Fix:** Simplified to window-based unique count

**Issue 4: "Activity vs baselines not loading"**
- **Root Cause:** Multiple complex queries causing timeout
- **Fix:** Simplified baseline queries to use constant values

---

## 🔧 Configuration Details

### Motion Tracking Parameters
```python
# Camera & Processing
FRAME_W, FRAME_H = 1280, 720           # Capture resolution
PROCESS_W, PROCESS_H = 640, 360        # Processing resolution (half-res)
FPS_TARGET = 20                         # Target and achieved FPS

# Detection
MIN_CONTOUR_AREA = 500                 # Minimum fish size (adjusted for half-res)
MOG_VAR_THRESHOLD = 40                 # Background subtraction sensitivity

# ROI Masking (filter area excluded)
ROI_MASK_ENABLED = True
FILTER_X1, Y1 = 0, 0                   # Top-left corner
FILTER_X2, Y2 = 250, 250               # Bottom-right corner

# Tracking & ID Management
TRACK_TIMEOUT = 15.0                   # Seconds before track considered lost
MIN_TRACK_AGE = 30.0                   # Minimum age before writing to database
GHOST_TIMEOUT = 300.0                  # 5-minute window for ID resurrection
APPEARANCE_WEIGHT = 0.5                # 50/50 appearance vs position matching
```

### Data Collection
```python
# Logged every 60 seconds per fish_id
Point("fish_activity")
    .tag("fish_id", str(tid))
    .field("distance_px", float)       # Pixels moved in last minute
    .field("activity_index", float)    # Percentage of frames with motion
    .time(timestamp)
```

### Light Cycle
- **Lights OFF:** 1:00 AM - 7:30 AM (6.5 hours)
- **Lights ON:** 7:30 AM - 1:00 AM (17.5 hours)
- **Day/Night Activity Ratio:** 2.68x (healthy goldfish behavior)

---

## 🐛 Known Issues & Limitations

### 1. High Fish ID Churn
- **Issue:** Motion tracking creates 2,898 unique IDs per day for 7 fish
- **Root Cause:** Motion-based tracking assigns new IDs when fish temporarily disappear
- **Impact:** Makes per-fish long-term tracking impossible
- **Solution:** Phase 2 AI upgrade (YOLOv8/EfficientDet) will provide persistent IDs
- **Status:** Expected, not a bug - by design of motion-based approach

### 2. Fish Activity Status vs System Uptime
- **Issue:** "Fish Activity Status" panel shows "Offline" when tank is empty
- **Root Cause:** Panel checks for fish movement records, not system health
- **Impact:** Misleading during tank cleaning or when fish are inactive
- **Current Workaround:** Renamed panel and added description explaining limitation
- **Future Fix Options:**
  1. Add system heartbeat measurement (writes every minute regardless of fish)
  2. Query systemd service status directly
- **Status:** Documented limitation, accepted for v1.0

### 3. No Email/SMS Alerts
- **Issue:** Dashboard shows alerts but doesn't notify
- **Status:** Feature not implemented in v1.0
- **Future Enhancement:** Configure Grafana alert notifications

### 4. Baseline Data Size
- **Issue:** baselines_v1.json is 64MB (9,258 fish profiles)
- **Root Cause:** High ID churn creating profile for each temporary ID
- **Impact:** Large file size, but no functional issues
- **Solution:** Phase 2 will reduce to ~7 fish profiles
- **Status:** Acceptable for v1.0

---

## 🗂️ File Locations & Structure

### On Raspberry Pi (`~/Development/fish-guardian/`)
```
fish-guardian/
├── .git/                              # Git repository (master branch)
├── .gitignore                         # Excludes .env, .venv, baselines, etc.
├── .env                               # InfluxDB credentials (NOT in git)
├── .venv/                             # Python virtual environment (NOT in git)
│
├── motion_track_influx.py             # Main tracking script ⭐
├── compute_baselines.py               # Baseline computation script
├── data_quality_analysis.py           # Data analysis tools
├── camera_stream.py                   # Live camera web viewer
├── view_camera.sh                     # Quick camera launcher
│
├── baselines_v1.json                  # Generated baselines (64MB, NOT in git)
├── 24h_report.txt                     # Latest analysis report
│
├── README.md                          # Project overview ⭐
├── PROJECT_CONTEXT.md                 # This file ⭐
├── GIT_WORKFLOW.md                    # Version control guide
├── V1_CONFIGURATION_DOCUMENTATION.md  # Technical reference
├── BASELINE_COLLECTION_GUIDE.md       # Daily operations
├── GRAFANA_DASHBOARD_GUIDE.md         # Dashboard setup
├── GRAFANA_QUERIES_v1.md              # Query library
├── QUICK_START_DASHBOARD.md           # Manual dashboard setup
├── TESTING_CHECKLIST.md               # Validation procedures
│
├── create_dashboard_v7.py             # Dashboard creation script
├── fix_system_status_final.py         # Latest dashboard fixes
│
└── docs/
    ├── archive/                       # Historical documentation
    └── planning/                      # Week PDFs and roadmaps
```

### On Local Machine
```
fish-guardian/
├── .git/                              # Git repository (main branch)
│   └── remote: pi-fish (master)       # Points to Pi as source of truth
├── .claude/                           # Claude Code settings
│
├── [All files synced from Pi]
├── PROJECT_CONTEXT.md                 # This file - session context ⭐
├── GIT_WORKFLOW.md                    # How to sync with Pi
│
└── [PDFs - planning documents]
```

---

## 🔄 Git Workflow

### Setup (Complete ✅)
- Pi: Git initialized, master branch, initial commit made
- Local: Git initialized, main branch, synced to Pi master
- Remote: `pi-fish` pointing to `pi-fish:~/Development/fish-guardian`

### Common Operations

**Pull updates from Pi to local:**
```bash
cd /Users/Max/Desktop/max/coding/codingProjects/personalProjects/fish-guardian
git pull pi-fish master
```

**Commit changes on Pi:**
```bash
ssh pi-fish
cd ~/Development/fish-guardian
git add -A
git commit -m "Description of changes"
```

**View recent changes:**
```bash
ssh pi-fish "cd ~/Development/fish-guardian && git log --oneline -10"
```

### Last Commit
```
3e048cf - Initial commit - Week 4 complete
```

---

## 💡 Common Tasks & Commands

### System Management
```bash
# Check if tracking is running
ssh pi-fish 'sudo systemctl status fish-guardian'

# View live logs
ssh pi-fish 'sudo journalctl -u fish-guardian -f'

# Restart service
ssh pi-fish 'sudo systemctl restart fish-guardian'
```

### Data Analysis
```bash
# Generate 24-hour report
ssh pi-fish 'cd ~/Development/fish-guardian && source .venv/bin/activate && python3 -c "exec(open(\"generate_24h_report.py\").read())"'

# Recompute baselines (if needed after data changes)
ssh pi-fish 'cd ~/Development/fish-guardian && source .venv/bin/activate && python3 compute_baselines.py'

# Check data quality
ssh pi-fish 'cd ~/Development/fish-guardian && source .venv/bin/activate && python3 data_quality_analysis.py'
```

### Camera Viewing
```bash
# Quick method
ssh pi-fish 'cd ~/Development/fish-guardian && ./view_camera.sh'
# Then open: http://192.168.0.213:5000

# Note: Data collection pauses while camera stream is active
```

### Dashboard Management
```bash
# Access dashboard
open http://192.168.0.213:3000/d/fish-guardian-v7

# Recreate dashboard (if needed)
ssh pi-fish 'cd ~/Development/fish-guardian && source .venv/bin/activate && python3 create_dashboard_v7.py'
```

---

## 🚀 Next Steps - Phase 2 (AI Upgrade)

### Objectives
1. **Replace motion tracking with AI object detection**
   - Evaluate YOLOv8 vs EfficientDet
   - Train/fine-tune model on goldfish dataset
   - Implement in motion_track_influx.py

2. **Achieve persistent fish IDs**
   - Reduce from 2,898 IDs/day → ~7 stable IDs
   - Enable long-term per-fish health tracking
   - Individual fish naming/profiles

3. **Recompute baselines with stable IDs**
   - Generate baselines_v2.json with per-fish profiles
   - Update dashboard queries for individual fish
   - Create per-fish alert thresholds

4. **Enhanced monitoring**
   - Individual fish health dashboards
   - Anomaly detection per fish
   - Behavioral pattern recognition

### Procurement Needed
- See `Phase_2_Procurement_Checklist.pdf` for details
- Possible hardware: Coral TPU for edge inference
- Software: YOLOv8, training dataset, annotation tools

### Timeline Estimate
- **Week 5-6:** Model selection, dataset collection, training
- **Week 7-8:** Implementation, integration testing
- **Week 9-10:** Baseline recomputation, dashboard updates

---

## 📝 Session History

### Session 1: Week 4 Completion (Oct 14-21, 2025)
**Major Work:**
- Ran baseline computation on 5.85 days of data
- Created Grafana dashboard v7 from scratch
- Fixed 5+ dashboard panel issues:
  - System Status "no data" issue (5 attempted fixes)
  - Series limit errors on multiple panels
  - Aggregation query timeouts
  - Value mapping errors
- Generated 24-hour analysis reports
- Established Git version control
- Updated all documentation (README, PROJECT_CONTEXT, GIT_WORKFLOW)

**Key Learnings:**
- InfluxDB Flux aggregation is tricky - many functions kill results
- Grafana stat panels need exactly one value - use reduceOptions
- Motion-based tracking inherently creates high ID churn
- System Status vs Fish Activity Status are different concepts

**Decisions Made:**
- Keep "Fish Activity Status" with limitation documented (Option 3)
- Don't implement system heartbeat yet (defer to Phase 2)
- Use Pi as single source of truth for version control
- Maintain local git sync for reference/documentation

**Files Created/Modified:**
- ✅ README.md (updated with Week 4 completion)
- ✅ PROJECT_CONTEXT.md (this file - created)
- ✅ GIT_WORKFLOW.md (created)
- ✅ .gitignore (created)
- ✅ 24h_report.txt (generated)
- ✅ create_dashboard_v7.py (final working dashboard)
- ✅ fix_system_status_final.py (last panel fix attempt)

---

## 🎓 Technical Notes for Future Sessions

### InfluxDB Flux Query Tips
1. **Aggregation kills results:** Using `count() |> sum()` often returns zero results
2. **Let Grafana aggregate:** Return multiple series, use Grafana's reduceOptions
3. **group() before count:** `|> group() |> count()` often returns nothing
4. **Use first() per series:** Returns one value per fish_id, then Grafana can sum
5. **Avoid double map():** `|> map() |> map()` chain often breaks data flow

### Grafana Panel Configuration
1. **Stat panels need single value:** Use `reduceOptions: {calcs: ["sum"]}` to aggregate
2. **Value mappings format:** Grafana 10 uses `options` object, not old format
3. **Series limit errors:** Aggregate in query or Grafana, don't return 1000s of series
4. **Background colors:** Use `thresholds` not `mappings` for color-only changes

### Dashboard Panel IDs
- Panel 4 = Fish Activity Status (the problematic one)
- Panel IDs are assigned sequentially when creating dashboard
- UID = `fish-guardian-v7` for dashboard itself

### Motion Tracking Quirks
- Fish IDs are temporary (30s-5min lifespan)
- Ghost timeout allows resurrection within 5 minutes
- ROI masking excludes filter area (0,0)→(250,250)
- Background subtraction (MOG2) sensitive to lighting changes
- Half-resolution processing (640x360) maintains 20 FPS

---

## 📞 Quick Reference

| What | Where | How |
|------|-------|-----|
| **Live Dashboard** | Browser | http://192.168.0.213:3000/d/fish-guardian-v7 |
| **SSH to Pi** | Terminal | `ssh pi-fish` |
| **Check Service** | Pi SSH | `sudo systemctl status fish-guardian` |
| **View Logs** | Pi SSH | `sudo journalctl -u fish-guardian -f` |
| **Camera Stream** | Pi SSH | `cd ~/Development/fish-guardian && ./view_camera.sh` |
| **Pull Updates** | Local | `git pull pi-fish master` |
| **Project Docs** | Local or Pi | `~/Development/fish-guardian/README.md` |
| **This File** | Local or Pi | `~/Development/fish-guardian/PROJECT_CONTEXT.md` |

---

## 🎯 For Future Claude Sessions

When starting a new session, read this file to understand:
1. **Current project phase** (top of document)
2. **System architecture** (how everything connects)
3. **Known issues** (what's already been tried)
4. **File locations** (where to find things)
5. **Recent session history** (what was just completed)

**Update this file** at the end of each significant session with:
- New work completed
- Issues encountered and solutions
- Decisions made
- Files modified

This ensures continuity across sessions without losing context.

---

**Document Version:** 1.0
**Created:** October 21, 2025
**Last Session:** Week 4 Completion & Git Setup
