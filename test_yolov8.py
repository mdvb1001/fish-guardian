#!/usr/bin/env python3
"""
Test YOLOv8 detection on current camera frame
"""
from ultralytics import YOLO
from picamera2 import Picamera2
import cv2
import time

print("Loading YOLOv8n model (pre-trained on COCO)...")
model = YOLO('yolov8n.pt')  # Will auto-download if not present

print("Initializing camera...")
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (1280, 720), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(2)

print("Capturing frame...")
frame = picam2.capture_array()

print("Running YOLOv8 inference...")
start_time = time.time()
results = model(frame, verbose=False)
inference_time = time.time() - start_time

print(f"Inference time: {inference_time:.3f}s ({1/inference_time:.1f} FPS)")
print(f"Detections: {len(results[0].boxes)}")

# Show detected objects
for box in results[0].boxes:
    cls = int(box.cls[0])
    conf = float(box.conf[0])
    name = results[0].names[cls]
    print(f"  - {name}: {conf:.2f}")

# Save annotated image
annotated = results[0].plot()
cv2.imwrite('yolov8_test.jpg', cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
print("Saved: yolov8_test.jpg")

picam2.stop()
print("Done!")
