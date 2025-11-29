# 📖 How to Use New PyZK Admin Actions

## Step-by-Step Guide

### Step 1: Access Django Admin
```
URL: http://localhost:8000/admin/
Login with your admin credentials
```

### Step 2: Go to ZKDevice Admin
```
Click: Home → Zktest → ZK devices
Or direct URL: http://localhost:8000/admin/zktest/zkdevice/
```

### Step 3: Select Device(s)
```
☐ Device 1 (192.168.1.201)
☐ Device 2 (192.168.1.202)
☑ Device 3 (192.168.1.203)  ← Check this box
```

**You can select:**
- Single device
- Multiple devices
- All devices (check top box)

### Step 4: Choose Action
```
Action: [Select an action ▼]
        ├── Reboot Selected Devices
        ├── Sync Time
        ├── Get Users from Device
        ├── Get Attendance Logs from Device
        ├── Mark as Offline
        ├── Clear Attendance Logs
        ├── 🔄 PyZK: Fetch & Import Users          ← NEW!
        ├── 🔄 PyZK: Fetch & Import Attendance     ← NEW!
        └── 🔄 PyZK: Fetch & Import All Data       ← NEW!
```

### Step 5: Click "Go"
```
[Go] ← Click this button
```

### Step 6: See Results
```
✅ PyZK Users: 1 devices processed, 15 users imported, 5 skipped
```

---

## Visual Guide

```
┌─────────────────────────────────────────────────────────┐
│ Django Administration                                    │
├─────────────────────────────────────────────────────────┤
│ Home › Zktest › ZK devices                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Action: [🔄 PyZK: Fetch & Import Users ▼]  [Go]        │
│                                                          │
│ ☑ Serial Number  Device Name    IP Address    Status   │
│ ─────────────────────────────────────────────────────── │
│ ☑ DEV001        Main Gate      192.168.1.201  Online   │
│ ☐ DEV002        Back Door      192.168.1.202  Online   │
│ ☑ DEV003        Office Entry   192.168.1.203  Online   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Action Descriptions

### 🔄 PyZK: Fetch & Import Users
```
What: Imports users from device via TCP
When: After enrolling new users
Result: New users + auto-created employees
Time: ~5-10 seconds per device
```

### 🔄 PyZK: Fetch & Import Attendance
```
What: Imports attendance records via TCP
When: Daily sync, before reports
Result: New attendance records
Time: ~10-30 seconds per device
```

### 🔄 PyZK: Fetch & Import All Data
```
What: Imports both users and attendance
When: Initial setup, complete sync
Result: Users + attendance + employees
Time: ~15-40 seconds per device
```

---

## Success Messages

### Users Imported
```
┌─────────────────────────────────────────────────────────┐
│ ✅ Success                                               │
├─────────────────────────────────────────────────────────┤
│ PyZK Users: 2 devices processed,                        │
│ 15 users imported, 5 skipped                            │
└─────────────────────────────────────────────────────────┘
```

### Attendance Imported
```
┌─────────────────────────────────────────────────────────┐
│ ✅ Success                                               │
├─────────────────────────────────────────────────────────┤
│ PyZK Attendance: 2 devices processed,                   │
│ 150 records imported, 20 skipped                        │
└─────────────────────────────────────────────────────────┘
```

### Full Sync
```
┌─────────────────────────────────────────────────────────┐
│ ✅ Success                                               │
├─────────────────────────────────────────────────────────┤
│ PyZK Full Sync: 2 devices processed,                    │
│ 15 users + 150 attendance imported                      │
└─────────────────────────────────────────────────────────┘
```

---

## Error Messages

### Device Failed
```
┌─────────────────────────────────────────────────────────┐
│ ⚠️ Warning                                               │
├─────────────────────────────────────────────────────────┤
│ 1 devices failed                                        │
│ (check if TCP is supported and IP is configured)       │
└─────────────────────────────────────────────────────────┘
```

**What to check:**
1. ✅ Device has IP address set
2. ✅ Device supports TCP (check device_type)
3. ✅ Device is online and reachable
4. ✅ Port is correct (default: 4370)
5. ✅ Network allows connection

---

## Common Scenarios

### Scenario 1: New Device Setup
```
1. Add device in admin
   - Set serial_number
   - Set ip_address
   - Set port (4370)
   
2. Select device
3. Action: 🔄 PyZK: Fetch & Import All Data
4. Click "Go"
5. Done! Users and attendance imported
```

### Scenario 2: Daily Attendance Sync
```
1. End of work day
2. Select all TCP devices
3. Action: 🔄 PyZK: Fetch & Import Attendance
4. Click "Go"
5. Generate reports
```

### Scenario 3: New User Enrolled
```
1. User enrolled on device
2. Go to admin
3. Select device
4. Action: 🔄 PyZK: Fetch & Import Users
5. Click "Go"
6. Employee auto-created
```

---

## Tips

### 💡 Tip 1: Check Device Type
Before using PyZK actions, verify device supports TCP:
```
Device Details → device_type → Should support TCP
```

### 💡 Tip 2: Verify IP Address
Make sure IP is set and reachable:
```
Device Details → ip_address → 192.168.1.201
```

### 💡 Tip 3: Test Connection First
Use "Sync Time" action to test if device is reachable

### 💡 Tip 4: Batch Operations
Select multiple devices to save time

### 💡 Tip 5: Check Statistics
After import, check device statistics:
- user_count - Should increase
- transaction_count - Should increase

---

## Troubleshooting

### Problem: No action visible
**Solution:** Refresh page, clear browser cache

### Problem: Action fails silently
**Solution:** Check Django logs for errors

### Problem: "0 devices processed"
**Solution:** 
- Check device supports TCP
- Verify IP is configured
- Check device is online

### Problem: "All records skipped"
**Solution:** This is normal - data already imported

### Problem: Slow performance
**Solution:**
- Check network speed
- Reduce number of devices per batch
- Check device has many records

---

## Best Practices

### ✅ DO:
- Use PyZK actions for old TCP devices
- Run attendance sync daily
- Check success messages
- Verify statistics after import
- Test with one device first

### ❌ DON'T:
- Use PyZK actions on ADMS-only devices
- Run full sync too frequently
- Ignore error messages
- Select too many devices at once (max 10)
- Run during peak hours

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PyZK Admin Actions Quick Reference                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 🔄 Import Users                                          │
│    Use: After enrolling users                           │
│    Time: ~5-10 sec/device                               │
│                                                          │
│ 🔄 Import Attendance                                     │
│    Use: Daily sync                                      │
│    Time: ~10-30 sec/device                              │
│                                                          │
│ 🔄 Import All Data                                       │
│    Use: Initial setup                                   │
│    Time: ~15-40 sec/device                              │
│                                                          │
│ Requirements:                                            │
│ ✅ Device supports TCP                                   │
│ ✅ IP address configured                                 │
│ ✅ Device online                                         │
│ ✅ Port 4370 accessible                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Summary

1. **Go to:** `/admin/zktest/zkdevice/`
2. **Select:** Device(s) with TCP support
3. **Choose:** PyZK action from dropdown
4. **Click:** "Go" button
5. **See:** Success message with statistics

Easy, fast, and reliable! 🎉
