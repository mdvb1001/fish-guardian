#!/usr/bin/env python3
"""
Fish Guardian - Motion Detection & Tracking with InfluxDB Integration
Monitors 7 goldfish using motion detection and logs metrics to InfluxDB
"""
import os
import time
import math
import cv2
import numpy as np
from collections import deque, defaultdict
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
from picamera2 import Picamera2

# --- Load Environment Variables ---
load_dotenv()
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG", "home")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "fish")

if not INFLUX_TOKEN:
    raise ValueError("INFLUX_TOKEN not set in .env file")

# --- Camera & CV Parameters ---
FRAME_W, FRAME_H = 1280, 720
PROCESS_W, PROCESS_H = 640, 360  # Half resolution for faster processing
FPS_TARGET = 20                  # Target FPS for processing
MIN_CONTOUR_AREA = 2000          # Full-res threshold (contours checked after resize)
MAX_ASSOC_DIST = 200             # Max pixel distance for track association - increased for fast swimming
TRACE_LEN = 12                   # Length of visual trail
MOG_HISTORY = 300                # Background subtractor history
MOG_VAR_THRESHOLD = 40           # Background subtractor sensitivity - higher = less sensitive
TRACK_TIMEOUT = 15.0             # Seconds before removing lost track - increased for goldfish pausing
MIN_TRACK_AGE = 30.0             # Seconds before logging track to DB - filters brief ghost tracks
GHOST_TIMEOUT = 300.0            # Keep lost tracks for 300s (5 min) - reduced ID churn by 56%
APPEARANCE_WEIGHT = 0.5          # Weight for appearance vs position (0.5 = 50/50 balance)

# ROI Mask Configuration - Exclude filter area (top-left corner)
ROI_MASK_ENABLED = True          # Enable/disable ROI masking
FILTER_X1, FILTER_Y1 = 0, 0      # Top-left corner of filter area
FILTER_X2, FILTER_Y2 = 250, 250  # Bottom-right corner of filter area (adjust based on tank)

# Initialize InfluxDB Client
print("Connecting to InfluxDB...")
try:
    influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    print(f"✓ Connected to InfluxDB at {INFLUX_URL}")
except Exception as e:
    print(f"✗ Failed to connect to InfluxDB: {e}")
    exit(1)

# Initialize Camera
print("Initializing Camera Module 3...")
try:
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": (FRAME_W, FRAME_H), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)  # Camera warm-up
    print(f"✓ Camera initialized at {FRAME_W}x{FRAME_H}")
except Exception as e:
    print(f"✗ Failed to initialize camera: {e}")
    exit(1)

# Background Subtractor (optimized - no shadow detection)
bg = cv2.createBackgroundSubtractorMOG2(
    history=200,  # Reduced from 300 for faster processing
    varThreshold=MOG_VAR_THRESHOLD,
    detectShadows=False  # Disabled for 2x speedup
)

