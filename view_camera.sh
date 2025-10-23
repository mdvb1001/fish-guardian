#!/bin/bash
# Fish Guardian - Camera Viewer
# Quick script to view live camera feed

echo "======================================================================"
echo "Fish Guardian - Camera Stream"
echo "======================================================================"
echo ""
echo "This will:"
echo "  1. Stop the fish-guardian monitoring service"
echo "  2. Start the camera web stream"
echo "  3. Make it available at http://192.168.0.213:5000"
echo ""
echo "⚠️  WARNING: Data collection will be paused while viewing!"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Stopping fish-guardian service..."
sudo systemctl stop fish-guardian

echo "Starting camera stream..."
echo ""
echo "======================================================================"
echo "Camera stream is starting..."
echo "Access at: http://192.168.0.213:5000"
echo "======================================================================"
echo ""
echo "Press Ctrl+C when done viewing to stop the stream."
echo "Then run: sudo systemctl start fish-guardian"
echo ""

cd ~/Development/fish-guardian
source .venv/bin/activate
python3 camera_stream.py
