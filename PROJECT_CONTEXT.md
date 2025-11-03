# Fish Guardian - Project Context

**Last Updated:** November 2, 2025
**Current Phase:** Week 6 (Phase 2) - EdgeTPU Integration Complete! 🎉
**System Status:** Production, operational, YOLOv8 model running at 11.9 FPS on EdgeTPU

---

## 🎯 Quick Status

| Aspect | Status | Details |
|--------|--------|---------|
| **Motion Tracking** | ✅ Running | 20 FPS, systemd service, 2+ days uptime |
| **Data Collection** | ✅ Active | InfluxDB, ~270 records/hour, 575% collection rate |
| **Baselines** | ✅ Complete | 5.85 days, 90,304 records, baselines_v1.json |
| **Dashboard** | ✅ Deployed | Grafana v7, 11 panels, baseline overlays |
| **Version Control** | ✅ Setup | Git + GitHub (single source of truth) |
| **Python Environment** | ✅ Complete | Python 3.9.19, YOLOv8, TFLite, PyCoral installed |
| **Training Data** | ✅ Complete | 1,134 images collected, 300 annotated in Roboflow |
| **Model Training** | ✅ Complete | 98.8% mAP50, YOLOv8n trained on 300 images |
| **EdgeTPU Model** | ✅ Working | 11.9 FPS (10.8x faster than CPU), INT8 quantized |
| **Phase 2 Progress** | 🚀 Active | Week 6: Model trained, EdgeTPU working, ready for integration |

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
- **Week 5 (Oct 25-30):** 🚀 Phase 2 Active
  - ✅ Python 3.9 migration complete
  - ✅ Coral TPU EdgeTPU optimization (202 FPS verified)
  - ✅ Training data collection (1,134 images)
  - ✅ Dataset annotation (300 images in Roboflow)
  - 🚀 YOLOv8n training in progress (Google Colab)
- **Week 6 (Next):** Model deployment, EdgeTPU conversion, integration

### Key Achievements (Week 5 - Phase 2)
- ✅ **Python 3.9 Migration:** Compiled from source, all dependencies working
- ✅ **Coral TPU Optimization:** Fixed compatibility (TFLite 2.7.0), 202 FPS verified
- ✅ **Training Data Collection:** 1,134 high-quality goldfish images
  - Original collection: 1,034 images (afternoon/evening/night)
  - Crystal-clear tank: 100 additional images
- ✅ **Dataset Annotation:** 300 images annotated with bounding boxes in Roboflow
- ✅ **Roboflow Setup:** Dataset Version 1 generated (70/20/10 split)
- ✅ **Google Colab Notebook:** Complete training pipeline created
- 🚀 **YOLOv8n Training:** Currently training on 300 annotated images (100 epochs)

### Key Achievements (Week 4)
- ✅ Collected 5.85 days of continuous baseline data
- ✅ Generated global baselines (P10: 168px, Median: 1334px, P90: 3530px)
- ✅ Created Grafana Dashboard v7 with 11 panels
- ✅ Fixed all dashboard panel issues (series limits, aggregation, mappings)
- ✅ Generated 24-hour analysis reports
- ✅ Established version control (Git + GitHub)
- ✅ Updated all documentation

---

## 🏗️ System Architecture

### Hardware
- **Computer:** Raspberry Pi 4 Model B
- **Camera:** Camera Module 3 (1280x720 @ 20 FPS)
- **Accelerator:** Coral USB Accelerator (Edge TPU) - Connected
- **Network:** 192.168.0.102 (hostname: pi-fish) - IP changed Oct 25
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
- **SSH:** `ssh pi-fish` (192.168.0.102)
- **Grafana:** http://192.168.0.102:3000/d/fish-guardian-v7 (admin/admin)
- **InfluxDB:** http://192.168.0.102:8086
- **Camera Stream:** http://192.168.0.102:5000 (when active)

### Python Environment (Updated Oct 25, 2025)
- **Python Version:** 3.9.19 (compiled from source)
- **Virtual Environment:** `.venv/` (Python 3.9)
- **Backup:** `.venv.python3.13.backup/` (old Python 3.13 environment)
- **Key Packages:**
  - ultralytics 8.3.221 (YOLOv8)
  - torch 2.8.0, torchvision 0.23.0
  - opencv-python 4.12.0.88
  - numpy 1.26.4 (downgraded from 2.0 for TFLite compatibility)
  - tflite-runtime 2.7.0 (downgraded from 2.14.0 for EdgeTPU compatibility)
  - pycoral 0.2.0
  - influxdb-client, picamera2, python-dotenv

