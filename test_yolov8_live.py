#!/usr/bin/env python3
"""Test YOLOv8 detection on live camera feed"""
from ultralytics import YOLO
from picamera2 import Picamera2
import cv2
import time

print("=" * 60)
print("YOLOv8 Goldfish Detection Test")
print("=" * 60)

# Load YOLOv8n model
print("\n[1/5] Loading YOLOv8n model...")
model = YOLO('yolov8n.pt')
print("Model loaded")

# Initialize camera
print("\n[2/5] Initializing camera...")
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (1280, 720), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(2)
print("Camera ready")

# Capture frame
print("\n[3/5] Capturing frame...")
frame = picam2.capture_array()
print(f"Frame captured: {frame.shape}")

# Run detection
print("\n[4/5] Running YOLOv8 inference...")
start_time = time.time()
results = model(frame, verbose=False)
inference_time = time.time() - start_time
fps = 1 / inference_time

print(f"Inference: {inference_time:.3f}s ({fps:.1f} FPS)")

# Analyze results
print("\n[5/5] Detection Results:")
print("-" * 60)

detections = results[0].boxes
print(f"Total detections: {len(detections)}")

if len(detections) > 0:
    class_counts = {}
    for box in detections:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        name = results[0].names[cls]
        
        if name not in class_counts:
            class_counts[name] = []
        class_counts[name].append(conf)
    
    print("\nDetected objects:")
    for name, confs in sorted(class_counts.items()):
        avg_conf = sum(confs) / len(confs)
        print(f"  {name}: {len(confs)} ({avg_conf:.1%} confidence)")

# Save image
annotated = results[0].plot()
cv2.imwrite('yolov8_goldfish_test.jpg', cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
print("\nSaved: yolov8_goldfish_test.jpg")

picam2.stop()
print("\nDone!")
