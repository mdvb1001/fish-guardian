#!/usr/bin/env python3
"""
Fish Guardian - AI-Powered Goldfish Detection with InfluxDB Integration
Monitors 7 goldfish using YOLOv8 EdgeTPU and logs metrics to InfluxDB
"""
import os
import time
import math
import subprocess
import tempfile
import numpy as np
from collections import deque, defaultdict
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
from PIL import Image

# Import goldfish detector
from goldfish_detector import GoldfishDetector

# --- Load Environment Variables ---
load_dotenv()
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG", "home")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "fish")

if not INFLUX_TOKEN:
    raise ValueError("INFLUX_TOKEN not set in .env file")

# --- Camera & Detection Parameters ---
FRAME_W, FRAME_H = 640, 640  # Phase 2A: Reduced resolution for better FPS
DETECTION_SIZE = 640              # YOLOv8 model input size
FPS_TARGET = 10                   # Target FPS (YOLOv8 @ 11.9 FPS)
MAX_ASSOC_DIST = 300              # Max pixel distance for track association (increased for 1.1 FPS)
TRACE_LEN = 12                    # Length of visual trail
TRACK_TIMEOUT = 45.0              # Seconds before removing lost track (increased to handle occlusions)
MIN_TRACK_AGE = 60.0              # Seconds before logging track to DB (filter spurious tracks)
GHOST_TIMEOUT = 900.0             # Keep lost tracks for 15 min (better resurrection)
APPEARANCE_WEIGHT = 0.7           # Weight for appearance vs position (rely more on bbox size)
DETECTION_CONFIDENCE = 0.4        # Minimum YOLOv8 confidence threshold (tuned to detect all 7 goldfish)

# YOLOv8 Model Configuration
# Use FLOAT32 model (1.2 FPS) for compatibility, or INT8 model (11.9 FPS) for speed
USE_INT8_MODEL = True  # Set to False to use FLOAT32 model (slower but more compatible)

if USE_INT8_MODEL:
    MODEL_PATH = 'models/goldfish_best_edgetpu_int8.tflite'
    EXPECTED_FPS = 11.9
else:
    MODEL_PATH = 'models/goldfish_best_edgetpu.tflite'
    EXPECTED_FPS = 1.2

# Initialize InfluxDB Client
print("Connecting to InfluxDB...")
try:
    influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    print(f"✓ Connected to InfluxDB at {INFLUX_URL}")
except Exception as e:
    print(f"✗ Failed to connect to InfluxDB: {e}")
    exit(1)

# Initialize Camera (using rpicam-still command instead of Picamera2 library)
print("Initializing Camera Module 3...")
print("Using rpicam-still for image capture (avoids libcamera Python binding issues)")
# Test camera with a quick capture
temp_image = tempfile.mktemp(suffix='.jpg')
try:
    subprocess.run([
        'rpicam-still', '-o', temp_image,
        '--width', str(FRAME_W), '--height', str(FRAME_H),
        '--timeout', '1', '-n'
    ], check=True, capture_output=True, timeout=5)
    os.remove(temp_image)
    print(f"✓ Camera initialized at {FRAME_W}x{FRAME_H}")
except Exception as e:
    print(f"✗ Failed to initialize camera: {e}")
    exit(1)

# Initialize YOLOv8 Goldfish Detector
print(f"Initializing YOLOv8 Detector...")
print(f"Model: {MODEL_PATH}")
print(f"Expected FPS: {EXPECTED_FPS}")
try:
    detector = GoldfishDetector(
        model_path=MODEL_PATH,
        conf_threshold=DETECTION_CONFIDENCE,
        use_edgetpu=True
    )
    print(f"✓ YOLOv8 Detector initialized")
except Exception as e:
    print(f"✗ Failed to initialize detector: {e}")
    print("  Try using FLOAT32 model instead (set USE_INT8_MODEL = False)")
    exit(1)

# Tracking State
next_id = 1
tracks = {}                       # id -> {'centroid': (x,y), 'trace': deque, 'bbox': (x,y,w,h), 'confidence': float}
last_seen = {}                    # id -> timestamp
track_birth_time = {}             # id -> timestamp when track was created
ghost_tracks = {}                 # Recently lost tracks for resurrection
per_minute_dist = defaultdict(float)  # id -> pixels moved this minute
per_minute_frames = defaultdict(int)  # id -> frames with motion
last_pos_for_dist = {}            # id -> (x,y)
minute_started = time.time()
total_frames_this_minute = 0

