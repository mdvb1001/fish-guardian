# Fish Guardian - Git Workflow Guide

## Quick Reference

**Single Source of Truth:** Raspberry Pi (`pi-fish:~/Development/fish-guardian`)

### Most Common Commands

```bash
# Pull latest changes from Pi to local machine
cd /Users/Max/Desktop/max/coding/codingProjects/personalProjects/fish-guardian
git pull pi-fish master

# View what changed on Pi
ssh pi-fish "cd ~/Development/fish-guardian && git status"
ssh pi-fish "cd ~/Development/fish-guardian && git log --oneline -5"

# Make changes and commit on Pi
ssh pi-fish "cd ~/Development/fish-guardian && git add -A && git commit -m 'Your message'"
```

---

## Repository Structure

```
┌─────────────────────────────────────┐
│   Raspberry Pi (pi-fish)            │
│   ~/Development/fish-guardian/      │
│   [master branch]                   │
│   SOURCE OF TRUTH ⭐                │
│   - Running production code         │
│   - Active InfluxDB database        │
│   - All development happens here    │
└─────────────────────────────────────┘
              ↓ git pull
┌─────────────────────────────────────┐
│   Local Mac                         │
│   /Users/Max/.../fish-guardian/     │
│   [main branch]                     │
│   READ-ONLY REFERENCE               │
│   - Documentation reference         │
│   - Offline code browsing           │
│   - Context preservation            │
└─────────────────────────────────────┘
```

---

## Workflow

### 1. Making Changes (Always on Pi)

```bash
# SSH to Pi
ssh pi-fish

# Navigate to project
cd ~/Development/fish-guardian

# Make your changes
nano motion_track_influx.py
# or
python3 compute_baselines.py

# Check what changed
git status
git diff

# Stage and commit
git add -A
git commit -m "Descriptive commit message

- Detail what changed
- Why the change was made
- Any important notes"

# View the commit
git log -1
```

### 2. Syncing to Local Machine

```bash
# On your Mac
cd /Users/Max/Desktop/max/coding/codingProjects/personalProjects/fish-guardian

# Pull latest from Pi
git pull pi-fish master

# Verify sync
git log -1
```

### 3. Reading Documentation Locally

All documentation is now synced, so you can read/search it locally without SSH:

```bash
# View README
cat README.md

# Search for specific info
grep -r "baseline" *.md

# Open in editor
code .
```

---

## What's in Git vs What's Not

### ✅ Tracked by Git
- All Python scripts (.py files)
- All documentation (.md files)
- Configuration guides
- Planning PDFs (docs/planning/)
- Shell scripts (.sh files)

### ❌ NOT in Git (via .gitignore)
- `.env` (contains InfluxDB token - SECRETS)
- `.venv/` (Python virtual environment - too large)
- `baselines_v1.json` (64MB - regenerable)
- `24h_report.txt` (temporary reports)
- Backup files (`*.backup`, `*_backup.py`)
- `__pycache__/`, `*.pyc` (Python cache)

---

## Common Scenarios

### Scenario 1: Updated dashboard script on Pi
```bash
# 1. On Pi - make changes
ssh pi-fish
cd ~/Development/fish-guardian
nano create_dashboard_v7.py
# ... make edits ...

# 2. Commit on Pi
git add create_dashboard_v7.py
git commit -m "Fix dashboard panel alignment issue"

# 3. Sync to local (on Mac)
cd /Users/Max/.../fish-guardian
git pull pi-fish master
```

### Scenario 2: View code changes from last week
```bash
# On Mac or Pi
git log --oneline --since="1 week ago"
git log --stat -3  # Last 3 commits with file stats
git diff HEAD~5    # Changes from 5 commits ago
```

### Scenario 3: Accidentally deleted a file
```bash
# On Pi
cd ~/Development/fish-guardian
git checkout -- motion_track_influx.py  # Restore from last commit
```

### Scenario 4: Want to update PROJECT_CONTEXT.md after a session
```bash
# On Pi
ssh pi-fish
cd ~/Development/fish-guardian
nano PROJECT_CONTEXT.md
# ... update session history ...

git add PROJECT_CONTEXT.md
git commit -m "Update PROJECT_CONTEXT: Week 5 AI training progress"

# Sync to local
# (on Mac)
git pull pi-fish master
```

### Scenario 5: Check if Pi has uncommitted changes
```bash
ssh pi-fish "cd ~/Development/fish-guardian && git status"
```

---

## Commit Message Best Practices

### Good Commit Messages