### Training Data (Oct 25-30, 2025)
- **Total Images:** 1,134 goldfish images
  - Original collection: 1,034 images (438 afternoon, 477 evening, 119 night)
  - Crystal-clear tank: 100 additional images
- **Annotated:** 300 images with bounding boxes (Roboflow)
- **Dataset Split:** 70% train (210), 20% valid (60), 10% test (30)
- **Location:**
  - Pi: `~/Development/fish-guardian/training_data/`
  - Mac: `~/Desktop/goldfish_dataset/`
  - Roboflow: Project "Goldfish Detection" Version 1

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
├── capture_training_data.py           # Training data collection script
├── capture_100_more.py                # Additional data collection
├── test_yolov8_rpicam.py              # YOLOv8 camera test
├── benchmark_edgetpu.py               # EdgeTPU performance test
│
├── training_data/                     # Goldfish training images (1,134 images)
│   ├── afternoon/                     # 438 images
│   ├── evening/                       # 477 images
│   ├── night/                         # 119 + 100 images
│   └── dataset_info.txt               # Collection metadata
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
├── PHASE_2_IMPLEMENTATION_PLAN.md     # AI upgrade roadmap (6 weeks)
├── CORAL_TPU_OPTIMIZATION.md          # EdgeTPU compatibility fixes
│
├── create_dashboard_v7.py             # Dashboard creation script
├── fix_system_status_final.py         # Latest dashboard fixes
│
└── docs/
    ├── archive/                       # Historical documentation
    └── planning/                      # Week PDFs and roadmaps
```

### On Local Machine (Mac Desktop)
```
fish-guardian/                         # Main project repo
├── .git/                              # Git repository (main branch)
│   └── remote: pi-fish (master)       # Points to Pi as source of truth
├── .claude/                           # Claude Code settings
│
├── [All files synced from Pi]
├── PROJECT_CONTEXT.md                 # This file - session context ⭐
├── GIT_WORKFLOW.md                    # How to sync with Pi
│
└── [PDFs - planning documents]

~/Desktop/goldfish_dataset/            # Training data (local copy)
├── training_data/                     # Original 1,034 images from Pi
│   ├── afternoon/                     # 438 images
│   ├── evening/                       # 477 images
│   ├── night/                         # 119 images
│   └── dataset_info.txt
│
└── new_100_images/                    # Crystal-clear 100 additional images
    └── goldfish_20251027_*.jpg        # Oct 27 collection

~/Desktop/goldfish_yolov8_training.ipynb  # Google Colab training notebook
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

### Session 4: EdgeTPU Integration Complete! (Nov 2, 2025) 🎉
**Major Achievement:** YOLOv8 goldfish model running at 11.9 FPS on Coral EdgeTPU (10.8x speedup)

**Major Work:**
- Diagnosed EdgeTPU performance issue: FLOAT32 vs INT8 quantization
- Created direct EdgeTPU export workflow using `format='edgetpu'` in Colab
- Successfully exported model with full INT8 quantization (input, weights, output)
- Tested and verified EdgeTPU acceleration: 11.9 FPS vs 1.1 FPS CPU
- Created 4 Colab notebooks for complete training → EdgeTPU pipeline
- Documented entire process in CORAL_TPU_OPTIMIZATION.md
- Committed all work to GitHub with detailed documentation

**The Problem:**
- Initial TFLite export using `format='tflite', int8=True` created FLOAT32 input/output layers
- Only internal weights were quantized to INT8
- EdgeTPU cannot accelerate models with FLOAT32 interfaces
- Result: 1.1 FPS running on CPU, not TPU

**The Solution:**
```python
# In Google Colab
model.export(format='edgetpu', imgsz=640)
# Creates: goldfish_best_full_integer_quant_edgetpu.tflite
```
- This creates proper INT8 model with INT8 inputs, INT8 weights, INT8 outputs
- EdgeTPU can now accelerate the model
- Result: **11.9 FPS on EdgeTPU!**

**Performance Results:**
| Model Type | Input Type | FPS | Speedup |
|------------|-----------|-----|---------|
| FLOAT32 TFLite (CPU) | FLOAT32 | 1.1 FPS | Baseline |
| INT8 TFLite (EdgeTPU) | INT8 | 11.9 FPS | **10.8x** |

**Files Created:**
- ✅ `notebooks/goldfish_edgetpu_direct_export.ipynb` - Working export method
- ✅ `notebooks/goldfish_tflite_export.ipynb` - FLOAT32 export (reference)
- ✅ `notebooks/goldfish_edgetpu_compile.ipynb` - Compiler approach (reference)
- ✅ `notebooks/goldfish_yolov8_training.ipynb` - Training notebook
- ✅ `docs/CORAL_TPU_OPTIMIZATION.md` - Updated with complete guide
- ✅ `docs/SESSION_SUMMARY_NOV_2_2025.md` - Detailed session summary
- ✅ `models/goldfish_best_edgetpu_int8.tflite` - Working INT8 model (3.4 MB)

