#!/usr/bin/env python3
"""
Camera detection script - finds the working camera device for OpenCV
"""
import cv2

def test_camera(device_index):
    """Test if a camera device works"""
    print(f"\nTesting device {device_index}...")
    cap = cv2.VideoCapture(device_index)
    
    if not cap.isOpened():
        print(f"  ✗ Cannot open device {device_index}")
        return False
    
    # Try to read a frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret or frame is None:
        print(f"  ✗ Device {device_index} opened but cannot read frames")
        return False
    
    print(f"  ✓ Device {device_index} works!")
    print(f"    Resolution: {frame.shape[1]}x{frame.shape[0]}")
    print(f"    Channels: {frame.shape[2] if len(frame.shape) > 2 else 1}")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Camera Device Detection")
    print("=" * 50)
    
    working_devices = []
    
    # Test common device indices
    for idx in range(5):
        if test_camera(idx):
            working_devices.append(idx)
    
    print("\n" + "=" * 50)
    if working_devices:
        print(f"✓ Working camera devices: {working_devices}")
        print(f"✓ Recommended: Use device {working_devices[0]}")
    else:
        print("✗ No working camera devices found!")
        print("  Check camera connection with: rpicam-hello")
    print("=" * 50)
