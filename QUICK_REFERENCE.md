# 🚀 Quick Reference Guide

## File Locations

### PyZK (TCP) - Everything in ONE file
```
zktest/api/pyzk_views.py
```
- ✅ ZKDeviceConnection class
- ✅ import_users_from_device()
- ✅ import_attendance_from_device()
- ✅ All 4 PyZK API views
- ✅ All utility functions

### ADMS (Push) - Everything in ONE file
```
zktest/api/api_views.py
```
- ✅ ADMSHandlerView
- ✅ Device handshake
- ✅ Attendance push handling
- ✅ User sync handling

### Attendance Calculations
```
zktest/report_views.py
```
- ✅ get_work_day_range()
- ✅ calculate_work_hours_from_punches()
- ✅ generate_attendance_from_logs()

### Utils (Minimal)
```
zktest/utils.py
```
- Just documentation
- No code

## API Endpoints

### PyZK APIs
```
POST /api/pyzk/devices/<id>/fetch-users/
POST /api/pyzk/devices/<id>/import-users/
POST /api/pyzk/devices/<id>/fetch-attendance/
POST /api/pyzk/devices/<id>/import-attendance/
```

### ADMS APIs
```
GET  /iclock/cdata?SN=<serial>
POST /iclock/cdata?SN=<serial>&table=ATTLOG
POST /iclock/cdata?SN=<serial>&table=USER
```

## Models (Shared by Both)

```python
ZKDevice         # Device information
DeviceUser       # Users enrolled in devices
AttendanceLog    # Punch records (source='adms' or 'tcp')
Employee         # Employee records
```

## Quick Test

```bash
# Check for errors
python3 manage.py check

# Run server
python3 manage.py runserver

# Test PyZK API
curl -X POST "http://localhost:8000/api/pyzk/devices/1/fetch-users/" \
  -H "Content-Type: application/json" \
  -d '{"import_new": true}'
```

## What Changed

### ✅ Before
- PyZK code scattered in `utils.py` and `pyzk_views.py`
- Import errors
- Messy structure

### ✅ After
- ALL PyZK code in `pyzk_views.py`
- No import errors
- Clean, self-contained modules

## Need to Modify?

### Want to change PyZK behavior?
→ Edit `zktest/api/pyzk_views.py`

### Want to change ADMS behavior?
→ Edit `zktest/api/api_views.py`

### Want to change attendance calculations?
→ Edit `zktest/report_views.py`

## 🎯 Key Points

1. **PyZK** = TCP pull-based (server connects to device)
2. **ADMS** = Push-based (device sends to server)
3. **Both use same models** (AttendanceLog, DeviceUser)
4. **No code duplication**
5. **Clean separation**

Done! 🎉