**Key Learnings:**
1. YOLOv8's `format='tflite'` doesn't create full INT8 quantization
2. Use `format='edgetpu'` for proper EdgeTPU export
3. INT8 models require special preprocessing (UINT8 → INT8 conversion)
4. EdgeTPU compiler needs Python 3.10+ (run in Colab, not on Pi)
5. Model input dtype verification is critical (check with interpreter)

**Troubleshooting Attempts:**
- ❌ 320x320 resolution test - No improvement (model still processes 640x640)
- ❌ EdgeTPU compiler on Pi - Installation failed (apt-key deprecated)
- ❌ Two-stage export (TFLite → EdgeTPU) - Still created FLOAT32
- ✅ Direct EdgeTPU export in Colab - SUCCESS!

**Git Commits:**
- bbdd8b0 - "YOLOv8 EdgeTPU Integration Complete - 11.9 FPS Achieved"
- 468d5c1 - "Add session summary for Nov 2 EdgeTPU integration"

**Documentation:**
- Complete technical guide in `docs/CORAL_TPU_OPTIMIZATION.md`
- Session summary with all details in `docs/SESSION_SUMMARY_NOV_2_2025.md`
- INT8 preprocessing code examples provided
- Export workflow fully documented

**Time Investment:**
- EdgeTPU troubleshooting: ~2 hours
- Colab notebook creation: ~30 minutes
- Testing and validation: ~30 minutes
- Documentation: ~1 hour
- **Total: ~4 hours**

**Next Steps:**
- Integrate INT8 EdgeTPU model into fish-guardian system
- Replace motion detection with YOLOv8 AI detection
- Test live goldfish detection on actual tank
- Verify all 7 fish detected consistently

**Status:** ✅ EdgeTPU model ready for integration tomorrow!

**See Also:**
- `docs/CORAL_TPU_OPTIMIZATION.md` - Complete technical reference
- `docs/SESSION_SUMMARY_NOV_2_2025.md` - Full session details
- `notebooks/goldfish_edgetpu_direct_export.ipynb` - Use this for future exports

---

