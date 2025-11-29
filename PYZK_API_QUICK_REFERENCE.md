# PyZK API Quick Reference

## 4 Essential APIs Only

### 1. Fetch Users
```bash
POST /api/pyzk/devices/{device_id}/fetch-users/
```

**Request:**
```json
{
  "import_new": true,
  "auto_create_employees": true
}
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
    "employees_created": 8,
    "errors": []
  }
}
```

---

### 2. Import Users
```bash
POST /api/pyzk/devices/{device_id}/import-users/
```

**Request:**
```json
{
  "auto_create_employees": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Imported 10 new users",
  "data": {
    "total": 150,
    "imported": 10,
    "skipped": 140,
    "failed": 0,
    "employees_created": 8,
    "errors": []
  }
}
```

---

### 3. Fetch Attendance
```bash
POST /api/pyzk/devices/{device_id}/fetch-attendance/
```

**Request (Today):**
```json
{
  "date_range": "today",
  "import_new": true
}
```

**Request (7 Days):**
```json
{
  "date_range": "7days",
  "import_new": true
}
```

**Request (30 Days):**
```json
{
  "date_range": "30days",
  "import_new": true
}
```

**Request (Custom Range):**
```json
{
  "date_range": "custom",
  "date_from": "2024-01-01",
  "date_to": "2024-01-31",
  "user_id": "123",
  "import_new": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Fetched 250 records, imported 50 new records",
  "data": {
    "total": 250,
    "imported": 50,
    "skipped": 200,
    "failed": 0,
    "date_range": {
      "from": "2024-01-15",
      "to": "2024-01-15"
    },
    "errors": []
  }
}
```

---

### 4. Import Attendance
```bash
POST /api/pyzk/devices/{device_id}/import-attendance/
```

**Request:**
```json
{
  "clear_after_sync": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Imported 50 new attendance records",
  "data": {
    "total": 5000,
    "imported": 50,
    "skipped": 4950,
    "failed": 0,
    "errors": []
  }
}
```

---

## Date Range Options

- `today` - Today's records only
- `7days` - Last 7 days
- `30days` - Last 30 days  
- `month` - Current month
- `custom` - Specify date_from and date_to

---

## Key Features

✅ **Import Only New Data** - Never creates duplicates
✅ **Auto-Create Employees** - Automatically creates Employee records
✅ **Flexible Date Ranges** - today, 7days, 30days, month, custom
✅ **User Filtering** - Filter by specific user_id
✅ **Clear After Sync** - Optional device memory clearing

---

## Setup

1. **Install PyZK:**
   ```bash
   pip install pyzk
   ```

2. **Configure Device in Admin:**
   - Set `connection_type` to `tcp` or `both`
   - Add `ip_address` (e.g., 192.168.1.201)
   - Set `port` (default: 4370)
   - Optional: Set `tcp_password`

3. **Test:**
   ```bash
   curl -X POST http://localhost:8000/api/pyzk/devices/1/fetch-users/ \
     -H "Content-Type: application/json" \
     -d '{"import_new": true, "auto_create_employees": true}'
   ```

---

## Architecture

```
zktest/
├── api/
│   ├── pyzk_views.py          # 4 APIs + helper functions
│   ├── pyzk_serializers.py    # Serializers
│   ├── utils.py                # Shared utilities
│   └── urls.py                 # URL routing
│
└── utils.py                    # ZKDeviceConnection class only
```

---

## That's It!

Only 4 APIs you need:
1. Fetch Users
2. Import Users
3. Fetch Attendance
4. Import Attendance

Simple, clean, and powerful! 🚀
