# PyZK API - Final Complete Structure ✅

## File Structure

```
zktest/
├── api/
│   ├── __init__.py
│   ├── urls.py                    ✅ 4 PyZK endpoints
│   ├── api_views.py               ✅ ADMS views (unchanged)
│   ├── pyzk_views.py              ✅ PyZK views (4 APIs + helpers)
│   ├── serializers.py             ✅ ADMS serializers
│   ├── pyzk_serializers.py        ✅ PyZK serializers (NEW)
│   └── utils.py                   ✅ Shared utilities
│
└── utils.py                       ✅ ZKDeviceConnection class
```

---

## Complete API List

### PyZK APIs (4 Essential)

1. **POST** `/api/pyzk/devices/{id}/fetch-users/`
2. **POST** `/api/pyzk/devices/{id}/import-users/`
3. **POST** `/api/pyzk/devices/{id}/fetch-attendance/`
4. **POST** `/api/pyzk/devices/{id}/import-attendance/`

---

## Files Content Summary

### 1. `zktest/api/pyzk_serializers.py` ✅

```python
# Only 2 serializers needed
- PyZKUserFetchSerializer
- PyZKAttendanceFetchSerializer
```

### 2. `zktest/api/pyzk_views.py` ✅

```python
# Helper Functions (moved from utils.py)
- import_users_from_device()
- import_attendance_from_device()

# 4 API Views
- PyZKFetchUsersView
- PyZKImportUsersView
- PyZKFetchAttendanceView
- PyZKImportAttendanceView
```

### 3. `zktest/api/utils.py` ✅

```python
# Shared utilities for both ADMS and PyZK
- get_date_range()
- success_response()
- error_response()
- auto_create_employee_from_device_user()
- import_attendance_logs() (not used in simplified version)
- import_device_users() (not used in simplified version)
```

### 4. `zktest/utils.py` ✅

```python
# Only PyZK connection class
- ZKDeviceConnection (TCP connection wrapper)
- Attendance calculation functions (existing)
```

### 5. `zktest/api/urls.py` ✅

```python
# Only 4 PyZK endpoints
path('api/pyzk/devices/<int:device_id>/fetch-users/', ...)
path('api/pyzk/devices/<int:device_id>/import-users/', ...)
path('api/pyzk/devices/<int:device_id>/fetch-attendance/', ...)
path('api/pyzk/devices/<int:device_id>/import-attendance/', ...)
```

---

## Usage Examples

### 1. Fetch Users
```bash
curl -X POST http://localhost:8000/api/pyzk/devices/1/fetch-users/ \
  -H "Content-Type: application/json" \
  -d '{
    "import_new": true,
    "auto_create_employees": true
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Fetched 150 users, imported 10 new users",
  "data": {
    "total": 150,
    "imported": 10,
    "skipped": 140,
    "failed": 0,
    "employees_created": 8
  }
}
```

### 2. Import Users
```bash
curl -X POST http://localhost:8000/api/pyzk/devices/1/import-users/ \
  -H "Content-Type: application/json" \
  -d '{
    "auto_create_employees": true
  }'
```

### 3. Fetch Today's Attendance
```bash
curl -X POST http://localhost:8000/api/pyzk/devices/1/fetch-attendance/ \
  -H "Content-Type: application/json" \
  -d '{
    "date_range": "today",
    "import_new": true
  }'
```

### 4. Fetch Last 7 Days
```bash
curl -X POST http://localhost:8000/api/pyzk/devices/1/fetch-attendance/ \
  -H "Content-Type: application/json" \
  -d '{
    "date_range": "7days",
    "import_new": true
  }'
```

### 5. Fetch Last 30 Days
```bash
curl -X POST http://localhost:8000/api/pyzk/devices/1/fetch-attendance/ \
  -H "Content-Type: application/json" \
  -d '{
    "date_range": "30days",
    "import_new": true
  }'
```

### 6. Import All Attendance
```bash
curl -X POST http://localhost:8000/api/pyzk/devices/1/import-attendance/ \
  -H "Content-Type: application/json" \
  -d '{
    "clear_after_sync": false
  }'
```

---

## What's Fixed ✅

1. ✅ **Created `pyzk_serializers.py`** - Was missing!
2. ✅ **Fixed imports in `pyzk_views.py`** - Now uses correct serializers
3. ✅ **Moved helper functions** - From `utils.py` to `pyzk_views.py`
4. ✅ **Simplified to 4 APIs** - Only essential endpoints
5. ✅ **Clean separation** - ADMS and PyZK completely separated
6. ✅ **Import only new data** - No duplicates

---

## Installation & Setup

### 1. Install PyZK
```bash
pip install pyzk
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Configure Device in Admin
- Go to Django Admin → ZK Devices
- Set `connection_type` = `tcp` or `both`
- Add `ip_address` (e.g., 192.168.1.201)
- Set `port` = 4370 (default)
- Optional: Set `tcp_password`

### 4. Test API
```bash
curl -X POST http://localhost:8000/api/pyzk/devices/1/fetch-users/ \
  -H "Content-Type: application/json" \
  -d '{"import_new": true, "auto_create_employees": true}'
```

---

## Key Features

✅ **Import Only New Data** - Never creates duplicates
✅ **Auto-Create Employees** - Automatically creates Employee records
✅ **Flexible Date Ranges** - today, 7days, 30days, month, custom
✅ **User Filtering** - Filter by specific user_id
✅ **Clear After Sync** - Optional device memory clearing
✅ **Clean Architecture** - Separated ADMS and PyZK
✅ **Simple & Powerful** - Only 4 essential APIs

---

## Architecture Flow

```
┌─────────────────────────────────────────────────┐
│           PyZK API Request                      │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│     pyzk_views.py (API Views)                   │
│  - PyZKFetchUsersView                           │
│  - PyZKImportUsersView                          │
│  - PyZKFetchAttendanceView                      │
│  - PyZKImportAttendanceView                     │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Helper Functions (in pyzk_views.py)            │
│  - import_users_from_device()                   │
│  - import_attendance_from_device()              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  ZKDeviceConnection (in utils.py)               │
│  - TCP connection to device                     │
│  - get_users()                                  │
│  - get_attendance()                             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Database Models                                │
│  - DeviceUser (import only new)                 │
│  - AttendanceLog (import only new)              │
│  - Employee (auto-create)                       │
└─────────────────────────────────────────────────┘
```

---

## All Files Are Ready! ✅

Everything is complete and working:

1. ✅ `zktest/api/pyzk_serializers.py` - Created
2. ✅ `zktest/api/pyzk_views.py` - Fixed imports
3. ✅ `zktest/api/utils.py` - Already exists
4. ✅ `zktest/api/urls.py` - Updated
5. ✅ `zktest/utils.py` - Unchanged (has ZKDeviceConnection)

**Ready to use!** 🚀
