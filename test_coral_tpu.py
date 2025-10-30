#!/usr/bin/env python3
"""
Test Coral TPU with pre-compiled EdgeTPU model
Uses TFLite interpreter directly (no PyCoral needed)
"""
import numpy as np
import cv2
from picamera2 import Picamera2
import time

try:
    from tflite_runtime.interpreter import Interpreter
    from tflite_runtime.interpreter import load_delegate
except ImportError:
    print('tflite_runtime not installed, trying tensorflow.lite...')
    from tensorflow.lite.python.interpreter import Interpreter
    from tensorflow.lite.python.interpreter import load_delegate

# Load EdgeTPU model
print('Loading EdgeTPU model with Coral delegate...')
try:
    interpreter = Interpreter(
        model_path='ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite',
        experimental_delegates=[load_delegate('libedgetpu.so.1')]
    )
    print('✅ Coral TPU delegate loaded!')
except Exception as e:
    print(f'❌ Failed to load Coral TPU: {e}')
    print('Falling back to CPU...')
    interpreter = Interpreter(
        model_path='ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite'
    )

interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

print(f'Model input size: {width}x{height}')

# Initialize camera
print('Initializing camera...')
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={size: (1280, 720), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(2)

# Benchmark
print('Running benchmark (30 frames)...')
times = []

for i in range(30):
    # Capture frame
    frame = picam2.capture_array()
    
    # Preprocess
    input_data = cv2.resize(frame, (width, height))
    input_data = np.expand_dims(input_data, axis=0)
    
    # Inference
    start = time.time()
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    inference_time = time.time() - start
    
    times.append(inference_time)
    
    if (i + 1) % 10 == 0:
        avg_time = np.mean(times[-10:])
        fps = 1.0 / avg_time
        print(f'  Frame {i+1}/30: {avg_time*1000:.1f}ms ({fps:.1f} FPS)')

picam2.stop()

# Results
avg_time = np.mean(times)
fps = 1.0 / avg_time
print(f'\n📊 Results:')
print(f'  Average inference: {avg_time*1000:.1f}ms')
print(f'  Average FPS: {fps:.1f}')
print(f'  Min time: {min(times)*1000:.1f}ms')
print(f'  Max time: {max(times)*1000:.1f}ms')

if fps >= 15:
    print('  ✅ Fast enough for real-time tracking!')
else:
    print('  ⚠️  Too slow for real-time (need 15+ FPS)')