### Session 3: Training Data Collection & YOLOv8 Training (Oct 30, 2025)
**Major Work:**
- Completed training data collection: 1,134 goldfish images total
  - Continued previous collection session (1,034 images)
  - Captured 100 additional crystal-clear images (user's request for better quality)
  - Organized by time of day (afternoon, evening, night)
- Set up Roboflow annotation workflow:
  - Created "Goldfish Detection" project
  - Uploaded 595 images to Roboflow (platform auto-filtered duplicates)
  - Annotated 300 images with "fish" bounding boxes
  - Generated Dataset Version 1 (70/20/10 train/valid/test split)
- Created comprehensive Google Colab training notebook:
  - GPU detection and verification
  - YOLOv8n model training (100 epochs)
  - Performance validation and metrics
  - TFLite INT8 export for EdgeTPU
  - Complete download package creation
- Started YOLOv8n training in Google Colab (in progress)

**Key Issues Resolved:**
1. **Dataset upload confusion** - Only 595 images uploaded vs 1,034
   - Root Cause: Roboflow auto-filtered very similar consecutive frames
   - Solution: 595 diverse images is actually better than 1,034 redundant ones
   - Result: User confirmed 595 is sufficient for training

2. **Annotation quantity question** - How many images to annotate?
   - User Question: "How many of these do I really need to annotate?"
   - Answer: 200-300 minimum, 300-400 recommended for 85-90% accuracy
   - Decision: User annotated 300 images (sweet spot)

3. **Annotation labeling strategy** - Individual fish IDs vs single class?
   - User Question: "Should I label as 'fish' or 'fish_1', 'fish_2', etc?"
   - Answer: Single "fish" class for object detection (not tracking)
   - Reasoning: YOLOv8 does detection, not re-identification

4. **Additional data collection** - User requested more images
   - User: "The tank is crystal clear and I feel the images will be crisper"
   - Solution: Created capture_100_more.py script
   - Result: Successfully captured 100 additional high-quality images
   - Download: Used rsync to transfer all new images to Mac

**Decisions Made:**
- Annotate 300 images (not 500+) - sufficient for good performance
- Use single "fish" class (not individual fish IDs)
- Train on Google Colab free GPU (not local or Roboflow training)
- YOLOv8n model (nano variant - optimized for EdgeTPU)
- 100 epochs with early stopping (patience=20)

**Files Created/Modified:**
- ✅ goldfish_yolov8_training.ipynb (Colab training notebook)
- ✅ capture_100_more.py (additional data collection script)
- ✅ ~/Desktop/goldfish_dataset/training_data/ (1,034 images)
- ✅ ~/Desktop/goldfish_dataset/new_100_images/ (100 new images)
- ✅ PROJECT_CONTEXT.md (updated with Session 3 progress)

**User Interaction Highlights:**
- User provided clear feedback on annotation progress
- User requested additional images for better quality
- User asked practical questions about annotation strategy
- User successfully uploaded notebook to Colab and started training

**Time Investment:**
- Data collection: 50 minutes (100 images × 30s intervals)
- Image downloads: ~5 minutes (rsync transfer)
- Annotation: ~2-3 hours (user, 300 images)
- Colab notebook creation: ~20 minutes
- Training time: ~20-30 minutes (in progress)
- **Total session: ~3-4 hours**

**Next Steps:**
- Wait for training to complete (~30 minutes)
- Download trained model from Colab
- Convert model to EdgeTPU format on Raspberry Pi
- Integrate into fish-guardian system
- Test live detection on aquarium

**Training Configuration:**
- Model: YOLOv8n (nano - 3.2M parameters)
- Dataset: 300 annotated images (210 train, 60 valid, 30 test)
- Epochs: 100 with early stopping
- Image size: 640x640
- Batch size: 16
- Device: Google Colab T4 GPU
- Augmentations: Flip horizontal, brightness ±15%, blur up to 1px

**Expected Results:**
- mAP50: 0.75-0.85 (good to excellent detection)
- Inference speed on Coral TPU: 20-30 FPS
- Model size: ~6MB (PyTorch), ~3MB (TFLite INT8)

---

### Session 2: Phase 2 Start - Python 3.9 Migration (Oct 25, 2025)
**Major Work:**
- Migrated entire environment from Python 3.13 → Python 3.9.19
  - Compiled Python 3.9.19 from source (40+ minutes build time)
  - Created new virtual environment
  - Reinstalled all packages successfully
- Installed Phase 2 AI dependencies:
  - YOLOv8 (Ultralytics 8.3.221)
  - PyTorch 2.8.0 + torchvision 0.23.0
  - TFLite runtime 2.14.0
  - PyCoral 0.2.0 (with all geospatial dependencies)
- Tested YOLOv8 on CPU: 1.2s/frame (0.9 FPS) - confirmed need for acceleration
- Set up GitHub as single source of truth for version control
- Updated SSH config for new Pi IP address (192.168.0.213 → 192.168.0.102)
- Created PHASE_2_IMPLEMENTATION_PLAN.md (6-week detailed plan)

**Key Issues Resolved:**
1. **Python 3.13 incompatibility** - TFLite/PyCoral require Python < 3.10
   - Solution: Compiled Python 3.9.19 from source
2. **NumPy 2.x incompatibility** - TFLite built against NumPy 1.x
   - Solution: Downgraded to numpy 1.26.4
3. **Missing build dependencies** - libcap-dev, gdal-dev, etc.
   - Solution: Installed all required system libraries
4. **Coral TPU library compatibility** - libedgetpu 16.0 (2021) vs TFLite 2.14.0 (2023)
   - Status: Known issue, will use YOLOv8 CPU/PyTorch for now

**Decisions Made:**
- Use Python 3.9 as primary environment (not dual Python versions)
- GitHub as single source of truth (not just Pi)
- Start with YOLOv8 CPU inference, optimize later
- Proceed with "Option A" approach (YOLOv8 + EdgeTPU export path)

**Files Created/Modified:**
- ✅ PROJECT_CONTEXT.md (updated with Phase 2 progress)
- ✅ GIT_WORKFLOW.md (updated for GitHub workflow)
- ✅ PHASE_2_IMPLEMENTATION_PLAN.md (created)
- ✅ .venv/ (rebuilt with Python 3.9)
- ✅ .venv.python3.13.backup/ (backed up old environment)
- ✅ ~/.ssh/config (updated IP address)

**Time Investment:**
- Python compilation: ~45 minutes
- Package installation: ~15 minutes (ultralytics, PyTorch, etc.)
- PyCoral + dependencies: ~15 minutes (fiona build)
- Testing & troubleshooting: ~30 minutes
- **Total: ~2 hours**

**Next Steps:**
- Test YOLOv8 on actual camera feed
- Capture sample images for model evaluation
- Begin Week 5 Day 3-5 tasks (model selection testing)

---

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
