# Coral TPU Optimization - Successfully Resolved

**Date:** October 25, 2025 (initial setup), November 2, 2025 (YOLOv8 integration complete)
**Status:** ✅ FULLY WORKING - YOLOv8 goldfish model running at 11.9 FPS on EdgeTPU

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
| MobileNet V2 (EdgeTPU) | 5ms | 202 FPS | ✅ Tested Oct 25 |
| YOLOv8n (CPU PyTorch) | 1547ms | 0.6 FPS | ✅ Tested Oct 25 |
| YOLOv8n Goldfish FLOAT32 (CPU) | 877ms | 1.1 FPS | ✅ Tested Nov 2 |
| **YOLOv8n Goldfish INT8 (EdgeTPU)** | **84ms** | **11.9 FPS** | **✅ Tested Nov 2** |

**Key Achievement:** 10.8x speedup over FLOAT32 model by using proper INT8 quantization!

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

## YOLOv8 EdgeTPU Integration (November 2, 2025)

### Challenge: FLOAT32 vs INT8 Quantization

**Problem Discovered:**
- Initial TFLite export using `format='tflite', int8=True` created models with FLOAT32 input/output layers
- Only internal weights were quantized to INT8
- EdgeTPU **cannot accelerate** models with FLOAT32 interfaces
- Result: 1.1 FPS (running on CPU, not TPU)

**Root Cause:**
YOLOv8's standard TFLite export doesn't create full integer quantization by default. The model structure was:
- Input layer: FLOAT32 (0-1 range)
- Internal weights: INT8 ✅
- Output layer: FLOAT32
- **EdgeTPU requirement:** INT8 for ALL layers (input, weights, output)

### Solution: Direct EdgeTPU Export

**Working Method:**
```python
# In Google Colab (Python 3.10+)
from ultralytics import YOLO

model = YOLO('goldfish_best.pt')
model.export(
    format='edgetpu',  # ← KEY: Use 'edgetpu' not 'tflite'
    imgsz=640,
)
```

This creates: `goldfish_best_full_integer_quant_edgetpu.tflite`

**Key Differences:**
| Export Method | Input Type | Output Type | EdgeTPU Accelerated | FPS |
|---------------|-----------|-------------|---------------------|-----|
| `format='tflite'` | FLOAT32 | FLOAT32 | ❌ No | 1.1 FPS |
| `format='edgetpu'` | **INT8** | **INT8** | ✅ Yes | **11.9 FPS** |

### INT8 Preprocessing Requirements

**Critical:** INT8 models require different preprocessing:

```python
import numpy as np
from PIL import Image

# Load image
image = Image.open('test.jpg')
image_resized = image.resize((640, 640), Image.LANCZOS)

# Convert UINT8 (0-255) to INT8 (-128 to 127)
input_data = np.array(image_resized, dtype=np.uint8).astype(np.float32)
input_data = (input_data - 128).astype(np.int8)
input_data = np.expand_dims(input_data, axis=0)

# Now set tensor
interpreter.set_tensor(input_details['index'], input_data)
```

**Common Mistake:** Trying to subtract 128 directly from UINT8 causes overflow to INT16.
**Solution:** Convert to FLOAT32 first, then subtract, then cast to INT8.

### Export Workflow (Colab Notebook)

Created: `goldfish_edgetpu_direct_export.ipynb`

**Steps:**
1. Upload `goldfish_best.pt` to Colab
2. Install EdgeTPU compiler (runs in Colab, not on Pi)
3. Export with `format='edgetpu'`
4. Download `goldfish_best_full_integer_quant_edgetpu.tflite`
5. Upload to Raspberry Pi

**Why Colab?**
- EdgeTPU compiler and onnx2tf require Python 3.10+
- Raspberry Pi uses Python 3.9.19 (incompatible)
- Colab has all dependencies pre-configured

### Files Created

**Models on Raspberry Pi:**
```
~/Development/fish-guardian/models/
├── goldfish_best.pt                      # 6.0 MB - PyTorch trained model
├── goldfish_best.onnx                    # 12 MB - ONNX intermediate
├── goldfish_best_int8.tflite             # 3.2 MB - FLOAT32 I/O (doesn't work)
├── goldfish_best_edgetpu.tflite          # 3.2 MB - FLOAT32 I/O (doesn't work)
└── goldfish_best_edgetpu_int8.tflite     # 3.4 MB - INT8 I/O (WORKS! 11.9 FPS)
```

**Colab Notebooks (on Desktop):**
```
~/Desktop/
├── goldfish_yolov8_training.ipynb         # Training notebook
├── goldfish_tflite_export.ipynb           # FLOAT32 export (didn't work)
├── goldfish_edgetpu_compile.ipynb         # EdgeTPU compiler (didn't work)
└── goldfish_edgetpu_direct_export.ipynb   # ✅ WORKING solution
```

### Troubleshooting Attempts (What Didn't Work)

1. **320x320 Resolution Test**
   - Captured at 320x320, upscaled to 640x640 for model
   - Result: Still 1.1 FPS (no improvement)
   - Reason: Model still processes 640x640 pixels

2. **EdgeTPU Compiler on Pi**
   - Attempted to install edgetpu-compiler on Pi
   - Failed: apt-key deprecated, GitHub URLs 404
   - Solution: Run compiler in Colab instead

3. **Two-Stage Export (TFLite → EdgeTPU)**
   - Export to TFLite first, then compile with edgetpu_compiler
   - Result: Still created FLOAT32 model
   - Solution: Use direct `format='edgetpu'` export

### Model Performance Metrics

**Training Results:**
- Dataset: 300 annotated goldfish images
- mAP50: 0.988 (98.8%) - Excellent!
- Precision: 0.965 (96.5%)
- Recall: 0.968 (96.8%)
- Training time: 10.9 minutes on Colab T4 GPU

**Inference Performance:**
- Input: 640x640 RGB images
- Output: (1, 5, 8400) - YOLOv8 detection format
- EdgeTPU Acceleration: ✅ Active
- Speed: 11.9 FPS (84ms per frame)
- Usability: Excellent for monitoring (checks fish ~12 times/second)

## Return to This After Training

**Status:** ✅ COMPLETE - YOLOv8 goldfish model working on EdgeTPU at 11.9 FPS
**Next Step:** Integrate into fish-guardian monitoring system
**Priority:** Ready for integration

---

**Document created:** October 25, 2025
**YOLOv8 integration:** November 2, 2025 - SUCCESS
**Last tested:** November 2, 2025 - 11.9 FPS achieved
**Author:** Claude (Fish Guardian Assistant)