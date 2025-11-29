# PyZK Implementation Summary

## Overview

Your system now supports **BOTH** ADMS (push-based) and PyZK (TCP pull-based) protocols for ZKTeco devices.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ZKTeco Device Support                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │   ADMS Protocol  │              │  PyZK Protocol   │    │
│  │   (Push-Based)   │              │  (TCP Pull-Based)│    │
│  └──────────────────┘              └──────────────────┘    │
│          │                                   │               │
│          │                                   │               │
│  ┌───────▼────────┐              ┌──────────▼─────────┐   │
│  │ api_views.py   │              │  pyzk_views.py     │   │
│  │ (Existing)     │              │  (New)             │   │
│  └────────────────┘              └────────────────────┘   │
│          │                                   │               │
│          └───────────────┬───────────────────┘              │
│                          │                                   │
│                  ┌───────▼────────┐                         │
│                  │   api/utils.py  │                         │
│                  │  (Shared Logic) │                         │
│                  └────────────────┘                         │
│                          │                                   │
│                  ┌───────▼────────┐                         │
│                  │  zktest/utils.py│                         │
│                  │ (Device Connect)│                         │
│                  └────────────────┘                         │
│                          │                                   │
│                  ┌───────▼────────┐                         │
│                  │  models.py      │                         │
│                  │ (AttendanceLog) │                         │
│                  └────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
zktest/
├── api/
│   ├── __init__.py
│   ├── urls.py                    # ✅ Unified URLs (ADMS + PyZK)
│   ├── api_views.py               # ✅ ADMS views (existing, unchanged)
│   ├── pyzk_views.py              # ✨ NEW: PyZK TCP views
│   ├── serializers.py             # ✅ ADMS serializers (existing)
│   ├── pyzk_serializers.py        # ✨ NEW: PyZK serializers
│   ├── utils.py                   # ✨ NEW: Shared API utilities
│   └── API_DOCUMENTATION.md       # ✨ NEW: Complete API docs
│
├── utils.py                       # ✅ Device connection & sync (existing)
├── models.py                      # ✅ Shared models (existing)
└── ...
```

---

## Key Features

### 1. **Separated Architecture**
- **ADMS APIs** remain in `api_views.py` (unchanged)
- **PyZK APIs** in new `pyzk_views.py` (separate)
- **Shared utilities** in `api/utils.py`
- **Single URL file** with both protocols

### 2. **Import Only New Data**
- ✅ Users: Only creates NEW users, never updates existing
- ✅ Attendance: Only imports NEW records, skips duplicates
- ✅ Uses `get_or_create` to prevent duplicates

### 3. **Flexible Date Ranges**
- `today` - Today's records
- `7days` - Last 7 days
- `30days` - Last 30 days
- `month` - Current month
- `custom` - Specify exact dates

### 4. **Auto-Create Employees**
- Automatically creates Employee records from DeviceUsers
- Enables immediate attendance tracking
- Optional (can be disabled)

### 5. **Same AttendanceLog Model**
- Both ADMS and PyZK save to same `AttendanceLog` model
- `source` field tracks origin ('adms' or 'tcp')
- Unified data structure

---

## API Endpoints

### PyZK (TCP) Endpoints

```
Base: /api/pyzk/
```

#### Device Management
- `GET /api/pyzk/devices/` - List TCP devices
- `GET /api/pyzk/devices/{id}/` - Device details
- `POST /api/pyzk/devices/{id}/test-connection/` - Test connection

#### User Operations
- `POST /api/pyzk/devices/{id}/fetch-users/` - Fetch users from device
- `POST /api/pyzk/devices/{id}/import-users/` - Import users
- `GET /api/pyzk/devices/{id}/users/` - Get users (from DB)

#### Attendance Operations
- `POST /api/pyzk/devices/{id}/fetch-attendance/` - Fetch attendance
- `POST /api/pyzk/devices/{id}/import-attendance/` - Import all attendance
- `GET /api/pyzk/devices/{id}/attendance-logs/` - Get logs (from DB)

#### Device Commands
- `POST /api/pyzk/devices/{id}/execute-command/` - Execute command
- `POST /api/pyzk/devices/{id}/sync-all/` - Sync users + attendance
- `GET /api/pyzk/devices/{id}/sync-logs/` - Get sync history

---

## Usage Examples

### 1. Fetch Today's Attendance

```bash
POST /api/pyzk/devices/1/fetch-attendance/
{
  "date_range": "today",
  "import_new": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Fetched 250 attendance records",
  "data": {
    "total": 250,
    "imported": 50,
    "skipped": 200,
    "failed": 0
  }
}
```

### 2. Fetch Last 7 Days

```bash
POST /api/pyzk/devices/1/fetch-attendance/
{
  "date_range": "7days",
  "import_new": true
}
```

### 3. Fetch Last 30 Days

```bash
POST /api/pyzk/devices/1/fetch-attendance/
{
  "date_range": "30days",
  "import_new": true
}
```

### 4. Fetch Custom Range

```bash
POST /api/pyzk/devices/1/fetch-attendance/
{
  "date_range": "custom",
  "date_from": "2024-01-01",
  "date_to": "2024-01-31",
  "import_new": true
}
```

### 5. Fetch All Attendance

```bash
POST /api/pyzk/devices/1/import-attendance/
{
  "clear_after_sync": false
}
```

### 6. Import Users

```bash
POST /api/pyzk/devices/1/import-users/
{
  "auto_create_employees": true
}
```

### 7. Sync Everything

```bash
POST /api/pyzk/devices/1/sync-all/
{
  "clear_attendance": false,
  "auto_create_employees": true
}
```

---

## How It Works

### ADMS (Push-Based)
1. Device connects to server
2. Device pushes data automatically
3. Server receives and stores data
4. No manual fetch needed

### PyZK (TCP Pull-Based)
1. Server connects to device via TCP
2. Server fetches data on demand
3. Server imports only new records
4. Manual or scheduled fetch

---

## Data Flow

### Attendance Import Flow

```
┌──────────────┐
│ ZKTeco Device│
└──────┬───────┘
       │
       │ TCP Connection (PyZK)
       │
