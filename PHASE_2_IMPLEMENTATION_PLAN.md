# Phase 2 Implementation Plan - AI Upgrade

**Goal:** Replace motion-based tracking with AI object detection for persistent fish IDs

**Timeline:** 4-6 weeks
**Current Status:** Week 4 complete, ready to begin Phase 2
**Last Updated:** October 24, 2025

---

## 🎯 Phase 2 Objectives

### Primary Goals
1. **Persistent Fish IDs** - Reduce from 2,898 IDs/day → 7 stable IDs
2. **AI-Based Detection** - Replace MOG2 background subtraction with object detection
3. **Individual Tracking** - Enable per-fish health monitoring and baselines
4. **Maintained Performance** - Keep 15-20 FPS with Coral TPU acceleration

### Success Metrics
- ✅ Fish count consistently = 7 (±1)
- ✅ Fish IDs persist across frames (>95% consistency)
- ✅ FPS maintained at 15-20 (with Coral TPU)
- ✅ Per-fish baselines computed successfully
- ✅ Dashboard updated with individual fish panels

---

## 📋 Prerequisites Check

### Hardware Required
- [x] Raspberry Pi 4 Model B (already have)
- [x] Camera Module 3 (already have)
- [ ] **Coral USB Accelerator (Edge TPU)** - MUST ORDER
- [ ] Short USB 3.0 cable (0.3-1m)
- [ ] MicroSD 64-128GB U3 (for training data storage)
- [ ] Camera mount/stabilization

### Software Already Installed
- [x] Python 3.11
- [x] OpenCV
- [x] InfluxDB 2.7
- [x] Grafana 10.1
- [x] Git version control

### Software To Install
- [ ] EdgeTPU runtime (`libedgetpu1-std`)
- [ ] TFLite runtime (`tflite-runtime`)
- [ ] PyCoral (`pycoral`)
- [ ] PyTorch (for training, if doing custom model)
- [ ] Roboflow or LabelStudio (for annotation)

---

## 🗓️ Implementation Timeline

### Week 5: Hardware & Model Selection (Days 1-7)

**Day 1-2: Order Hardware**
- [ ] Order Coral USB Accelerator
- [ ] Order USB 3.0 cable
- [ ] Order additional MicroSD card if needed
- [ ] Estimated delivery: 3-7 days

**Day 3-5: Research & Selection**
- [ ] Test pre-trained models (no Coral needed yet):
  - YOLOv8n (Nano) - CPU inference
  - YOLOv8s (Small) - CPU inference
  - Evaluate detection accuracy on your goldfish
- [ ] Benchmark FPS on Pi 4 CPU (expect 2-5 FPS)
- [ ] Decide: pre-trained vs fine-tuning approach

**Day 6-7: Data Collection Planning**
- [ ] Set up image capture script
- [ ] Capture 100 sample images (day/night mix)
- [ ] Review detection quality
- [ ] Decision point: proceed with pre-trained or collect training data?

**Deliverables:**
- Hardware ordered
- YOLOv8 model tested on CPU
- Sample images captured
- Decision made on training approach

---

### Week 6: Model Preparation (Days 8-14)

**If Pre-Trained Model Path:**
- [ ] Download YOLOv8n pre-trained weights
- [ ] Convert to TFLite format
- [ ] Compile for EdgeTPU (when Coral arrives)
- [ ] Test inference speed on sample images

**If Fine-Tuning Path (Recommended):**

**Day 8-10: Dataset Collection**
- [ ] Capture 500-800 images from tank
  - Morning (100 images)
  - Midday (200 images)
  - Evening (200 images)
  - Night (100 images)
- [ ] Variety: feeding time, resting, active swimming
- [ ] Script: `capture_training_data.py`

**Day 11-13: Annotation**
- [ ] Set up Roboflow account (free tier)
- [ ] Upload images to Roboflow
- [ ] Annotate all 7 goldfish in each frame
  - Class: "goldfish"
  - Bounding boxes around each fish
- [ ] Export dataset in YOLOv8 format
- [ ] Estimated time: 3-5 hours

**Day 14: Model Training Setup**
- [ ] Set up training environment:
  - Local PC with GPU (if available), OR
  - Google Colab (free tier), OR
  - Kaggle notebooks (free)
- [ ] Install YOLOv8 training dependencies
- [ ] Prepare training script

**Deliverables:**
- 500-800 annotated images
- Dataset ready for training
- Training environment configured

---

