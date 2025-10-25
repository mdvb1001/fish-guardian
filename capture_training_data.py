#!/usr/bin/env python3
"""
Capture Training Data for Goldfish Detection
Collects images at regular intervals for YOLOv8 fine-tuning
"""

import os
import time
import subprocess
from datetime import datetime
import signal
import sys

# Configuration
OUTPUT_DIR = "training_data"
CAPTURE_INTERVAL = 30  # seconds between captures
TOTAL_IMAGES = 800  # target number of images
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720

# Time-of-day categories
def get_time_category():
    hour = datetime.now().hour
    if 6 <= hour < 10:
        return "morning"
    elif 10 <= hour < 14:
        return "midday"
    elif 14 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 22:
        return "evening"
    else:
        return "night"

# Create output directories
def setup_directories():
    categories = ["morning", "midday", "afternoon", "evening", "night"]
    for category in categories:
        path = os.path.join(OUTPUT_DIR, category)
        os.makedirs(path, exist_ok=True)

    # Create info file
    info_file = os.path.join(OUTPUT_DIR, "dataset_info.txt")
    with open(info_file, "w") as f:
        f.write(f"Dataset Collection Started: {datetime.now()}\n")
        f.write(f"Image Resolution: {IMAGE_WIDTH}x{IMAGE_HEIGHT}\n")
        f.write(f"Capture Interval: {CAPTURE_INTERVAL} seconds\n")
        f.write(f"Target Images: {TOTAL_IMAGES}\n")
        f.write("-" * 50 + "\n")

# Capture single image
def capture_image(image_number):
    category = get_time_category()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"goldfish_{timestamp}_{image_number:04d}.jpg"
    filepath = os.path.join(OUTPUT_DIR, category, filename)

    # Use rpicam-still to capture
    cmd = [
        'rpicam-still',
        '-o', filepath,
        '--width', str(IMAGE_WIDTH),
        '--height', str(IMAGE_HEIGHT),
        '--timeout', '1',
        '-n'  # No preview
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / 1024  # KB
            return True, category, file_size
        else:
            return False, category, 0
    except subprocess.TimeoutExpired:
        return False, category, 0
    except Exception as e:
        print(f"Error capturing image: {e}")
        return False, category, 0

# Signal handler for clean exit
def signal_handler(sig, frame):
    print("\n" + "=" * 60)
    print("Collection interrupted by user")
    print_summary()
    sys.exit(0)

# Print collection summary
def print_summary():
    print("\nCollection Summary:")
    print("-" * 40)
    total = 0
    for category in ["morning", "midday", "afternoon", "evening", "night"]:
        path = os.path.join(OUTPUT_DIR, category)
        if os.path.exists(path):
            count = len([f for f in os.listdir(path) if f.endswith('.jpg')])
            if count > 0:
                print(f"  {category:10s}: {count:4d} images")
                total += count
    print("-" * 40)
    print(f"  {'TOTAL':10s}: {total:4d} images")

    # Update info file
    info_file = os.path.join(OUTPUT_DIR, "dataset_info.txt")
    with open(info_file, "a") as f:
        f.write(f"\nCollection Ended: {datetime.now()}\n")
        f.write(f"Total Images Collected: {total}\n")

# Main collection loop
def main():
    print("=" * 60)
    print("GOLDFISH TRAINING DATA COLLECTION")
    print("=" * 60)
    print(f"\nTarget: {TOTAL_IMAGES} images")
    print(f"Interval: {CAPTURE_INTERVAL} seconds")
    print(f"Resolution: {IMAGE_WIDTH}x{IMAGE_HEIGHT}")
    print(f"Output: {OUTPUT_DIR}/")
    print("\nPress Ctrl+C to stop collection")
    print("-" * 60)

    # Setup
    signal.signal(signal.SIGINT, signal_handler)
    setup_directories()

    # Check if camera is available
    print("\nChecking camera...")
    success, _, _ = capture_image(0)
    if not success:
        print("ERROR: Camera not available")
        print("Make sure fish-guardian service is stopped:")
        print("  sudo systemctl stop fish-guardian.service")
        return

    print("Camera OK! Starting collection...\n")

    # Collection loop
    image_count = 1
    consecutive_failures = 0

    while image_count <= TOTAL_IMAGES:
        # Capture image
        success, category, size_kb = capture_image(image_count)

        if success:
            # Calculate progress
            progress = (image_count / TOTAL_IMAGES) * 100
            eta_seconds = (TOTAL_IMAGES - image_count) * CAPTURE_INTERVAL
            eta_hours = eta_seconds / 3600

            # Print status
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Image {image_count:04d}/{TOTAL_IMAGES} "
                  f"({progress:5.1f}%) - {category:10s} - {size_kb:6.1f}KB "
                  f"- ETA: {eta_hours:.1f}h")

            image_count += 1
            consecutive_failures = 0

            # Save progress every 10 images
            if image_count % 10 == 0:
                with open(os.path.join(OUTPUT_DIR, "dataset_info.txt"), "a") as f:
                    f.write(f"Progress: {image_count} images at {datetime.now()}\n")

        else:
            consecutive_failures += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Failed to capture image "
                  f"(attempt {consecutive_failures})")

            if consecutive_failures >= 5:
                print("\nERROR: Too many consecutive failures")
                print("Check if camera is being used by another process")
                break

        # Wait for next capture
        if image_count <= TOTAL_IMAGES:
            time.sleep(CAPTURE_INTERVAL)

    # Collection complete
    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE!")
    print_summary()
    print("\nNext steps:")
    print("1. Review collected images for quality")
    print("2. Upload to Roboflow for annotation")
    print("3. Annotate goldfish with bounding boxes")
    print("4. Export dataset in YOLOv8 format")
    print("=" * 60)

if __name__ == "__main__":
    main()