┌──────▼───────┐
│ pyzk_views.py│
└──────┬───────┘
       │
       │ Fetch Data
       │
┌──────▼───────┐
│ api/utils.py │
│ import_      │
│ attendance_  │
│ logs()       │
└──────┬───────┘
       │
       │ get_or_create
       │
┌──────▼───────┐
│ AttendanceLog│
│ (Model)      │
└──────────────┘
```

### User Import Flow

```
┌──────────────┐
│ ZKTeco Device│
└──────┬───────┘
       │
       │ TCP Connection
       │
┌──────▼───────┐
│ pyzk_views.py│
└──────┬───────┘
       │
       │ Fetch Users
       │
┌──────▼───────┐
│ api/utils.py │
│ import_      │
│ device_users()│
└──────┬───────┘
       │
       │ Create if not exists
       │
┌──────▼───────┐
│ DeviceUser   │
│ (Model)      │
└──────┬───────┘
       │
       │ auto_create_employee
       │
┌──────▼───────┐
│ Employee     │
│ (Model)      │
└──────────────┘
```

---

## Key Functions

### In `zktest/utils.py` (Existing)

```python
# Device Connection
class ZKDeviceConnection:
    """TCP connection wrapper for PyZK"""
    
# Sync Functions
sync_users_from_device_tcp(device)
sync_attendance_from_device_tcp(device, clear_after_sync)
sync_all_from_device_tcp(device, clear_attendance)
execute_tcp_command(device, command_type)
```

### In `zktest/api/utils.py` (New)

```python
# Date Helpers
get_date_range(range_type)  # today, 7days, 30days, month, custom
parse_date_param(date_str)

# Import Helpers
import_attendance_logs(device, records, source='tcp')
import_device_users(device, users, source='tcp')

# Query Helpers
get_attendance_logs_filtered(device_id, user_id, date_from, date_to)
get_device_users_filtered(device_id, is_active, has_fp, has_face)

# Response Helpers
success_response(data, message)
error_response(message, errors)

# Pagination
paginate_queryset(queryset, page, per_page)

# Employee Sync
auto_create_employee_from_device_user(device_user)
```

---

## Benefits

### 1. **Scalable Architecture**
- Separated concerns (ADMS vs PyZK)
- Reusable utilities
- Easy to maintain

### 2. **No Duplicates**
- Import only new data
- Automatic duplicate detection
- Safe to run multiple times

### 3. **Flexible Fetching**
- Fetch by date range
- Fetch by user
- Fetch all or specific records

### 4. **Unified Data Model**
- Same AttendanceLog for both protocols
- Consistent data structure
- Easy reporting

### 5. **Auto-Employee Creation**
- Automatic employee records
- Immediate attendance tracking
- Reduces manual work

---

## Configuration

### Device Setup

In Django Admin, configure device:

```python
# For TCP/PyZK devices
connection_type = 'tcp'  # or 'both'
ip_address = '192.168.1.201'
port = 4370
tcp_timeout = 5
tcp_password = ''  # Optional comm key
```

---

## Testing

### 1. Test Connection
```bash
POST /api/pyzk/devices/1/test-connection/
```

### 2. Fetch Users
```bash
POST /api/pyzk/devices/1/fetch-users/
{
  "import_new": true,
  "auto_create_employees": true
}
```

### 3. Fetch Today's Attendance
```bash
POST /api/pyzk/devices/1/fetch-attendance/
{
  "date_range": "today",
  "import_new": true
}
```

---

## Troubleshooting

### Connection Failed
- Check device IP and port
- Verify device is powered on
- Check network connectivity
- Verify TCP password if set

### No Data Imported
- Check date range
- Verify device has data
- Check sync logs for errors

### Duplicates
- Should not happen (uses get_or_create)
- Check unique_together constraint
- Review import logic

---

## Next Steps

1. **Install PyZK Library**
   ```bash
   pip install pyzk
   ```

2. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Configure Devices**
   - Set connection_type to 'tcp' or 'both'
   - Add IP address and port

4. **Test APIs**
   - Use Postman or curl
   - Test connection first
   - Then fetch users and attendance

5. **Schedule Sync**
   - Use Celery or cron
   - Fetch attendance daily
   - Import users weekly

---

## Summary

✅ **ADMS APIs** - Unchanged, working as before
✅ **PyZK APIs** - New, separated, powerful
✅ **Shared Models** - Same AttendanceLog for both
✅ **Import Only New** - No duplicates
✅ **Flexible Dates** - today, 7days, 30days, month, custom
✅ **Auto Employees** - Automatic employee creation
✅ **Scalable** - Clean architecture, easy to maintain

Your system now supports both modern (ADMS) and old (PyZK) ZKTeco devices with a unified, scalable architecture!
