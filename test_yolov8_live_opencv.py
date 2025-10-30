#!/usr/bin/env python3
"""Test YOLOv8 detection on live camera feed using OpenCV"""
from ultralytics import YOLO
import cv2
import time

print("=" * 60)
print("YOLOv8 Goldfish Detection Test (OpenCV)")
print("=" * 60)

# Load YOLOv8n model
print("\n[1/5] Loading YOLOv8n model...")
model = YOLO('yolov8n.pt')
print("Model loaded")

# Initialize camera
print("\n[2/5] Initializing camera...")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Allow camera to warm up
time.sleep(2)

# Check if camera opened successfully
if not cap.isOpened():
    print("ERROR: Cannot open camera")
    exit(1)

print("Camera ready")

# Capture frame
print("\n[3/5] Capturing frame...")
ret, frame = cap.read()
if not ret:
    print("ERROR: Cannot read frame")
    cap.release()
    exit(1)

print(f"Frame captured: {frame.shape}")

# Convert BGR to RGB (YOLOv8 expects RGB)
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Run detection
print("\n[4/5] Running YOLOv8 inference...")
start_time = time.time()
results = model(frame_rgb, verbose=False)
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
    print("This likely means:")
    print("  - Pre-trained COCO model doesn't recognize goldfish")
    print("  - Need to fine-tune model on goldfish dataset")
    print("  - OR adjust confidence threshold (currently 0.25)")

# Save annotated image
annotated = results[0].plot()
# Convert RGB back to BGR for cv2.imwrite
cv2.imwrite('yolov8_goldfish_test.jpg', cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
print("\nSaved: yolov8_goldfish_test.jpg")

# Cleanup
cap.release()
print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Review yolov8_goldfish_test.jpg to see what was detected")
print("2. If goldfish detected → Great! Proceed with integration")
print("3. If NOT detected → Need to fine-tune model on goldfish dataset")
print("4. Week 5 Day 6-7: Capture 100 sample images for evaluation")