### Week 7: Training & Optimization (Days 15-21)

**Day 15-17: Model Training**
- [ ] Fine-tune YOLOv8n on goldfish dataset
  - Base: COCO-pretrained YOLOv8n
  - Epochs: 50-100
  - Batch size: 16
  - Image size: 640x640
- [ ] Monitor training metrics (mAP, loss)
- [ ] Validate on test set (20% holdout)
- [ ] Expected training time: 2-4 hours on GPU

**Day 18-19: Model Conversion**
- [ ] Export trained model to ONNX
- [ ] Convert ONNX → TFLite
- [ ] Compile TFLite → EdgeTPU format
- [ ] Test inference on sample images
- [ ] Benchmark: expect 20-30 FPS with Coral

**Day 20-21: Integration Prep**
- [ ] Create new script: `motion_track_coral.py`
- [ ] Implement:
  - Model loading (PyCoral)
  - Frame preprocessing
  - Inference pipeline
  - Post-processing (NMS, confidence filtering)
- [ ] Test on recorded video first (not live)

**Deliverables:**
- Trained model (`goldfish_yolov8n.tflite`)
- EdgeTPU compiled model (`goldfish_yolov8n_edgetpu.tflite`)
- Integration script created
- Inference tested on video

---

### Week 8: Implementation & Testing (Days 22-28)

**Day 22-23: Fish ID Tracking Logic**
- [ ] Implement persistent ID assignment:
  - Track fish positions frame-to-frame
  - Use IoU (Intersection over Union) matching
  - Assign persistent IDs (fish_001 to fish_007)
  - Handle occlusions and temporary disappearances
- [ ] Test tracking stability on recorded video
- [ ] Measure ID consistency: target >95%

**Day 24-25: InfluxDB Integration**
- [ ] Update data schema:
  ```python
  Point("fish_activity_v2")
      .tag("fish_id", "fish_001")  # Stable ID
      .field("distance_px", float)
      .field("activity_index", float)
      .field("confidence", float)  # Detection confidence
      .field("bbox_area", float)    # Fish size
  ```