def euclid(p1, p2):
    """Euclidean distance between two points"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def bbox_to_centroid(bbox):
    """Convert YOLO bbox (x, y, w, h) to centroid"""
    x, y, w, h = bbox
    return (int(x + w/2), int(y + h/2))

def bbox_similarity(bbox1, bbox2):
    """
    Compute similarity between two bounding boxes based on size
    Returns value between 0 and 1 (1 = identical size)
    """
    _, _, w1, h1 = bbox1
    _, _, w2, h2 = bbox2

    area1 = w1 * h1
    area2 = w2 * h2

    if area1 == 0 or area2 == 0:
        return 0.0

    # Size similarity (ratio of smaller to larger)
    size_ratio = min(area1, area2) / max(area1, area2)

    return size_ratio

def flush_minute_metrics():
    """Flush aggregated per-minute metrics to InfluxDB"""
    global per_minute_dist, per_minute_frames, total_frames_this_minute

    now = time.time()
    points = []

    for fish_id in tracks.keys():
        if fish_id not in per_minute_dist:
            continue

        # Calculate metrics
        total_dist = per_minute_dist[fish_id]
        active_frames = per_minute_frames[fish_id]
        activity_pct = (active_frames / total_frames_this_minute * 100.0) if total_frames_this_minute > 0 else 0.0

        # Create InfluxDB point
        timestamp = now
        point = Point("fish_activity") \
            .tag("fish_id", str(fish_id)) \
            .field("distance_px", float(total_dist)) \
            .field("active_frames", int(active_frames)) \
            .field("activity_index", float(activity_pct)) \
            .time(int(timestamp * 1e9), WritePrecision.NS)

        points.append(point)

    if points:
        try:
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=points)
            print(f"[{time.strftime('%H:%M:%S')}] Flushed metrics for {len(points)} fish to InfluxDB")
        except Exception as e:
            print(f"[ERROR] Failed to write to InfluxDB: {e}")

    # Reset counters
    per_minute_dist = defaultdict(float)
    per_minute_frames = defaultdict(int)
    total_frames_this_minute = 0

print("="*70)
print("Fish Guardian - AI-Powered Detection Started")
print("="*70)
print(f"Detection Model: YOLOv8 EdgeTPU ({'INT8' if USE_INT8_MODEL else 'FLOAT32'})")
print(f"Expected FPS: {EXPECTED_FPS}")
print(f"Confidence Threshold: {DETECTION_CONFIDENCE}")
print(f"Logging to: {INFLUX_BUCKET} @ {INFLUX_URL}")
print(f"Min Track Age: {MIN_TRACK_AGE}s (logging filter)")
print(f"Ghost Timeout: {GHOST_TIMEOUT}s (ID resurrection)")
print("Press Ctrl+C to stop")
print("="*70)

frame_count = 0
start_time = time.time()
detect_times = deque(maxlen=30)  # Track detection performance

try:
    # Create temp file for image capture (reuse same file for performance)
    capture_image_path = tempfile.mktemp(suffix='.jpg')

    while True:
        loop_start = time.time()

        # Capture frame from camera using rpicam-still
        try:
            subprocess.run([
                'rpicam-still', '-o', capture_image_path,
                '--width', str(FRAME_W), '--height', str(FRAME_H),
                '--timeout', '1', '-n'
            ], check=True, capture_output=True, timeout=3)
        except subprocess.TimeoutExpired:
            print(f"[{time.strftime('%H:%M:%S')}] Camera timeout, skipping frame")
            continue
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Camera error: {e}")
            continue

        # Load captured image
        pil_image = Image.open(capture_image_path)

        # Run YOLOv8 detection
        detect_start = time.time()
        detections = detector.detect(pil_image)
        detect_time = time.time() - detect_start
        detect_times.append(detect_time)

        # Extract detection info
        detection_list = []
        for det in detections:
            bbox = det['bbox']  # (x, y, w, h)
            conf = det['confidence']
            centroid = bbox_to_centroid(bbox)
            detection_list.append((centroid, bbox, conf))

        # Associate detections with tracks
        unmatched_tracks = set(tracks.keys())
        unmatched_detections = list(range(len(detection_list)))
        assignments = []

        # Try to match with active tracks first
        for det_idx in list(unmatched_detections):
            ctr, bbox, conf = detection_list[det_idx]
            best_id, best_score = None, -1e9

            for tid in list(unmatched_tracks):
                # Position distance
                pos_dist = euclid(ctr, tracks[tid]['centroid'])
                pos_score = max(0, 1.0 - (pos_dist / MAX_ASSOC_DIST))

                # Bounding box similarity
                bbox_score = bbox_similarity(bbox, tracks[tid]['bbox'])

                # Combined score
                combined_score = (1 - APPEARANCE_WEIGHT) * pos_score + APPEARANCE_WEIGHT * bbox_score

                if combined_score > best_score and pos_dist <= MAX_ASSOC_DIST:
                    best_score = combined_score
                    best_id = tid

            if best_id is not None:
                assignments.append((best_id, det_idx))
                unmatched_tracks.discard(best_id)
                unmatched_detections.remove(det_idx)

        # Try to resurrect ghost tracks for unmatched detections
        for det_idx in list(unmatched_detections):
            ctr, bbox, conf = detection_list[det_idx]
            best_ghost_id, best_ghost_score = None, -1e9

            for ghost_id, ghost_data in ghost_tracks.items():
                pos_dist = euclid(ctr, ghost_data['centroid'])
                pos_score = max(0, 1.0 - (pos_dist / MAX_ASSOC_DIST))
                bbox_score = bbox_similarity(bbox, ghost_data['bbox'])
                combined_score = (1 - APPEARANCE_WEIGHT) * pos_score + APPEARANCE_WEIGHT * bbox_score

                if combined_score > best_ghost_score and pos_dist <= MAX_ASSOC_DIST:
                    best_ghost_score = combined_score
                    best_ghost_id = ghost_id

            if best_ghost_id is not None:
                # Resurrect ghost track
                assignments.append((best_ghost_id, det_idx))
                tracks[best_ghost_id] = ghost_tracks[best_ghost_id]
                del ghost_tracks[best_ghost_id]
                unmatched_detections.remove(det_idx)
                print(f"[{time.strftime('%H:%M:%S')}] Resurrected track ID={best_ghost_id}")

        # Update existing tracks
        now = time.time()
        for tid, det_idx in assignments:
            ctr, bbox, conf = detection_list[det_idx]

            # Update track
            if tid in tracks:
                tracks[tid]['trace'].append(ctr)
            else:
                # Resurrected track
                tracks[tid]['trace'] = deque([ctr], maxlen=TRACE_LEN)

            tracks[tid]['centroid'] = ctr
            tracks[tid]['bbox'] = bbox
            tracks[tid]['confidence'] = conf
            last_seen[tid] = now

            # Track movement for metrics
            if tid in last_pos_for_dist:
                dist = euclid(ctr, last_pos_for_dist[tid])
                per_minute_dist[tid] += dist
                per_minute_frames[tid] += 1
            last_pos_for_dist[tid] = ctr

        # Create new tracks for unmatched detections
        for det_idx in unmatched_detections:
            ctr, bbox, conf = detection_list[det_idx]
            tracks[next_id] = {
                'centroid': ctr,
                'trace': deque([ctr], maxlen=TRACE_LEN),
                'bbox': bbox,
                'confidence': conf
            }
            last_seen[next_id] = now
            track_birth_time[next_id] = now
            last_pos_for_dist[next_id] = ctr
            print(f"[{time.strftime('%H:%M:%S')}] New track ID={next_id} (conf={conf:.2f})")
            next_id += 1

        # Remove timed-out tracks
        lost_tracks = []
        for tid in list(tracks.keys()):
            if now - last_seen.get(tid, now) > TRACK_TIMEOUT:
                # Move to ghost tracks
                ghost_tracks[tid] = tracks[tid].copy()
                ghost_tracks[tid]['lost_at'] = now
                del tracks[tid]
                lost_tracks.append(tid)

        if lost_tracks:
            print(f"[{time.strftime('%H:%M:%S')}] Lost tracks: {lost_tracks}")

        # Clean up old ghost tracks
        for ghost_id in list(ghost_tracks.keys()):
            if now - ghost_tracks[ghost_id]['lost_at'] > GHOST_TIMEOUT:
                del ghost_tracks[ghost_id]

        # Flush metrics every 60 seconds
        total_frames_this_minute += 1
        if now - minute_started >= 60.0:
            flush_minute_metrics()
            minute_started = now

        # Performance stats
        frame_count += 1
        if frame_count % 30 == 0:
            elapsed = time.time() - start_time
            overall_fps = frame_count / elapsed
            avg_detect_ms = np.mean(detect_times) * 1000
            current_detect_fps = 1.0 / np.mean(detect_times) if np.mean(detect_times) > 0 else 0

            print(f"[{time.strftime('%H:%M:%S')}] "
                  f"Active: {len(tracks)}, Ghosts: {len(ghost_tracks)}, "
                  f"Detections: {len(detection_list)}, "
                  f"FPS: {overall_fps:.1f}, "
                  f"Detect: {avg_detect_ms:.1f}ms ({current_detect_fps:.1f} FPS)")

        # Frame rate limiting
        loop_time = time.time() - loop_start
        sleep_time = max(0, (1.0 / FPS_TARGET) - loop_time)
        if sleep_time > 0:
            time.sleep(sleep_time)

except KeyboardInterrupt:
    print("\n\nShutting down...")

    # Final metrics flush
    flush_minute_metrics()

    # Cleanup
    if os.path.exists(capture_image_path):
        os.remove(capture_image_path)
    influx_client.close()

    print("✓ Temp files cleaned up")
    print("✓ InfluxDB connection closed")
    print("Fish Guardian stopped cleanly")
