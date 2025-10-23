#!/usr/bin/env python3
"""
Motion detection and tracking using picamera2 and OpenCV
Tests multi-fish tracking without InfluxDB
"""
import cv2
import time
import math
import numpy as np
from collections import deque, defaultdict
from picamera2 import Picamera2

# --- Parameters ---
FRAME_W, FRAME_H = 1280, 720
MIN_CONTOUR_AREA = 2000          # adjust to ignore bubbles/noise - tuned for goldfish
MAX_ASSOC_DIST = 200             # px; max centroid distance to keep same ID - increased for fast swimming
TRACE_LEN = 12                   # for on-screen trails
MOG_HISTORY = 300                # frames
MOG_VAR_THRESHOLD = 40           # sensitivity - higher = less sensitive
TRACK_TIMEOUT = 15.0             # seconds before removing lost track - increased for goldfish pausing
GHOST_TIMEOUT = 60.0             # Keep lost tracks for 60s for potential resurrection
APPEARANCE_WEIGHT = 0.4          # Weight for appearance vs position (0.4 = 40% appearance, 60% position)

# Initialize camera
print("Initializing camera...")
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (FRAME_W, FRAME_H), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(2)  # warm-up

# Background subtractor
bg = cv2.createBackgroundSubtractorMOG2(
    history=MOG_HISTORY, 
    varThreshold=MOG_VAR_THRESHOLD, 
    detectShadows=True
)

# Track state
next_id = 1
tracks = {}  # id -> {'centroid': (x,y), 'trace': deque, 'features': {...}}
last_seen = {}  # id -> timestamp
track_birth_time = {}  # id -> timestamp when track was created
ghost_tracks = {}  # Recently lost tracks for resurrection: id -> {'features': {...}, 'lost_at': timestamp}
per_minute_dist = defaultdict(float)  # id -> pixels moved this minute
last_pos_for_dist = {}  # id -> (x,y)
minute_started = time.time()

def centroid_of(cnt):
    """Calculate centroid from contour"""
    x, y, w, h = cv2.boundingRect(cnt)
    return (int(x + w/2), int(y + h/2)), (x, y, w, h)

def euclid(a, b):
    """Euclidean distance between two points"""
    return math.hypot(a[0]-b[0], a[1]-b[1])

def extract_features(frame, box):
    """Extract appearance features from fish region"""
    x, y, w, h = box
    x = max(0, x)
    y = max(0, y)
    w = min(w, frame.shape[1] - x)
    h = min(h, frame.shape[0] - y)

    if w <= 0 or h <= 0:
        return None

    roi = frame[y:y+h, x:x+w]
    if roi.size == 0:
        return None

    area = w * h
    aspect_ratio = w / max(h, 1)
    roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hist_h = cv2.calcHist([roi_hsv], [0], None, [16], [0, 180])
    hist_s = cv2.calcHist([roi_hsv], [1], None, [8], [0, 256])
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

    area_diff = abs(feat1['area'] - feat2['area']) / max(feat1['area'], feat2['area'])
    area_sim = max(0, 1.0 - (area_diff / 0.3))

    ar_diff = abs(feat1['aspect_ratio'] - feat2['aspect_ratio']) / max(feat1['aspect_ratio'], feat2['aspect_ratio'])
    ar_sim = max(0, 1.0 - (ar_diff / 0.2))

    hist_h_corr = cv2.compareHist(feat1['hist_h'].reshape(-1, 1), feat2['hist_h'].reshape(-1, 1), cv2.HISTCMP_CORREL)
    hist_s_corr = cv2.compareHist(feat1['hist_s'].reshape(-1, 1), feat2['hist_s'].reshape(-1, 1), cv2.HISTCMP_CORREL)
    hist_h_sim = (hist_h_corr + 1) / 2.0
    hist_s_sim = (hist_s_corr + 1) / 2.0

    total_sim = (0.5 * (hist_h_sim + hist_s_sim) / 2.0) + (0.3 * area_sim) + (0.2 * ar_sim)
    return total_sim

print("="*60)
print("Motion Tracking Started (Press 'q' to quit)")
print("="*60)