```bash
# Example 1: Feature addition
git commit -m "Add system heartbeat for true uptime monitoring

- Added heartbeat_check measurement to InfluxDB
- Updated Fish Activity Status panel to use heartbeat
- Fixes issue where empty tank showed offline
- Heartbeat writes every 60 seconds regardless of fish movement"

# Example 2: Bug fix
git commit -m "Fix dashboard series limit error on Activity Alert panel

- Changed query to aggregate before returning to Grafana
- Added group() and sum() to reduce series count
- Tested with 2898 fish IDs - now returns single value"

# Example 3: Documentation update
git commit -m "Update README with Week 5 completion status"
```

### Bad Commit Messages

```bash
git commit -m "fixed stuff"  # Too vague
git commit -m "update"       # No context
git commit -m "asdf"         # Not descriptive
```

### Format Recommendation

```
Brief summary (50 chars or less)

Detailed explanation if needed:
- Bullet points for multiple changes
- Why the change was necessary
- Any testing done
- Related issues or future work
```

---

## Viewing History

```bash
# Compact one-line view
git log --oneline -10

# With file changes
git log --stat -5

# With full diff
git log -p -2

# Graphical view (if you have gitk)
gitk --all

# Filter by date
git log --since="2025-10-14" --until="2025-10-21"

# Filter by author
git log --author="Fish Guardian"

# Search commit messages
git log --grep="dashboard"

# Search code changes
git log -S"fish_activity" --source --all
```

---

## Undoing Changes

### Uncommitted Changes

```bash
# Discard changes to a specific file
git checkout -- filename.py

# Discard all uncommitted changes
git reset --hard HEAD

# Unstage a file (keep changes)
git reset HEAD filename.py
```

### Committed Changes

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - DANGEROUS
git reset --hard HEAD~1

# Create a new commit that reverses a previous commit
git revert <commit-hash>
```

**⚠️ Warning:** Be careful with `--hard` - it permanently deletes changes!

---

## Initial Setup (Already Complete ✅)

This was done during project setup and doesn't need to be repeated:

```bash
# On Pi
cd ~/Development/fish-guardian
git init
git config user.name "Fish Guardian"
git config user.email "noreply@fishguardian.local"
cat > .gitignore << 'EOF'
.env
.venv/
baselines_v1.json
24h_report.txt
*.backup
__pycache__/
EOF
git add -A
git commit -m "Initial commit - Week 4 complete"

# On Local Mac
cd /Users/Max/Desktop/max/coding/codingProjects/personalProjects/fish-guardian
git init
git remote add pi-fish pi-fish:~/Development/fish-guardian
git fetch pi-fish
git checkout -b main pi-fish/master
```

---

## Troubleshooting

### Issue: "Permission denied" when pulling
```bash
# Check SSH connection
ssh pi-fish "echo Connection successful"

# Check remote is configured
git remote -v
```

### Issue: "Merge conflict" when pulling
```bash
# This shouldn't happen if you only edit on Pi
# But if it does:
git pull pi-fish master
# Fix conflicts in editor
git add <conflicted-files>
git commit -m "Resolve merge conflict"
```

### Issue: "Diverged branches"
```bash
# If local accidentally has commits:
git fetch pi-fish
git reset --hard pi-fish/master  # WARNING: Discards local commits
```

### Issue: Forgot to commit before making new changes
```bash
# On Pi
git add -A
git commit -m "WIP: Uncommitted changes before X"
# Then continue with new work
```

---

## Future: GitHub Integration (Optional)

If you want to add cloud backup to GitHub:

```bash
# 1. Create GitHub repository
# Go to github.com and create "fish-guardian" repo

# 2. On Pi - add GitHub as remote
ssh pi-fish
cd ~/Development/fish-guardian
git remote add github https://github.com/yourusername/fish-guardian.git
git branch -M main
git push -u github main

# 3. On Local - add GitHub remote
cd /Users/Max/.../fish-guardian
git remote add github https://github.com/yourusername/fish-guardian.git

# 4. Now you can push/pull from GitHub too
git push github main
git pull github main
```

Benefits:
- Cloud backup of entire project history
- Access from anywhere
- Share with others
- GitHub Actions for automation (optional)

---

## Current Status

- ✅ Git initialized on Pi (master branch)
- ✅ Git initialized locally (main branch)
- ✅ Remote configured: `pi-fish` → Pi repository
- ✅ Initial commit made: `3e048cf - Initial commit - Week 4 complete`
- ✅ Local synced with Pi
- ✅ `.gitignore` configured (excludes secrets and large files)

**Last Sync:** October 21, 2025

---

## Key Principles

1. **Pi is the source of truth** - All changes happen there first
2. **Local is read-only** - Only for reference and documentation
3. **Commit frequently** - After each significant change or milestone
4. **Meaningful messages** - Future you will thank present you
5. **Sync regularly** - Keep local updated for offline reference
6. **Never commit secrets** - `.env` is in `.gitignore` for a reason

---

**Last Updated:** October 21, 2025
**Document Version:** 1.0