# Create ROI Mask - Exclude filter area (for both resolutions)
roi_mask_full = np.ones((FRAME_H, FRAME_W), dtype=np.uint8) * 255
roi_mask_half = np.ones((PROCESS_H, PROCESS_W), dtype=np.uint8) * 255
if ROI_MASK_ENABLED:
    # Black out filter area (top-left corner) - full resolution
    roi_mask_full[FILTER_Y1:FILTER_Y2, FILTER_X1:FILTER_X2] = 0
    # Black out filter area - half resolution
    roi_mask_half[FILTER_Y1//2:FILTER_Y2//2, FILTER_X1//2:FILTER_X2//2] = 0
    print(f"✓ ROI Mask enabled - excluding filter area ({FILTER_X1},{FILTER_Y1}) to ({FILTER_X2},{FILTER_Y2})")
    print(f"✓ Processing at {PROCESS_W}x{PROCESS_H} for improved FPS")
else:
    print("✓ ROI Mask disabled - processing entire frame")

# Tracking State
next_id = 1
tracks = {}                      # id -> {'centroid': (x,y), 'trace': deque, 'features': {...}}
last_seen = {}                   # id -> timestamp
track_birth_time = {}            # id -> timestamp when track was created
ghost_tracks = {}                # Recently lost tracks for resurrection: id -> {'features': {...}, 'lost_at': timestamp}
per_minute_dist = defaultdict(float)  # id -> pixels moved this minute
per_minute_frames = defaultdict(int)  # id -> frames with motion
last_pos_for_dist = {}           # id -> (x,y)
minute_started = time.time()
total_frames_this_minute = 0

def euclid(a, b):
    """Euclidean distance between two points"""
    return math.hypot(a[0] - b[0], a[1] - b[1])

def centroid_of(cnt):
    """Calculate centroid from contour"""
    x, y, w, h = cv2.boundingRect(cnt)
    return (int(x + w/2), int(y + h/2)), (x, y, w, h)

def extract_features(frame, box):
    """Extract appearance features from fish region"""
    x, y, w, h = box

    # Ensure box is within frame bounds
    x = max(0, x)
    y = max(0, y)
    w = min(w, frame.shape[1] - x)
    h = min(h, frame.shape[0] - y)

    if w <= 0 or h <= 0:
        return None

    roi = frame[y:y+h, x:x+w]

    if roi.size == 0:
        return None

    # 1. Size (area of bounding box)
    area = w * h

    # 2. Aspect ratio (width/height)
    aspect_ratio = w / max(h, 1)

    # 3. Color histogram (HSV for better color representation)
    roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    # Use only Hue (color) and Saturation channels, ignore Value (brightness)
    hist_h = cv2.calcHist([roi_hsv], [0], None, [16], [0, 180])
    hist_s = cv2.calcHist([roi_hsv], [1], None, [8], [0, 256])

    # Normalize histograms
    cv2.normalize(hist_h, hist_h)
    cv2.normalize(hist_s, hist_s)

    return {
        'area': area,
        'aspect_ratio': aspect_ratio,
        'hist_h': hist_h.flatten(),
        'hist_s': hist_s.flatten()
    }

def appearance_similarity(feat1, feat2):
    """Calculate appearance similarity score (0-1, higher = more similar)"""
    if feat1 is None or feat2 is None:
        return 0.0

    # 1. Size similarity (allow 30% variation)
    area_diff = abs(feat1['area'] - feat2['area']) / max(feat1['area'], feat2['area'])
    area_sim = max(0, 1.0 - (area_diff / 0.3))  # 0.3 = 30% tolerance

    # 2. Aspect ratio similarity (allow 20% variation)
    ar_diff = abs(feat1['aspect_ratio'] - feat2['aspect_ratio']) / max(feat1['aspect_ratio'], feat2['aspect_ratio'])
    ar_sim = max(0, 1.0 - (ar_diff / 0.2))  # 0.2 = 20% tolerance

    # 3. Color histogram correlation
    hist_h_corr = cv2.compareHist(feat1['hist_h'].reshape(-1, 1), feat2['hist_h'].reshape(-1, 1), cv2.HISTCMP_CORREL)
    hist_s_corr = cv2.compareHist(feat1['hist_s'].reshape(-1, 1), feat2['hist_s'].reshape(-1, 1), cv2.HISTCMP_CORREL)

    # Normalize correlation from [-1,1] to [0,1]
    hist_h_sim = (hist_h_corr + 1) / 2.0
    hist_s_sim = (hist_s_corr + 1) / 2.0

    # Weighted average: color is most important, then size, then aspect ratio
    total_sim = (0.5 * (hist_h_sim + hist_s_sim) / 2.0) + (0.3 * area_sim) + (0.2 * ar_sim)

    return total_sim

def flush_metrics_to_influx(timestamp):
    """Write per-minute metrics to InfluxDB"""
    global per_minute_dist, per_minute_frames, total_frames_this_minute

    if total_frames_this_minute == 0:
        return

    points = []
    for tid in tracks.keys():
        # Only log tracks that have existed for at least MIN_TRACK_AGE seconds
        track_age = timestamp - track_birth_time.get(tid, timestamp)
        if track_age < MIN_TRACK_AGE:
            continue

        distance = per_minute_dist.get(tid, 0.0)
        frames_active = per_minute_frames.get(tid, 0)
        activity_pct = (frames_active / total_frames_this_minute) * 100.0 if total_frames_this_minute > 0 else 0.0

        point = Point("fish_activity") \
            .tag("fish_id", str(tid)) \
            .field("distance_px", float(distance)) \
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
print("Fish Guardian - Motion Tracking Started")
print("="*70)
print(f"Target FPS: {FPS_TARGET}")
print(f"Min Contour Area: {MIN_CONTOUR_AREA}")
print(f"Logging to: {INFLUX_BUCKET} @ {INFLUX_URL}")
print(f"Tracking Mode: Position + Appearance (Color/Size)")
print(f"Min Track Age: {MIN_TRACK_AGE}s (logging filter)")
print(f"Ghost Timeout: {GHOST_TIMEOUT}s (ID resurrection)")
print(f"ROI Mask: {'Enabled' if ROI_MASK_ENABLED else 'Disabled'}")
print("Press Ctrl+C to stop")
print("="*70)

frame_count = 0
start_time = time.time()

try:
    while True:
        loop_start = time.time()
        
        # Capture frame from camera
        frame_rgb = picam2.capture_array()
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Resize to half resolution for faster processing
        frame_small = cv2.resize(frame, (PROCESS_W, PROCESS_H))

        # Apply background subtraction on smaller frame
        fg = bg.apply(frame_small)

        # Apply ROI mask to exclude filter area
        if ROI_MASK_ENABLED:
            fg = cv2.bitwise_and(fg, fg, mask=roi_mask_half)

        # Clean up foreground mask - reduced kernel for half-res
        fg = cv2.medianBlur(fg, 3)  # Reduced from 9 to 3 for half-res
        _, th = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)

        # Erosion to eliminate small noise before dilation
        th = cv2.erode(th, np.ones((3, 3), np.uint8), iterations=1)  # Reduced from 5x5
        # Dilation to reconnect fish parts
        th = cv2.dilate(th, np.ones((2, 2), np.uint8), iterations=1)  # Reduced from 3x3

        # Resize mask back to full resolution for tracking
        th = cv2.resize(th, (FRAME_W, FRAME_H))
        
        # Find contours
        cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Extract detections with features
        detections = []
        for c in cnts:
            if cv2.contourArea(c) < MIN_CONTOUR_AREA:
                continue
            ctr, box = centroid_of(c)
            features = extract_features(frame, box)
            if features is not None:
                detections.append((ctr, box, features))
        
        # Associate detections using position + appearance
        unmatched_tracks = set(tracks.keys())
        unmatched_detections = list(range(len(detections)))
        assignments = []

        # Try to match with active tracks first
        for det_idx in list(unmatched_detections):
            ctr, box, features = detections[det_idx]
            best_id, best_score = None, -1e9

            for tid in list(unmatched_tracks):
                # Position distance (normalized to 0-1 range, inverted so lower distance = higher score)
                pos_dist = euclid(ctr, tracks[tid]['centroid'])
                pos_score = max(0, 1.0 - (pos_dist / MAX_ASSOC_DIST))

                # Appearance similarity (0-1, higher = more similar)
                app_score = appearance_similarity(features, tracks[tid].get('features'))

                # Combined score (weighted average)
                combined_score = (1 - APPEARANCE_WEIGHT) * pos_score + APPEARANCE_WEIGHT * app_score

                if combined_score > best_score and pos_dist <= MAX_ASSOC_DIST:
                    best_score = combined_score
                    best_id = tid

            # Require minimum combined score of 0.3
            if best_id is not None and best_score >= 0.3:
                assignments.append((best_id, ctr, box, features, False))  # False = not resurrected
                unmatched_tracks.discard(best_id)
                unmatched_detections.remove(det_idx)

        # Check ghost tracks for resurrection
        now = time.time()
        for det_idx in list(unmatched_detections):
            ctr, box, features = detections[det_idx]
            best_ghost_id, best_ghost_score = None, -1e9

            for ghost_id, ghost_data in ghost_tracks.items():
                # Only consider ghosts from last 60 seconds
                if now - ghost_data['lost_at'] > GHOST_TIMEOUT:
                    continue

                # Only use appearance for ghost matching (no position available)
                app_score = appearance_similarity(features, ghost_data.get('features'))

                if app_score > best_ghost_score and app_score >= 0.6:  # Higher threshold for resurrection
                    best_ghost_score = app_score
                    best_ghost_id = ghost_id

            if best_ghost_id is not None:
                assignments.append((best_ghost_id, ctr, box, features, True))  # True = resurrected
                unmatched_detections.remove(det_idx)

        # Create new tracks for remaining unmatched detections
        for det_idx in unmatched_detections:
            ctr, box, features = detections[det_idx]
            assignments.append((None, ctr, box, features, False))
        
        # Update tracks and accumulate metrics
        for tid, ctr, box, features, resurrected in assignments:
            if tid is None:
                # Create new track
                tid = next_id
                next_id += 1
                tracks[tid] = {
                    'centroid': ctr,
                    'trace': deque(maxlen=TRACE_LEN),
                    'features': features
                }
                last_pos_for_dist[tid] = ctr
                track_birth_time[tid] = time.time()
                print(f"[NEW] Fish ID {tid} detected")
            elif resurrected:
                # Resurrect from ghost tracks
                tracks[tid] = {
                    'centroid': ctr,
                    'trace': deque(maxlen=TRACE_LEN),
                    'features': features
                }
                # Restore original birth time if available
                if tid not in track_birth_time:
                    track_birth_time[tid] = ghost_tracks[tid].get('birth_time', time.time())
                last_pos_for_dist[tid] = ctr
                ghost_tracks.pop(tid, None)
                print(f"[RESURRECT] Fish ID {tid} reappeared (appearance match)")
            else:
                # Update existing track features (exponential moving average)
                old_features = tracks[tid].get('features')
                if old_features is not None:
                    # Blend old and new features (80% old, 20% new for stability)
                    tracks[tid]['features'] = {
                        'area': 0.8 * old_features['area'] + 0.2 * features['area'],
                        'aspect_ratio': 0.8 * old_features['aspect_ratio'] + 0.2 * features['aspect_ratio'],
                        'hist_h': 0.8 * old_features['hist_h'] + 0.2 * features['hist_h'],
                        'hist_s': 0.8 * old_features['hist_s'] + 0.2 * features['hist_s']
                    }
                else:
                    tracks[tid]['features'] = features

            # Update distance
            prev = last_pos_for_dist.get(tid, ctr)
            distance = euclid(prev, ctr)
            per_minute_dist[tid] += distance
            last_pos_for_dist[tid] = ctr

            # Update activity frame count
            if distance > 1.0:  # Only count if fish actually moved
                per_minute_frames[tid] += 1

            # Update track position
            tracks[tid]['centroid'] = ctr
            tracks[tid]['trace'].append(ctr)
            last_seen[tid] = time.time()
        
        # Move stale tracks to ghost_tracks for potential resurrection
        now = time.time()
        for tid in list(tracks.keys()):
            if now - last_seen.get(tid, now) > TRACK_TIMEOUT:
                track_age = now - track_birth_time.get(tid, now)
                print(f"[LOST] Fish ID {tid} - no motion for {TRACK_TIMEOUT}s (age: {track_age:.1f}s)")

                # Save to ghost tracks if it has features
                if tracks[tid].get('features') is not None:
                    ghost_tracks[tid] = {
                        'features': tracks[tid]['features'],
                        'lost_at': now,
                        'birth_time': track_birth_time.get(tid, now)
                    }

                # Remove from active tracking
                tracks.pop(tid, None)
                last_pos_for_dist.pop(tid, None)

        # Clean up old ghost tracks (older than GHOST_TIMEOUT)
        for ghost_id in list(ghost_tracks.keys()):
            if now - ghost_tracks[ghost_id]['lost_at'] > GHOST_TIMEOUT:
                print(f"[GHOST EXPIRED] Fish ID {ghost_id} - {GHOST_TIMEOUT}s since last seen")
                ghost_tracks.pop(ghost_id, None)
                track_birth_time.pop(ghost_id, None)
        
        # Check if minute elapsed
        total_frames_this_minute += 1
        if now - minute_started >= 60.0:
            flush_metrics_to_influx(now)
            minute_started = now
        
        # FPS control
        frame_count += 1
        elapsed = time.time() - loop_start
        sleep_time = max(0, (1.0 / FPS_TARGET) - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        # Periodic status
        if frame_count % 100 == 0:
            runtime = time.time() - start_time
            fps = frame_count / runtime
            print(f"[STATUS] {frame_count} frames | {fps:.1f} FPS | {len(tracks)} active | {len(ghost_tracks)} ghost")

except KeyboardInterrupt:
    print("\n\nShutting down...")
    # Flush remaining metrics
    if per_minute_dist:
        flush_metrics_to_influx(time.time())

finally:
    print("Cleaning up...")
    picam2.stop()
    influx_client.close()
    print("Done!")
