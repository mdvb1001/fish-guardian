#!/usr/bin/env python3
"""
Camera test using picamera2 (recommended for Camera Module 3)
"""
import cv2
import numpy as np
from picamera2 import Picamera2

def test_camera():
    """Test camera capture with picamera2"""
    print("=" * 60)
    print("Camera Module 3 Test (using picamera2)")
    print("=" * 60)
    
    try:
        # Initialize camera
        print("\n[1/4] Initializing camera...")
        picam2 = Picamera2()
        
        # Configure for 1280x720 (good balance for fish monitoring)
        print("[2/4] Configuring camera (1280x720)...")
        config = picam2.create_preview_configuration(
            main={"size": (1280, 720), "format": "RGB888"}
        )
        picam2.configure(config)
        
        # Start camera
        print("[3/4] Starting camera...")
        picam2.start()
        
        # Capture a test frame
        print("[4/4] Capturing test frame...")
        frame = picam2.capture_array()
        
        # Verify frame
        if frame is not None and frame.size > 0:
            print(f"\n✓ SUCCESS!")
            print(f"  Frame shape: {frame.shape}")
            print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
            print(f"  Channels: {frame.shape[2] if len(frame.shape) > 2 else 1}")
            print(f"  Data type: {frame.dtype}")
            
            # Test OpenCV compatibility
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            print(f"\n✓ OpenCV processing works!")
            print(f"  Grayscale shape: {gray.shape}")
            
            result = True
        else:
            print("\n✗ FAILED: Could not capture frame")
            result = False
        
        # Cleanup
        picam2.stop()
        print("\n✓ Camera stopped")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        result = False
    
    print("=" * 60)
    return result

if __name__ == "__main__":
    success = test_camera()
    exit(0 if success else 1)