- [ ] Add new measurement alongside old one (don't break v1)
- [ ] Test data writing
- [ ] Monitor InfluxDB performance

**Day 26: Live Testing**
- [ ] Stop `fish-guardian` service
- [ ] Run `motion_track_coral.py` manually
- [ ] Monitor for 1-2 hours:
  - Fish count accuracy
  - ID stability
  - FPS performance
  - Error handling
- [ ] Review logs and debug issues

**Day 27: Systemd Service Update**
- [ ] Create new service: `fish-guardian-v2.service`
- [ ] Configure to run `motion_track_coral.py`
- [ ] Set up auto-restart on failure
- [ ] Enable and start service
- [ ] Monitor for 24 hours

**Day 28: Validation**
- [ ] Verify data collection (24h continuous)
- [ ] Check fish count consistency
- [ ] Measure ID churn (should be <10 IDs/day)
- [ ] Compare FPS vs v1 baseline
- [ ] Document any issues

**Deliverables:**
- `motion_track_coral.py` fully integrated
- Systemd service running
- 24 hours of stable data collection
- Validation metrics documented

---

### Week 9-10: Baseline Recomputation & Dashboard (Days 29-42)

**Day 29-31: Data Analysis**
- [ ] Collect 3-5 days of v2 data
- [ ] Analyze fish ID stability
- [ ] Identify the 7 persistent IDs
- [ ] Map fish IDs to physical fish (manual observation)
- [ ] Optionally name fish: "Goldie", "Bubbles", etc.

**Day 32-35: Baseline Recomputation**
- [ ] Create `compute_baselines_v2.py`
- [ ] Compute per-fish baselines:
  ```json
  {
    "fish_001": {
      "distance_px": {"p10": 150, "median": 1200, "p90": 3200},
      "activity_index": {"p10": 2, "median": 15, "p90": 40},
      "typical_size_px": 1850
    },
    "global": { ... }
  }
  ```
- [ ] Generate `baselines_v2.json`
- [ ] Compare to v1 baselines
- [ ] Document differences

**Day 36-40: Dashboard Updates**
- [ ] Create new dashboard: "Fish Guardian v2 - Individual Tracking"
- [ ] Panels:
  1. **Fish Count (Real-time)** - Should show 7
  2. **Individual Fish Activity** - 7 separate timeseries
  3. **Per-Fish Baseline Comparison** - Each fish vs their baseline
  4. **Fish Health Grid** - 7 stat panels (one per fish)
  5. **Most/Least Active Fish** - Rankings
  6. **Fish Size Tracking** - Detect growth over time
  7. **Anomaly Detection** - Flag unusual behavior per fish
  8. **Model Performance** - Detection confidence, FPS
- [ ] Create queries using `fish_activity_v2` measurement
- [ ] Deploy dashboard
- [ ] Test all panels

**Day 41-42: Documentation & Cleanup**
- [ ] Update README with v2 information
- [ ] Document model training process
- [ ] Create `TRAINING_GUIDE.md`
- [ ] Update PROJECT_CONTEXT.md
- [ ] Git commit all changes
- [ ] Push to GitHub

**Deliverables:**
- Per-fish baselines computed
- New dashboard deployed
- Complete documentation
- Phase 2 complete ✅

---

## 🔧 Technical Implementation Details

### Model Selection Rationale

**YOLOv8n (Nano) - RECOMMENDED**
- ✅ Fast (30+ FPS with Coral TPU)
- ✅ Lightweight (6 MB)
- ✅ Good accuracy for goldfish detection
- ✅ Easy to fine-tune
- ✅ Excellent EdgeTPU support

**Alternative: EfficientDet-Lite0**
- ✅ Designed for EdgeTPU
- ✅ Good accuracy
- ❌ Harder to fine-tune
- ❌ Less community support

**Decision: YOLOv8n** for flexibility and performance

---

### Architecture Changes

**Current (v1 - Motion-Based):**
```
Camera → MOG2 Background Subtraction → Contour Detection →
  Kalman Tracking → Temporary IDs → InfluxDB
```

**New (v2 - AI-Based):**
```
Camera → Frame Preprocessing → YOLOv8 Inference (Coral TPU) →
  Bounding Box Post-processing → IoU Tracking → Persistent IDs → InfluxDB
```

---

### Key Code Components

**1. Model Inference (PyCoral)**
```python
from pycoral.utils import edgetpu
from pycoral.adapters import common
from PIL import Image

# Load model
interpreter = edgetpu.make_interpreter('goldfish_yolov8n_edgetpu.tflite')
interpreter.allocate_tensors()

# Run inference
def detect_fish(frame):
    # Preprocess
    input_image = preprocess_frame(frame)
    common.set_input(interpreter, input_image)

    # Inference
    interpreter.invoke()

    # Get results
    boxes = get_output(interpreter, 0)  # Bounding boxes
    scores = get_output(interpreter, 1)  # Confidence scores

    return boxes, scores
```

**2. Fish ID Tracking**
```python
class FishTracker:
    def __init__(self):
        self.tracks = {}  # {fish_id: Track}
        self.next_id = 1

    def update(self, detections):
        # Match detections to existing tracks using IoU
        matched, unmatched = self.match_detections(detections)

        # Update matched tracks
        for track_id, detection in matched:
            self.tracks[track_id].update(detection)

        # Create new tracks for unmatched detections
        for detection in unmatched:
            if self.next_id <= 7:  # Only track up to 7 fish
                self.tracks[f"fish_{self.next_id:03d}"] = Track(detection)
                self.next_id += 1

        return self.tracks
```

**3. InfluxDB Schema**
```python
# Write point for each fish
for fish_id, track in tracker.items():
    point = Point("fish_activity_v2") \
        .tag("fish_id", fish_id) \
        .field("distance_px", track.distance_traveled) \
        .field("activity_index", track.activity_percentage) \
        .field("confidence", track.avg_confidence) \
        .field("bbox_area", track.bbox_area) \
        .field("x_position", track.x) \
        .field("y_position", track.y) \
        .time(timestamp)

    write_api.write(bucket="fish", record=point)
```

---

## 📊 Expected Improvements

### Metric Comparison (v1 vs v2)

| Metric | v1 (Motion) | v2 (AI Expected) | Improvement |
|--------|-------------|------------------|-------------|
| Fish IDs/day | 2,898 | ~7-10 | **99.7% reduction** |
| ID stability | 5-10 min | Hours-Days | **Persistent** |
| False positives | High (filter, bubbles) | Low | **Better accuracy** |
| FPS | 17-20 | 15-25 (w/ Coral) | **Comparable** |
| Per-fish tracking | ❌ Impossible | ✅ Enabled | **New capability** |
| Fish count accuracy | Variable | 7 ± 1 | **Accurate** |

---

## 🚨 Risk Mitigation

### Potential Issues & Solutions

**Issue 1: Coral TPU not detecting fish**
- **Cause:** Model not trained on goldfish specifically
- **Solution:** Fine-tune on custom dataset (Week 6)
- **Backup:** Use pre-trained COCO model, adjust confidence threshold

**Issue 2: Low FPS performance**
- **Cause:** Model too large, poor optimization
- **Solution:** Use YOLOv8n (smallest), optimize input size to 416x416
- **Backup:** Reduce camera resolution to 640x480

**Issue 3: Fish IDs still unstable**
- **Cause:** Occlusions, similar-looking fish
- **Solution:** Improve IoU matching, add appearance features (color histogram)
- **Backup:** Accept 10-15 stable IDs, filter out short-lived IDs

**Issue 4: Coral TPU overheating**
- **Cause:** Continuous inference, poor ventilation
- **Solution:** Add small fan, use `libedgetpu1-std` (not max clock)
- **Backup:** Throttle inference to 10 FPS during peak heat

---

## 💰 Budget Estimate

### Hardware
- Coral USB Accelerator: $60-75
- USB 3.0 cable: $5-10
- MicroSD 64GB U3: $15-20
- Camera mount: $10-20
- **Total Hardware: ~$100**

### Software
- Roboflow (free tier): $0
- Google Colab (free tier): $0
- **Total Software: $0**

### Time Investment
- Implementation: 40-60 hours over 6 weeks
- Training/annotation: 5-10 hours
- Testing/debugging: 10-15 hours
- **Total Time: ~60-80 hours**

---

## 📚 Resources & References

### Documentation
- **YOLOv8 Docs:** https://docs.ultralytics.com/
- **Coral Getting Started:** https://coral.ai/docs/accelerator/get-started/
- **PyCoral API:** https://coral.ai/docs/reference/py/
- **TFLite Conversion:** https://www.tensorflow.org/lite/models/convert

### Tutorials
- **YOLOv8 Fine-tuning:** https://blog.roboflow.com/how-to-train-yolov8-on-a-custom-dataset/
- **EdgeTPU Compilation:** https://coral.ai/docs/edgetpu/compiler/
- **Fish Tracking Examples:** GitHub search "fish tracking yolo"

### Community
- **Coral AI Forums:** https://coral.ai/community/
- **Ultralytics Discord:** YOLOv8 support community

---

## ✅ Phase 2 Checklist

### Pre-Implementation
- [ ] Order Coral USB Accelerator
- [ ] Install EdgeTPU runtime
- [ ] Test YOLOv8 on CPU
- [ ] Capture sample images

### Model Development
- [ ] Collect training dataset (500-800 images)
- [ ] Annotate images in Roboflow
- [ ] Train YOLOv8n model
- [ ] Convert to EdgeTPU format
- [ ] Validate inference speed

### Integration
- [ ] Create `motion_track_coral.py`
- [ ] Implement fish ID tracking
- [ ] Update InfluxDB schema
- [ ] Test live inference
- [ ] Create systemd service

### Validation
- [ ] 24-hour stability test
- [ ] Verify fish count = 7
- [ ] Measure ID persistence
- [ ] Benchmark FPS

### Baselines & Dashboard
- [ ] Collect 3-5 days of v2 data
- [ ] Compute per-fish baselines
- [ ] Create v2 dashboard
- [ ] Deploy all panels
- [ ] Validate metrics

### Documentation
- [ ] Update README
- [ ] Create TRAINING_GUIDE.md
- [ ] Update PROJECT_CONTEXT.md
- [ ] Git commit & push
- [ ] Celebrate completion! 🎉

---

## 🎯 Success Criteria

Phase 2 is considered **complete** when:

1. ✅ **Persistent IDs:** Same 7 fish IDs maintained for 24+ hours
2. ✅ **Accurate Count:** Fish count = 7 (±1) consistently
3. ✅ **Performance:** 15+ FPS with Coral TPU
4. ✅ **Data Quality:** Per-fish baselines computed successfully
5. ✅ **Dashboard:** Individual fish monitoring deployed
6. ✅ **Documentation:** Complete implementation guide created
7. ✅ **Service Stability:** Runs continuously for 7+ days without errors

---

**Next Step:** Order Coral USB Accelerator and begin Week 5 tasks!

**Document Version:** 1.0
**Created:** October 24, 2025
**Author:** Claude (Fish Guardian Assistant)
