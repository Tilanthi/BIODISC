# BIODISC Session Recovery Guide

## 🔄 Context Exhaustion Recovery

BIODISC V5.0 includes **automatic session persistence** to recover from context overflow or session closure.

## 📂 Session Persistence Files

### Primary Files

**`session_state.json`** - Main session state
```json
{
  "timestamp": "2026-07-01T16:30:00",
  "running": true,
  "cycle_count": 15,
  "discovery_count": 8
}
```

**`autonomous_discoveries.jsonl`** - Persistent discoveries
```json
{"id": "discovery_abc123", "question": "...", "discovery": "...", ...}
```

**`biodisc_discovery.log`** - Discovery activity logs

### Memory Files
**`~/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/`** - Persistent memory palace

## 🛠️ Recovery Procedures

### Automatic Recovery (Default)

**Just restart the system**:
```bash
python .genuine_autonomous_discovery.py
```

**System automatically**:
1. Reads `session_state.json`
2. Restores discovery count
3. Continues from last cycle
4. Maintains all state

### Manual Recovery (If Automatic Fails)

```bash
# Check session state
cat session_state.json

# Verify discoveries
wc -l autonomous_discoveries.jsonl

# Check recent logs
tail -50 logs/genuine_discovery.log

# Restart system
python .genuine_autonomous_discovery.py
```

### Emergency Recovery (Corrupted State)

```bash
# Backup current discoveries
cp autonomous_discoveries.jsonl autonomous_discoveries.jsonl.backup

# Reset session state
echo '{"timestamp": "2026-07-01T16:30:00", "running": false, "cycle_count": 0, "discovery_count": 0}' > session_state.json

# Restart fresh
python .genuine_autonomous_discovery.py
```

## 🔧 Context Recovery Triggers

### Automatic Context Loading

**Hook**: `~/.claude/session-start-hook.sh`

**When Triggered**: Every Claude session start

**What It Does**:
1. Updates session context files
2. Starts genuine discovery if in BIODISC directory
3. Displays system status

### Manual Context Recovery

**If auto-load fails**:
```bash
# Re-run session hook
bash ~/.claude/session-start-hook.sh

# Check context
cat ~/.claude/session-manager/session_startup.txt
```

## 📊 State Verification

### Check System Status

```bash
# Session state
cat session_state.json

# Discovery count
wc -l autonomous_discoveries.jsonl

# Process status
ps aux | grep "genuine_autonomous" | grep -v grep

# Recent activity
tail -20 logs/genuine_discovery.log
```

### Validate Data Integrity

```python
import json

# Validate session state
with open('session_state.json') as f:
    state = json.load(f)
    assert 'timestamp' in state
    assert 'cycle_count' in state

# Validate discoveries
with open('autonomous_discoveries.jsonl') as f:
    for line in f:
        if line.strip():
            discovery = json.loads(line)
            assert 'id' in discovery
            assert 'computational_backing' in discovery
```

## 🚨 Error Recovery

### Common Errors & Solutions

**"Session state corrupted"**
```bash
# Reset to clean state
echo '{"running": false, "cycle_count": 0, "discovery_count": 0}' > session_state.json
```

**"No discoveries file"**
```bash
# Create empty discoveries file
touch autonomous_discoveries.jsonl
```

**"Process won't start"**
```bash
# Kill old processes
pkill -f "autonomous_discovery"

# Restart system
python .genuine_autonomous_discovery.py
```

## 📝 Session State Management

### State Components

**Cycle Counter**: Tracks discovery cycles completed
**Discovery Count**: Total discoveries made
**Running Status**: System operational state
**Timestamp**: Last activity time

### Persistence Strategy

**Auto-Save Triggers**:
- After each discovery cycle
- On system shutdown
- Every 5 minutes during operation

**Auto-Load Triggers**:
- System startup
- After context recovery
- Manual state load

## 🔬 Discovery Recovery Validation

### Verify Recovery Success

**Check log for**:
```
✅ Session state loaded from session_state.json
📂 Previous session restored: X discoveries made
```

**Verify discoveries continue**:
```
✅ Discovery stored: discovery_xyz123
✅ Discovery discovery_xyz123 stored successfully
```

## 💾 Backup Strategy

### Automatic Backups

**Files Automatically Backed Up**:
- `session_state.json` → `session_state.json.backup`
- `autonomous_discoveries.jsonl` → `autonomous_discoveries.jsonl.backup`

**Backup Frequency**: Every save operation

### Manual Backup

```bash
# Create timestamped backup
cp session_state.json session_state_$(date +%Y%m%d_%H%M%S).json
cp autonomous_discoveries.jsonl discoveries_$(date +%Y%m%d_%H%M%S).jsonl
```

## 🔄 Full Recovery Procedure

### Complete System Recovery

```bash
# 1. Navigate to BIODISC directory
cd /Users/gjw255/astrodata/SWARM/BIODISC

# 2. Check current state
cat session_state.json
wc -l autonomous_discoveries.jsonl
ps aux | grep "autonomous_discovery"

# 3. Verify data integrity
python -c "
import json
with open('session_state.json') as f:
    print(json.load(f))
"

# 4. Restart system
python .genuine_autonomous_discovery.py

# 5. Monitor recovery
tail -f logs/genuine_discovery.log
```

### Expected Recovery Output

```
📂 Previous session restored: 15 discoveries made
✅ Session state loaded from session_state.json
🔬 Genuine autonomous discovery restarted
📊 Continuing from cycle 16...
```

## 🆘 Emergency Procedures

### Complete System Reset

**Only use if system is completely corrupted**:

```bash
# Stop all discovery processes
pkill -f "autonomous_discovery"

# Reset all state
rm session_state.json
echo '{"running": false, "cycle_count": 0, "discovery_count": 0}' > session_state.json

# Reset discoveries (CAUTION)
rm autonomous_discoveries.jsonl
touch autonomous_discoveries.jsonl

# Restart fresh
python .genuine_autonomous_discovery.py
```

### Selective Reset

**Reset only cycle count**:
```bash
# Preserve discoveries, reset cycles
python -c "
import json
with open('session_state.json', 'r') as f:
    state = json.load(f)
state['cycle_count'] = 0
with open('session_state.json', 'w') as f:
    json.dump(state, f, indent=2)
"
```

## 📞 Support

### Session Recovery Issues

**Check Logs First**:
```bash
tail -100 logs/genuine_discovery.log | grep -E "ERROR|WARNING|session|recovery"
```

**Common Issues**:
- Missing session_state.json → Auto-created on next run
- Corrupted JSON → Reset session state
- Process stuck → Kill and restart

### Documentation

**Recovery Details**: See `docs/10_genuine_discovery_system.md`  
**Architecture**: See `docs/04_architecture.md`  
**Development**: See `docs/06_development.md`

---

**BIODISC V5.0 is designed for reliable session recovery. The system automatically restores state and continues from where it left off.**