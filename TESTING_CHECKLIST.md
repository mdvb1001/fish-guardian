# Week 2 Testing Checklist

## ✅ Pre-Flight Checks

### 1. Verify InfluxDB is Running
```bash
systemctl status influxdb
curl http://localhost:8086/health
```
Expected: Active (running) + healthy response

### 2. Verify Grafana is Running
```bash
systemctl status grafana-server
```
Expected: Active (running)

### 3. Test Camera
```bash
cd ~/Development/fish-guardian
source .venv/bin/activate
python3 cam_test.py
```
Expected: ✓ SUCCESS! Camera captures frames

---

## 🐠 Testing Motion Tracking

### Test 1: Standalone Motion Tracking (No Database)
This runs tracking without writing to InfluxDB - good for initial testing.

```bash
cd ~/Development/fish-guardian
source .venv/bin/activate
python3 motion_track.py
```

**What to look for:**
- Window opens showing camera feed
- Green boxes appear around moving objects
- Fish IDs appear above boxes
- Yellow trails follow fish
- Console shows "[NEW] Fish ID X detected" when fish appear
- Press 'q' to quit

**Troubleshooting:**
- If no boxes appear: Water may be too still, wave hand over tank
- If too many boxes: Increase MIN_CONTOUR_AREA in script
- If boxes flicker: Adjust lighting to be more consistent

---

### Test 2: Full System with InfluxDB
This is the production script that logs data.

```bash
cd ~/Development/fish-guardian
source .venv/bin/activate
python3 motion_track_influx.py
```

**What to look for:**
- "✓ Connected to InfluxDB"
- "✓ Camera initialized"
- "[NEW] Fish ID X detected" as fish are tracked
- Every 60 seconds: "[HH:MM:SS] Flushed metrics for X fish to InfluxDB"
- "[STATUS]" updates every 100 frames showing FPS
- Press Ctrl+C to stop

**Let it run for 2-3 minutes** to collect data, then stop with Ctrl+C.

---

### Test 3: Verify Data in InfluxDB
```bash
/tmp/influx query 'from(bucket:"fish") 
  |> range(start: -1h) 
  |> filter(fn: (r) => r._measurement == "fish_activity")
  |> limit(n:10)' --org home
```

**Expected output:** Table showing fish_id, distance_px, activity_index values

---

## 📊 Setup Grafana Dashboard

1. **Open Grafana:**
   - URL: http://192.168.0.213:3000
   - Login: admin / admin (change password when prompted)

2. **Add Data Source:**
   - Settings → Data Sources → Add Data Source
   - Choose "InfluxDB"
   - Configuration:
     - Query Language: **Flux**
     - URL: http://localhost:8086
     - Organization: home
     - Token: (from .env file)
     - Default Bucket: fish
   - Click "Save & Test" → should see ✓

3. **Create Dashboard:**
   - See `grafana_setup.md` for detailed panel configurations
   - Create at least one panel with this query:
   ```flux
   from(bucket: "fish")
     |> range(start: -6h)
     |> filter(fn: (r) => r._measurement == "fish_activity")
     |> filter(fn: (r) => r._field == "distance_px")
   ```

---

## 🚀 Enable Auto-Start Service

**Only do this AFTER testing works!**

```bash
# Start the service
sudo systemctl start fish-guardian

# Check status
sudo systemctl status fish-guardian

# View live logs
sudo journalctl -u fish-guardian -f

# If everything looks good, it's already enabled to start on boot!
# To disable auto-start: sudo systemctl disable fish-guardian
```

---

## 🔧 Tuning Parameters

After running for a while, you may want to adjust:

### In `motion_track_influx.py`:

**Too many false detections (bubbles, reflections):**
```python
MIN_CONTOUR_AREA = 300  # Increase from 200
MOG_VAR_THRESHOLD = 20  # Increase from 16
```

**Missing fish:**
```python
MIN_CONTOUR_AREA = 150  # Decrease from 200
MOG_VAR_THRESHOLD = 12  # Decrease from 16
```

**Fish IDs change too often:**
```python
MAX_ASSOC_DIST = 120    # Increase from 80
```

After editing, restart the service:
```bash
sudo systemctl restart fish-guardian
```

---

## 📝 Expected Normal Operation

After 5-10 minutes of running:
- ✅ 5-7 fish IDs being tracked
- ✅ Metrics flushed every 60 seconds
- ✅ ~15-20 FPS processing speed
- ✅ Data visible in Grafana
- ✅ No error messages in logs

---

## 🆘 Common Issues

### "INFLUX_TOKEN not set"
- Check .env file exists: `ls -la ~/Development/fish-guardian/.env`
- Verify token is in file: `cat ~/Development/fish-guardian/.env`

### "Failed to connect to InfluxDB"
- Check InfluxDB is running: `systemctl status influxdb`
- Verify port 8086 is open: `curl http://localhost:8086/health`

### "Camera initialization failed"
- Check camera connection: `rpicam-hello --list-cameras`
- Verify /dev/video devices exist: `ls -la /dev/video*`

### Service won't start
- Check logs: `sudo journalctl -u fish-guardian -n 50`
- Test script manually first: `python3 motion_track_influx.py`

---

## ✨ Success Criteria

Week 2 is complete when:
- [x] Camera captures frames reliably
- [x] Motion detection identifies fish
- [x] Tracking assigns and maintains fish IDs
- [x] Metrics write to InfluxDB every minute
- [x] Grafana displays data from InfluxDB
- [x] System runs automatically on boot
- [x] Can tune parameters for your specific setup

**Next:** Week 3 - Dashboard refinement and baseline collection!
