# Baseline Data Collection Guide
**Fish Guardian - Week 4**

## 🌙 Overnight Collection - You're All Set!

### ✅ System Status (Verified):
- Service is **RUNNING** and will auto-restart on failure
- Data logging every 60 seconds
- 48 GB disk space available
- InfluxDB running normally
- Appearance tracking + ghost resurrection active

### 📊 What's Being Collected:
**Every minute, for each fish:**
- `distance_px`: Total pixels moved
- `activity_index`: % of time moving (0-100%)
- `fish_id`: Fish identifier
- Timestamp

**Expected overnight data:**
- ~6,000-9,000 data points
- ~1-2 MB of storage
- Complete activity timeline

---

## 🌅 Morning Analysis

### Quick Check (30 seconds):
```bash
# SSH into Pi
ssh pi-fish

# Check if service ran all night
sudo systemctl status fish-guardian

# See last few log entries
sudo journalctl -u fish-guardian -n 20
```

### Full Baseline Analysis (2 minutes):
```bash
cd ~/Development/fish-guardian
source .venv/bin/activate
python3 /tmp/morning_baseline_analysis.py
```

**This script will show you:**
1. **Data Collection Summary** - How many points were collected
2. **Day vs Night Patterns** - Activity differences (fish should be less active at night)
3. **Activity Ranges** - Min/max/average movement (suggests alert thresholds)
4. **Fish Rankings** - Which fish are most/least active
5. **Data Quality** - Any gaps in collection

---

## 🎯 What You're Looking For

### Good Baseline Indicators:
- ✅ **80%+ data collection rate** - System ran reliably
- ✅ **2-3x day/night ratio** - Fish more active during day (normal for goldfish)
- ✅ **Clear activity ranges** - Can set meaningful alert thresholds
- ✅ **All fish showing activity** - No completely inactive fish
- ✅ **<5% data gaps** - Reliable continuous monitoring

### What Different Patterns Mean:

**Normal Goldfish Behavior:**
- **Daytime:** 800-3000 px/min average, 20-40% activity index
- **Nighttime:** 100-500 px/min average, 5-15% activity index
- **Activity peaks:** Around feeding times
- **Quiet periods:** Late night, early morning

**Concerning Patterns:**
- 🔴 **One fish much less active** - Possible health issue
- 🔴 **No day/night difference** - Lighting issue or stress
- 🔴 **Overall very low activity** - Water quality check needed
- 🔴 **Large data gaps** - Service crashed (check logs)

---

## 📈 Using Grafana for Analysis

**Dashboard URL:** http://localhost:3000

### Morning Review Checklist:
1. **Change time range to "Last 24 hours"**
2. **Look at Fish Movement graph:**
   - Should see lower activity during night (flat lines)
   - Higher activity during day (more variance)
3. **Check Low Activity Alert panel:**
   - Should show GREEN most of daytime
   - ORANGE/YELLOW at night is normal
4. **Review Recent Fish Activity table:**
   - All fish should have recent entries
   - Wide range of distances is healthy

---

## 📋 Daily Baseline Log (Days 1-7)

For each day, note:

**Day 1 (Date: ________):**
- Average daytime movement: ________ px/min
- Average nighttime movement: ________ px/min
- Most active fish ID: ________
- Least active fish ID: ________
- Any unusual observations: ________________________________

**Day 2 (Date: ________):**
- Average daytime movement: ________ px/min
- Average nighttime movement: ________ px/min
- Most active fish ID: ________
- Least active fish ID: ________
- Any unusual observations: ________________________________

*(Continue for Days 3-7)*

---

## 🔧 Troubleshooting

### If service stopped overnight:
```bash
# Check why it stopped
sudo journalctl -u fish-guardian --since "yesterday" | grep -i error

# Restart it
sudo systemctl restart fish-guardian

# Verify it's running
systemctl status fish-guardian
```

### If no data was collected:
1. Check InfluxDB is running: `systemctl status influxdb`
2. Check service logs: `sudo journalctl -u fish-guardian -n 50`
3. Verify camera access: Try running `python3 motion_track.py` manually
4. Check .env file: `cat ~/Development/fish-guardian/.env`

### If data looks weird:
- Check if lights were left on/off unexpectedly
- Verify camera hasn't moved
- Look for maintenance activities (filter cleaning, water change, etc.)
- Check if anyone fed fish at unusual times

---

## 📊 Week 4 Goal

**Primary Objective:** Establish normal activity baseline

**Success Criteria:**
- [ ] 5-7 days of continuous data collection
- [ ] Clear day/night activity patterns observed
- [ ] All fish showing consistent activity
- [ ] Identify normal ranges for your specific fish
- [ ] No major system interruptions

**After baseline established:**
- Update Grafana alert thresholds to match YOUR fish patterns
- Set up notifications (optional - Week 5)
- Begin long-term monitoring with confidence

---

## 🚀 Quick Commands Reference

```bash
# Check system status
ssh pi-fish 'systemctl status fish-guardian'

# View live logs
ssh pi-fish 'sudo journalctl -u fish-guardian -f'

# Run morning analysis
ssh pi-fish 'cd ~/Development/fish-guardian && source .venv/bin/activate && python3 /tmp/morning_baseline_analysis.py'

# Check Grafana
# Open browser: http://192.168.0.213:3000

# Restart service if needed
ssh pi-fish 'sudo systemctl restart fish-guardian'
```

---

**Last Updated:** October 15, 2025  
**Week:** 4 - Baseline Collection  
**Duration:** 5-7 days recommended
