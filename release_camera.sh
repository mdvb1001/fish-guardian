#!/bin/bash
# Fish Guardian Camera Release Helper
# Run this before manual testing to free the camera
# Usage: ./release_camera.sh

echo "============================================"
echo "Fish Guardian - Camera Release Helper"
echo "============================================"
echo ""

echo "[1/4] Stopping fish-guardian service..."
sudo systemctl stop fish-guardian
if [ $? -eq 0 ]; then
    echo "  ✓ Service stopped"
else
    echo "  ✗ Failed to stop service (may not be running)"
fi
echo ""

echo "[2/4] Stopping pipewire services..."
systemctl --user stop pipewire pipewire-pulse wireplumber 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Pipewire services stopped"
else
    echo "  ⚠ Pipewire services may not be running"
fi
echo ""

echo "[3/4] Stopping pipewire sockets..."
systemctl --user stop pipewire.socket pipewire-pulse.socket 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Pipewire sockets stopped"
else
    echo "  ⚠ Pipewire sockets may not be running"
fi
echo ""

echo "[4/4] Killing chromium if running..."
pkill chromium 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Chromium killed"
else
    echo "  ⚠ Chromium not running"
fi
echo ""

echo "============================================"
echo "✓ Camera should now be available!"
echo "============================================"
echo ""
echo "To test manually:"
echo "  cd ~/Development/fish-guardian"
echo "  source .venv/bin/activate"
echo "  python3 motion_track.py"
echo ""
echo "To restart fish-guardian service:"
echo "  sudo systemctl start fish-guardian"
echo ""
