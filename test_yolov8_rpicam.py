#!/usr/bin/env python3
"""Test YOLOv8 detection using rpicam-still for image capture"""
from ultralytics import YOLO
import cv2
import subprocess
import time
import os

print("=" * 60)
print("YOLOv8 Goldfish Detection Test (rpicam-still)")
print("=" * 60)

# Load YOLOv8n model
print("\n[1/4] Loading YOLOv8n model...")
model = YOLO('yolov8n.pt')
print("Model loaded")

# Capture frame using rpicam-still
print("\n[2/4] Capturing frame with rpicam-still...")
temp_image = '/tmp/goldfish_frame.jpg'

# Remove old image if exists
if os.path.exists(temp_image):
    os.remove(temp_image)

# Capture using rpicam-still (fast capture mode)
capture_start = time.time()
result = subprocess.run([
    'rpicam-still',
    '-o', temp_image,
    '--width', '1280',
    '--height', '720',
    '--timeout', '1',  # 1ms timeout for fast capture
    '-n'  # No preview
], capture_output=True, text=True)

capture_time = time.time() - capture_start

if result.returncode != 0 or not os.path.exists(temp_image):
    print(f"ERROR: Failed to capture image")
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    exit(1)

print(f"Frame captured in {capture_time:.3f}s")

# Read the captured image
frame = cv2.imread(temp_image)
if frame is None:
    print("ERROR: Failed to read captured image")
    exit(1)

print(f"Image loaded: {frame.shape}")

# Convert BGR to RGB for YOLOv8
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Run detection
print("\n[3/4] Running YOLOv8 inference...")
start_time = time.time()
results = model(frame_rgb, verbose=False)
inference_time = time.time() - start_time
fps = 1 / inference_time

print(f"Inference: {inference_time:.3f}s ({fps:.1f} FPS)")
print(f"Total time (capture + inference): {capture_time + inference_time:.3f}s")

# Analyze results
print("\n[4/4] Detection Results:")
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

    # Print detailed detection info
    print("\nDetailed detections:")
    for i, box in enumerate(detections):
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        name = results[0].names[cls]
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        print(f"  [{i+1}] {name} {conf:.2%} at ({int(x1)},{int(y1)})-({int(x2)},{int(y2)})")
else:
    print("\nNo objects detected")
    print("\nThis likely means one of:")
    print("  1. Pre-trained COCO model doesn't recognize goldfish")
    print("  2. Tank is not in frame or lighting is poor")
    print("  3. Need to fine-tune model on goldfish dataset")
    print("  4. Confidence threshold too high (currently 0.25)")

# Save annotated image
annotated = results[0].plot()
output_path = 'yolov8_goldfish_test.jpg'
cv2.imwrite(output_path, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
print(f"\nSaved annotated image: {output_path}")

# Cleanup
os.remove(temp_image)

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Review yolov8_goldfish_test.jpg to see what was detected")
print("2. If goldfish detected → Great! Proceed with tracking integration")
print("3. If NOT detected → Fine-tune YOLOv8 on goldfish dataset")
print("4. Week 5 Day 6-7: Capture 100+ sample images for evaluation")
print("\nExpected outcomes:")
print("  - COCO model may detect 'fish' class (class_id=1)")
print("  - OR may misclassify as 'bowl', 'vase', or 'orange'")
print("  - Fine-tuning will give better goldfish-specific results")
