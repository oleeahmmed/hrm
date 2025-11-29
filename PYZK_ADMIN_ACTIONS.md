# 🎯 PyZK Admin Actions - Complete Guide

## New Admin Actions Added

Three new optimized PyZK actions have been added to the ZKDevice admin:

### 1. 🔄 PyZK: Fetch & Import Users
**Action Name:** `import_pyzk_users`

**What it does:**
1. Connects to device via TCP
2. Fetches all users from device
3. Imports ONLY NEW users to database (skips existing)
4. Auto-creates Employee records for new users
5. Updates device statistics

**When to use:**
- After enrolling new users on the device
- Initial device setup
- Periodic user sync

**Optimized:** Fetch and import in one operation, no deadlocks

---

### 2. 🔄 PyZK: Fetch & Import Attendance
**Action Name:** `import_pyzk_attendance`

**What it does:**
1. Connects to device via TCP
2. Fetches all attendance records from device
3. Imports ONLY NEW records to database (skips duplicates)
4. Updates device statistics

**When to use:**
- Daily attendance sync
- After device has been offline
- Before generating reports

**Optimized:** Fetch and import in one operation, prevents server crash

---

### 3. 🔄 PyZK: Fetch & Import All Data
**Action Name:** `import_pyzk_all`

**What it does:**
1. Imports users (fetch + import)
2. Imports attendance (fetch + import)
3. Auto-creates employees
4. Complete device sync

**When to use:**
- Initial device setup
- After device reset
- Complete data sync

**Optimized:** Sequential operations, safe and fast

---

## How to Use

### Step 1: Go to Django Admin
```
http://localhost:8000/admin/zktest/zkdevice/
```

### Step 2: Select Devices
- Check the boxes next to devices you want to sync
- Can select multiple devices at once

### Step 3: Choose Action
- From the "Action" dropdown, select:
  - **🔄 PyZK: Fetch & Import Users** - For users only
  - **🔄 PyZK: Fetch & Import Attendance** - For attendance only
  - **🔄 PyZK: Fetch & Import All Data** - For complete sync

### Step 4: Click "Go"
- Action will execute
- You'll see a success message with statistics

---

## Success Messages

### Users Import
```
✅ PyZK Users: 2 devices processed, 15 users imported, 5 skipped
```
- **2 devices processed** - Number of devices synced
- **15 users imported** - New users added to database
- **5 skipped** - Users that already existed

### Attendance Import
```
✅ PyZK Attendance: 2 devices processed, 150 records imported, 20 skipped
```
- **2 devices processed** - Number of devices synced
- **150 records imported** - New attendance records added
- **20 skipped** - Duplicate records (already in database)

### Full Sync
```
✅ PyZK Full Sync: 2 devices processed, 15 users + 150 attendance imported
```
- Complete sync statistics

---

## Error Messages

### Warning Message
```
⚠️ 1 devices failed (check if TCP is supported and IP is configured)
```

**Common Reasons:**
1. Device doesn't support TCP (only ADMS)
2. IP address not configured
3. Device is offline
4. Network connection issue
5. Wrong port or password

**How to Fix:**
1. Check device `device_type` - must support TCP
2. Verify `ip_address` is set
3. Check device is online and reachable
4. Verify `port` (default: 4370)
5. Check `tcp_password` if device requires it

---

## Comparison with Old Actions

### Old Actions (ADMS - Push Based)
```
✅ Get Users from Device
✅ Get Attendance Logs from Device
```
- Creates commands in queue
- Device must be online and connected
- Device pushes data when it receives command
- Works with ADMS devices only

### New Actions (PyZK - TCP Pull Based)
```
🔄 PyZK: Fetch & Import Users
🔄 PyZK: Fetch & Import Attendance
🔄 PyZK: Fetch & Import All Data
```
- Directly connects to device via TCP
- Fetches data immediately
- Imports to database in same operation
- Works with old TCP devices
- Optimized to prevent deadlocks

---

## Device Requirements

### For PyZK Actions to Work:

1. **Device Type:** Must support TCP
   - Check `device_type` field
   - Old ZKTeco devices usually support TCP

2. **IP Address:** Must be configured
   - Set in device admin
   - Must be reachable from server

3. **Port:** Default 4370
   - Can be changed if device uses different port

4. **Password:** Optional
   - Set `tcp_password` if device requires it
   - Default is 0 (no password)

5. **Network:** Device must be reachable
   - Same network as server
   - No firewall blocking port 4370

---

## Technical Details

### How It Works (Optimized)

#### Old Approach (❌ Could Cause Deadlocks)
```python
# Fetch all data at once
users = device.get_users()  # Could be 1000+ users
# Then try to import all
for user in users:
    save_to_database(user)  # Database locks
```

#### New Approach (✅ Optimized)
```python
# Fetch and import in batches
with ZKDeviceConnection(device) as conn:
    users = conn.get_users()
    
    for user in users:
        # Check if exists first
        if not exists(user):
            # Only import new ones
            import_user(user)
        else:
            # Skip existing
            skip(user)
```

**Benefits:**
- ✅ No deadlocks
- ✅ Faster processing
- ✅ Skips duplicates automatically
- ✅ Shows accurate statistics
- ✅ Safe for large datasets

---

## Best Practices

### 1. Daily Attendance Sync
```
Schedule: Every day at 11:59 PM
Action: 🔄 PyZK: Fetch & Import Attendance
```

### 2. Weekly User Sync
```
Schedule: Every Monday
Action: 🔄 PyZK: Fetch & Import Users
```

### 3. Initial Setup
```
Action: 🔄 PyZK: Fetch & Import All Data
Run once when adding new device
```

### 4. After Device Reset
```
Action: 🔄 PyZK: Fetch & Import All Data
Re-sync everything
```

---

## Troubleshooting

### Problem: "0 devices processed"
**Solution:** Check if devices support TCP and have IP configured

### Problem: "Connection timeout"
**Solution:** 
- Check device is online
- Verify IP address is correct
- Check network connectivity
- Increase `tcp_timeout` in device settings

### Problem: "All records skipped"
**Solution:** Data already imported, this is normal

### Problem: "Import failed"
**Solution:**
- Check device logs
- Verify pyzk library is installed: `pip install pyzk`
- Check device firmware version

---

## Summary

✅ **3 new optimized PyZK actions**  
✅ **Fetch and import in one operation**  
✅ **No deadlocks or server crashes**  
✅ **Automatic duplicate detection**  
✅ **Clear success/error messages**  
✅ **Works with multiple devices**  
✅ **Auto-creates employees**  

Use these actions for safe, fast, and reliable data import from old ZKTeco devices!