try:
    while True:
        # Capture frame
        frame_rgb = picam2.capture_array()
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)  # OpenCV uses BGR
        
        # Apply background subtraction
        fg = bg.apply(frame)
        
        # Clean up mask
        fg = cv2.medianBlur(fg, 9)
        _, th = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
        # Erosion to eliminate small noise
        th = cv2.erode(th, np.ones((5,5), np.uint8), iterations=1)
        # Dilation to reconnect fish parts
        th = cv2.dilate(th, np.ones((3,3), np.uint8), iterations=1)
        
        # Find contours
        cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
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
                pos_dist = euclid(ctr, tracks[tid]['centroid'])
                pos_score = max(0, 1.0 - (pos_dist / MAX_ASSOC_DIST))
                app_score = appearance_similarity(features, tracks[tid].get('features'))
                combined_score = (1 - APPEARANCE_WEIGHT) * pos_score + APPEARANCE_WEIGHT * app_score

                if combined_score > best_score and pos_dist <= MAX_ASSOC_DIST:
                    best_score = combined_score
                    best_id = tid

            if best_id is not None and best_score >= 0.3:
                assignments.append((best_id, ctr, box, features, False))
                unmatched_tracks.discard(best_id)
                unmatched_detections.remove(det_idx)

        # Check ghost tracks for resurrection
        now = time.time()
        for det_idx in list(unmatched_detections):
            ctr, box, features = detections[det_idx]
            best_ghost_id, best_ghost_score = None, -1e9

            for ghost_id, ghost_data in ghost_tracks.items():
                if now - ghost_data['lost_at'] > GHOST_TIMEOUT:
                    continue
                app_score = appearance_similarity(features, ghost_data.get('features'))
                if app_score > best_ghost_score and app_score >= 0.6:
                    best_ghost_score = app_score
                    best_ghost_id = ghost_id

            if best_ghost_id is not None:
                assignments.append((best_ghost_id, ctr, box, features, True))
                unmatched_detections.remove(det_idx)

        # Create new tracks for remaining unmatched detections
        for det_idx in unmatched_detections:
            ctr, box, features = detections[det_idx]
            assignments.append((None, ctr, box, features, False))
        
        # Update existing & create new tracks
        for tid, ctr, box, features, resurrected in assignments:
            if tid is None:
                tid = next_id
                next_id += 1
                tracks[tid] = {
                    'centroid': ctr,
                    'trace': deque(maxlen=TRACE_LEN),
                    'features': features
                }
                last_pos_for_dist[tid] = ctr
                track_birth_time[tid] = time.time()
            elif resurrected:
                tracks[tid] = {
                    'centroid': ctr,
                    'trace': deque(maxlen=TRACE_LEN),
                    'features': features
                }
                if tid not in track_birth_time:
                    track_birth_time[tid] = ghost_tracks[tid].get('birth_time', time.time())
                last_pos_for_dist[tid] = ctr
                ghost_tracks.pop(tid, None)
            else:
                # Update existing track features
                old_features = tracks[tid].get('features')
                if old_features is not None:
                    tracks[tid]['features'] = {
                        'area': 0.8 * old_features['area'] + 0.2 * features['area'],
                        'aspect_ratio': 0.8 * old_features['aspect_ratio'] + 0.2 * features['aspect_ratio'],
                        'hist_h': 0.8 * old_features['hist_h'] + 0.2 * features['hist_h'],
                        'hist_s': 0.8 * old_features['hist_s'] + 0.2 * features['hist_s']
                    }
                else:
                    tracks[tid]['features'] = features

            # Distance accumulation
            prev = last_pos_for_dist.get(tid, ctr)
            per_minute_dist[tid] += euclid(prev, ctr)
            last_pos_for_dist[tid] = ctr

            tracks[tid]['centroid'] = ctr
            tracks[tid]['trace'].append(ctr)
            last_seen[tid] = time.time()

            # Draw
            x,y,w,h = box
            color = (0, 255, 255) if resurrected else (0, 255, 0)  # Yellow if resurrected
            cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
            cv2.putText(frame, f"ID {tid}", (x, y-6),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Move stale tracks to ghost_tracks for potential resurrection
        for tid in list(tracks.keys()):
            if now - last_seen.get(tid, now) > TRACK_TIMEOUT:
                if tracks[tid].get('features') is not None:
                    ghost_tracks[tid] = {
                        'features': tracks[tid]['features'],
                        'lost_at': now,
                        'birth_time': track_birth_time.get(tid, now)
                    }
                tracks.pop(tid, None)
                last_pos_for_dist.pop(tid, None)

        # Clean up old ghost tracks
        for ghost_id in list(ghost_tracks.keys()):
            if now - ghost_tracks[ghost_id]['lost_at'] > GHOST_TIMEOUT:
                ghost_tracks.pop(ghost_id, None)
                track_birth_time.pop(ghost_id, None)
        
        # Draw traces
        for tid, st in tracks.items():
            for i in range(1, len(st['trace'])):
                cv2.line(frame, st['trace'][i-1], st['trace'][i], (255, 255, 0), 2)
        
        # Display per-minute stats
        if now - minute_started >= 60.0:
            print(f"\n--- Per-Minute Movement ---")
            for tid, dist in sorted(per_minute_dist.items()):
                print(f"  Fish {tid}: {dist:.1f} pixels")
            per_minute_dist = defaultdict(float)
            minute_started = now

        # Add status overlay
        status_text = f"Active: {len(tracks)} | Ghost: {len(ghost_tracks)}"
        cv2.putText(frame, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Show frame
        cv2.imshow("Fish Motion Tracking", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print("Done!")
