# 🚀 Admin Actions Quick Guide

## All Available Actions in ZKDevice Admin

### 📡 ADMS Actions (Push-Based - For New Devices)
```
✅ Reboot Selected Devices
✅ Sync Time
✅ Get Users from Device
✅ Get Attendance Logs from Device
✅ Mark as Offline
✅ Clear Attendance Logs
```
**How they work:** Create commands → Device receives → Device pushes data

---

### 🔄 PyZK Actions (TCP Pull-Based - For Old Devices)
```
🔄 PyZK: Fetch & Import Users
🔄 PyZK: Fetch & Import Attendance
🔄 PyZK: Fetch & Import All Data
```
**How they work:** Server connects → Fetches data → Imports immediately

---

## Quick Decision Guide

### Use ADMS Actions When:
- ✅ Device supports ADMS (push protocol)
- ✅ Device is online and connected
- ✅ You want to queue commands
- ✅ Device will push data automatically

### Use PyZK Actions When:
- ✅ Device is old (doesn't support ADMS)
- ✅ You want immediate results
- ✅ You need to fetch data on demand
- ✅ Device supports TCP connection

---

## Action Comparison

| Feature | ADMS Actions | PyZK Actions |
|---------|-------------|--------------|
| **Speed** | Depends on device | Immediate |
| **Connection** | Device must be online | Direct TCP |
| **Data Flow** | Device → Server | Server → Device |
| **Best For** | New devices | Old devices |
| **Reliability** | Depends on device | Direct control |

---

## Usage Examples

### Example 1: Daily Attendance Sync (Old Device)
```
1. Go to ZKDevice admin
2. Select device(s)
3. Choose: 🔄 PyZK: Fetch & Import Attendance
4. Click "Go"
5. See: ✅ 150 records imported, 20 skipped
```

### Example 2: New User Enrollment (Old Device)
```
1. Enroll users on device
2. Go to ZKDevice admin
3. Select device
4. Choose: 🔄 PyZK: Fetch & Import Users
5. Click "Go"
6. See: ✅ 5 users imported, employees auto-created
```

### Example 3: Complete Sync (Old Device)
```
1. Go to ZKDevice admin
2. Select device
3. Choose: 🔄 PyZK: Fetch & Import All Data
4. Click "Go"
5. See: ✅ 5 users + 150 attendance imported
```

### Example 4: Reboot Device (Any Device)
```
1. Go to ZKDevice admin
2. Select device(s)
3. Choose: ✅ Reboot Selected Devices
4. Click "Go"
5. Command queued, device will reboot
```

---

## Success Messages Explained

### PyZK Users
```
✅ PyZK Users: 2 devices processed, 15 users imported, 5 skipped
```
- **2 devices** = Number of devices synced
- **15 imported** = New users added
- **5 skipped** = Already existed

### PyZK Attendance
```
✅ PyZK Attendance: 2 devices processed, 150 records imported, 20 skipped
```
- **2 devices** = Number of devices synced
- **150 imported** = New attendance records
- **20 skipped** = Duplicates (already in DB)

### PyZK Full Sync
```
✅ PyZK Full Sync: 2 devices processed, 15 users + 150 attendance imported
```
- Complete statistics for both users and attendance

---

## Error Messages

### Warning
```
⚠️ 1 devices failed (check if TCP is supported and IP is configured)
```

**Quick Fixes:**
1. ✅ Check device has IP address set
2. ✅ Verify device supports TCP
3. ✅ Check device is online
4. ✅ Test network connectivity

---

## Tips & Tricks

### 💡 Tip 1: Batch Operations
Select multiple devices and run action once - saves time!

### 💡 Tip 2: Check Before Import
If you see "all skipped", data is already imported (this is good!)

### 💡 Tip 3: Use Full Sync Sparingly
Only use "Import All Data" for initial setup or after device reset

### 💡 Tip 4: Daily Routine
Run "Fetch & Import Attendance" daily at end of day

### 💡 Tip 5: Monitor Statistics
Check device statistics (user_count, transaction_count) after import

---

## Common Workflows

### Workflow 1: New Device Setup
```
1. Add device in admin (set IP, port)
2. Run: 🔄 PyZK: Fetch & Import All Data
3. Verify users and attendance imported
4. Done!
```

### Workflow 2: Daily Attendance Collection
```
1. End of day
2. Select all TCP devices
3. Run: 🔄 PyZK: Fetch & Import Attendance
4. Generate reports
```

### Workflow 3: New User Enrollment
```
1. Enroll user on device
2. Run: 🔄 PyZK: Fetch & Import Users
3. Employee auto-created
4. User ready to work
```

---

## Summary

| Action | When to Use | Result |
|--------|------------|--------|
| **🔄 Import Users** | After enrolling users | New users + employees |
| **🔄 Import Attendance** | Daily sync | New attendance records |
| **🔄 Import All** | Initial setup | Complete sync |
| **✅ Reboot** | Device issues | Device restarts |
| **✅ Sync Time** | Time drift | Time synchronized |
| **✅ Get Users** | ADMS devices | Command queued |
| **✅ Get Logs** | ADMS devices | Command queued |

---

## Quick Reference

```
Old TCP Device? → Use 🔄 PyZK Actions
New ADMS Device? → Use ✅ ADMS Actions
Need immediate results? → Use 🔄 PyZK Actions
Want to queue commands? → Use ✅ ADMS Actions
```

Done! 🎉
