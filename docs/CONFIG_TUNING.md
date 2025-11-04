# Fish Guardian - Configuration Tuning Recommendations

## 5-Minute Test Results

### Current Performance
- **20 IDs created** in 5 minutes (~576 IDs/day)
- **1.1 FPS** overall (vs 6.3 FPS detection)
- **2-5 fish** detected per frame (out of 7 total)
- **Conf threshold**: 0.6 (too high)

### Comparison to Old System
- **Old MOG2**: 2,898 IDs/day
- **New YOLOv8**: ~576 IDs/day (projected)
- **Improvement**: 5x fewer IDs, but still not ideal goal of ~7-20 IDs/day

## Recommended Parameter Changes

### 1. Detection Threshold
```python
# Current
DETECTION_CONFIDENCE = 0.6

# Recommended
DETECTION_CONFIDENCE = 0.4  # Catches all 7 goldfish
```

**Rationale**: Multi-capture test showed confidences down to 0.41. Need 0.4 to detect all fish.

### 2. Track Timeout
```python
# Current
TRACK_TIMEOUT = 15.0  # Seconds before removing lost track

# Recommended
TRACK_TIMEOUT = 45.0  # Increased to handle longer occlusions
```

**Rationale**: At 1.1 FPS with 2-5 visible fish, individual fish can be occluded for 30-60 seconds. 15s timeout is too aggressive.

### 3. Ghost Timeout
```python
# Current
GHOST_TIMEOUT = 300.0  # 5 minutes

# Recommended
GHOST_TIMEOUT = 900.0  # 15 minutes
```

**Rationale**: Ghost resurrection is working well. Keeping ghosts longer will catch more re-entries instead of creating new IDs.

### 4. Association Distance
```python
# Current
MAX_ASSOC_DIST = 200  # pixels

# Recommended
MAX_ASSOC_DIST = 300  # pixels
```

**Rationale**: At 1.1 FPS (900ms between frames), goldfish can swim significant distances. 200px may be too restrictive.

### 5. Appearance Weight
```python
# Current
APPEARANCE_WEIGHT = 0.5

# Recommended
APPEARANCE_WEIGHT = 0.7  # Rely more on bbox size similarity
```

**Rationale**: Position is unreliable at 1.1 FPS. Bbox size is more stable for goldfish.

### 6. Min Track Age
```python
# Current
MIN_TRACK_AGE = 30.0  # Seconds before logging to DB

# Recommended
MIN_TRACK_AGE = 60.0  # Only log truly persistent tracks
```

**Rationale**: Filter out short-lived spurious tracks. Only log fish that persist for 1+ minute.

## Performance Bottleneck Analysis

### Frame Processing Breakdown
1. **rpicam-still capture**: ~100-200ms (subprocess + disk I/O)
2. **PIL Image.open**: ~50ms (disk read + decode)
3. **YOLOv8 detection**: ~160ms (EdgeTPU inference)
4. **Tracking logic**: ~20ms
5. **Frame limiting sleep**: ~650ms (to achieve 1.1 FPS target of 10 FPS)

**Total**: ~900ms per frame = 1.1 FPS

### Optimization Opportunities

1. **Eliminate disk I/O**: Capture directly to memory buffer
   ```python
   # Instead of: rpicam-still → file → PIL.Image.open
   # Use: rpicam-still --output - | numpy array
   ```
   **Expected gain**: +150ms = 1.7 FPS

2. **Remove frame limiting**: Let system run at natural speed
   ```python
   # Current: FPS_TARGET = 10 (artificially limited)
   # Recommended: FPS_TARGET = 3 (more realistic for disk-based capture)
   ```
   **Expected gain**: Run at natural 1.1 FPS without sleep overhead

3. **Reduce image resolution**:
   ```python
   # Current: 1280x720 → downscale to 640x640
   # Recommended: 640x640 → downscale to 640x640 (no downscale)
   ```
   **Expected gain**: +50ms = 1.3 FPS

## Test Plan

### Phase 1: Quick Fixes (No Code Changes)
1. Update `DETECTION_CONFIDENCE = 0.4`
2. Update `TRACK_TIMEOUT = 45.0`
3. Update `GHOST_TIMEOUT = 900.0`
4. Update `MAX_ASSOC_DIST = 300`
5. Run 10-minute test

**Expected Result**: 10-30 IDs (vs 40 IDs currently projected)

### Phase 2: Performance Optimization
1. Eliminate disk I/O (capture to memory)
2. Capture at 640x640 directly
3. Run 10-minute test

**Expected Result**: 2-3 FPS, 5-15 IDs

### Phase 3: Long-term Test
1. Run 24-hour test with Phase 1 or Phase 2 config
2. Monitor:
   - Total IDs created
   - Track persistence
   - False positive rate
   - InfluxDB data quality

**Success Criteria**: <100 IDs/day with 7 core persistent tracks

## Next Steps

1. ✅ Visual validation complete (annotated image saved)
2. ✅ 5-minute integration test complete
3. 🔄 Apply Phase 1 parameter tuning
4. ⏳ Run 10-minute test with new params
5. ⏳ Analyze and decide on Phase 2 optimizations
