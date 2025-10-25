# Coral TPU Optimization - Successfully Resolved

**Date:** October 25, 2025
**Status:** ✅ WORKING - EdgeTPU operational with TFLite 2.7.0

## Problem & Solution

### Original Issue
- **Problem:** Segmentation fault when loading EdgeTPU delegate
- **Root Cause:** Version mismatch between libedgetpu 16.0 (July 2021) and TFLite 2.14.0 (2023)
- **Error:** `Segmentation fault` when calling `load_delegate('libedgetpu.so.1')`

### Solution Implemented
- **Fix:** Downgraded TFLite from 2.14.0 to 2.7.0
- **Result:** EdgeTPU now works perfectly
- **Performance:** 202 FPS on MobileNet V2 (5ms inference)

## Current Configuration

### Working Setup
```bash
# Python environment
Python 3.9.19 (compiled from source)

# Package versions
tflite-runtime==2.7.0  # Downgraded from 2.14.0
pycoral==0.2.0
libedgetpu1-std==16.0  # System package

# Verified working
- EdgeTPU delegate loads successfully
- 202 FPS on MobileNet V2
- 5ms inference time
```

### Installation Commands
```bash
# In Python 3.9 virtual environment
pip uninstall -y tflite-runtime
pip install tflite-runtime==2.7.0
# pycoral already installed
```

## Benchmark Results

### EdgeTPU Performance (Verified)
| Model | Inference Time | FPS | Status |
|-------|---------------|-----|---------|
| MobileNet V2 (EdgeTPU) | 5ms | 202 FPS | ✅ Tested |
| YOLOv8n (CPU PyTorch) | 1547ms | 0.6 FPS | ✅ Tested |
| YOLOv8n (EdgeTPU) | ~30-50ms | 20-30 FPS | 📋 Projected |

## Next Steps for EdgeTPU Integration

### After Model Training (Week 7)
1. **Export trained YOLOv8 to TFLite**
   - Challenge: YOLOv8 export typically requires TF 2.8+
   - Solution: Export on different machine, then transfer

2. **Convert to EdgeTPU format**
   ```bash
   # Install compiler if not present
   curl -O https://packages.cloud.google.com/apt/doc/apt-key.gpg
   sudo apt-key add apt-key.gpg
   echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
   sudo apt update
   sudo apt install edgetpu-compiler

   # Compile model
   edgetpu_compiler goldfish_yolov8n.tflite
   # Output: goldfish_yolov8n_edgetpu.tflite
   ```

3. **Integration code template**
   ```python
   from tflite_runtime.interpreter import Interpreter
   from tflite_runtime.interpreter import load_delegate

   # Load EdgeTPU delegate
   delegate = load_delegate('libedgetpu.so.1')

   # Create interpreter
   interpreter = Interpreter(
       model_path='goldfish_yolov8n_edgetpu.tflite',
       experimental_delegates=[delegate]
   )
   interpreter.allocate_tensors()
   ```

## Important Notes

### Version Compatibility Matrix
| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.9.19 | ✅ Works |
| Python | 3.13 | ❌ Incompatible with PyCoral |
| TFLite Runtime | 2.7.0 | ✅ Works with EdgeTPU |
| TFLite Runtime | 2.14.0 | ❌ Segfault with EdgeTPU |
| libedgetpu | 16.0 | ✅ Current version |
| PyCoral | 0.2.0 | ✅ Works |
| NumPy | 1.26.4 | ✅ Downgraded from 2.0 |

### Known Limitations
1. **TFLite 2.7.0 constraint** - Older version but required for EdgeTPU
2. **Export challenge** - YOLOv8 → TFLite may need workaround
3. **Model size** - EdgeTPU has 8MB model size limit

## Testing Scripts Created

### 1. test_edgetpu_v2.py
- Verifies EdgeTPU delegate loads
- Status: ✅ PASSING

### 2. benchmark_edgetpu.py
- Benchmarks MobileNet V2 performance
- Result: 202 FPS achieved

### 3. test_yolov8_rpicam.py
- Tests YOLOv8 on camera (CPU)
- Result: 0.6 FPS, detected "vase" not goldfish

## Files to Preserve

```
~/Development/fish-guardian/
├── benchmark_edgetpu.py          # EdgeTPU benchmark script
├── test_edgetpu_v2.py            # EdgeTPU verification script
├── test_yolov8_rpicam.py        # YOLOv8 camera test
├── mobilenet_v2_1.0_224_quant_edgetpu.tflite  # Test model
└── yolov8n.onnx                  # ONNX export (for reference)
```

## Return to This After Training

**When to revisit:** Week 7 (after model training)
**Priority:** HIGH - Required for 15-20 FPS target
**Time estimate:** 2-4 hours for full integration

---

**Document created:** October 25, 2025
**Last tested:** October 25, 2025 - WORKING
**Author:** Claude (Fish Guardian Assistant)