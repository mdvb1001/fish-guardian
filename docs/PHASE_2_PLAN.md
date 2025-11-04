# Phase 2: Performance Optimization Plan

## Phase 1 Results Summary

### Tuned Parameters (Phase 1):
- **DETECTION_CONFIDENCE**: 0.4 (from 0.6)
- **TRACK_TIMEOUT**: 45s (from 15s)
- **GHOST_TIMEOUT**: 900s (from 300s)
- **MAX_ASSOC_DIST**: 300px (from 200px)
- **APPEARANCE_WEIGHT**: 0.7 (from 0.5)
- **MIN_TRACK_AGE**: 60s (from 30s)

### Results:
- **10-minute test**: 18 IDs created
- **Projected daily rate**: ~259 IDs/day
- **Improvement**: 55% reduction from untun Tuned (576 → 259 IDs/day)
- **Comparison to MOG2**: 91% reduction (2,898 → 259 IDs/day)

### Resurrection Working:
✅ Resurrected track IDs: 4, 8, 9
✅ Ghost system preventing some duplicate IDs
✅ Track persistence improving

### Remaining Issue:
❌ Still creating 259 IDs/day vs goal of 7-20 IDs/day
❌ Root cause: **1.1 FPS = 900ms frame gaps** cause association failures

## Root Cause Analysis

### Frame Processing Breakdown (Current):
1. **rpicam-still capture → disk**: ~150ms
2. **PIL Image.open from disk**: ~50ms
3. **YOLOv8 detection**: ~160ms
4. **Tracking logic**: ~20ms
5. **Frame limiting sleep**: ~520ms (targeting 10 FPS but achieving 1.1 FPS)

**Total**: ~900ms/frame = 1.1 FPS

### Why This Breaks Tracking:
At 1.1 FPS with goldfish swimming:
- Fish can move 200-500 pixels in 900ms
- MAX_ASSOC_DIST of 300px is barely adequate
- Position-based matching becomes unreliable
- Many "new" detections are actually existing fish

## Phase 2: Eliminate Disk I/O Bottleneck

### Strategy:
Capture directly to memory buffer instead of disk file.

### Current Flow (Disk-based):
```
rpicam-still → save to /tmp/xxx.jpg → PIL.Image.open(file) → numpy array
```

### Proposed Flow (Memory-based):
```
rpicam-still --output - --encoding rgb → stdout → numpy array → PIL.Image
```

### Implementation:
```python
def capture_to_memory(width=1280, height=720):
    """Capture image directly to memory without disk I/O"""
    import io

    # Capture to stdout in RGB format
    result = subprocess.run([
        'rpicam-still',
        '--output', '-',          # stdout
        '--encoding', 'rgb',      # Raw RGB (no JPEG compression)
        '--width', str(width),
        '--height', str(height),
        '--timeout', '1',
        '-n'
    ], capture_output=True, timeout=3, check=True)

    # Convert RGB bytes directly to numpy array
    img_array = np.frombuffer(result.stdout, dtype=np.uint8)
    img_array = img_array.reshape((height, width, 3))

    # Convert to PIL Image
    return Image.fromarray(img_array, 'RGB')
```

### Expected Improvements:
- **Eliminate disk I/O overhead**: +200ms
- **Target FPS**: 2.5-3.0 FPS (vs 1.1 FPS)
- **Frame gap**: 330-400ms (vs 900ms)
- **Track association**: Much more reliable with smaller gaps

### Expected ID Creation Rate:
- **Current**: 259 IDs/day
- **Projected with 3 FPS**: 50-100 IDs/day (60-80% reduction)
- **Closer to goal**: 7-20 IDs/day

## Phase 3 Alternative: Reduce Resolution

If Phase 2 doesn't achieve 3 FPS, try reducing camera resolution:

### Current:
```python
FRAME_W, FRAME_H = 1280, 720  # Capture at 720p
DETECTION_SIZE = 640           # Downscale to 640x640
```

### Proposed:
```python
FRAME_W, FRAME_H = 640, 640    # Capture at 640x640 directly
DETECTION_SIZE = 640           # No downscaling needed
```

### Expected Impact:
- **Faster capture**: ~100ms saved
- **No downscaling**: ~50ms saved
- **Target FPS**: 3.5-4.0 FPS
- **Trade-off**: Smaller field of view

## Implementation Plan

### Step 1: Implement Memory-Based Capture
1. Create `capture_to_memory()` function
2. Replace disk-based capture in main loop
3. Remove temp file cleanup
4. Test for 10 minutes

### Step 2: Evaluate Results
- If IDs < 100/day → SUCCESS, move to 24-hour test
- If 100-200 IDs/day → Try Phase 3 (reduce resolution)
- If > 200 IDs/day → Need deeper investigation

### Step 3: 24-Hour Production Test
- Deploy best configuration
- Monitor:
  - Total IDs created
  - Track persistence
  - InfluxDB data quality
  - System stability

## Success Criteria

- **Target**: < 100 IDs/day with 7 stable core tracks
- **Acceptable**: 50-150 IDs/day (still 95% better than MOG2)
- **Minimum**: < 300 IDs/day (88% better than MOG2)

## Next Steps

1. ✅ Phase 1 parameter tuning complete (259 IDs/day)
2. 🔄 Implement Phase 2 memory-based capture
3. ⏳ Run 10-minute test with Phase 2
4. ⏳ Evaluate and iterate
5. ⏳ 24-hour production test

