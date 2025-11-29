# ZKTeco Device API Documentation

Complete API documentation for both ADMS (push-based) and PyZK (TCP pull-based) protocols.

---

## Table of Contents

1. [ADMS Protocol APIs](#adms-protocol-apis)
2. [PyZK (TCP) APIs](#pyzk-tcp-apis)
3. [Common Concepts](#common-concepts)
4. [Examples](#examples)

---

## ADMS Protocol APIs

ADMS is a push-based protocol where devices automatically send data to the server.

### Device Communication

#### 1. Device Handshake
```
GET /iclock/cdata?SN=<serial_number>
```
Device connects and gets commands from server.

#### 2. Data Push
```
POST /iclock/cdata?SN=<serial_number>&table=<TABLE_NAME>
```
Device pushes data (attendance, users, etc.)

**Supported Tables:**
- `ATTLOG` - Attendance logs
- `USER` / `USERINFO` - User data
- `OPERLOG` - Operation logs
- `FINGERTMP` / `TEMPLATEV10` - Fingerprint templates
- `FACE` - Face templates

---

## PyZK (TCP) APIs

PyZK APIs are for old ZKTeco devices that don't support ADMS. Server actively connects to device via TCP.

### Base URL
```
/api/pyzk/
```

---

### Device Management

#### 1. List TCP Devices
```http
GET /api/pyzk/devices/
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z",
  "count": 2,
  "data": [
    {
      "id": 1,
      "serial_number": "ABCD1234",
      "device_name": "Main Gate",
      "ip_address": "192.168.1.201",
      "port": 4370,
      "connection_type": "tcp",
      "is_online": true,
      "user_count": 150,
      "transaction_count": 5000
    }
  ]
}
```

#### 2. Get Device Details
```http
GET /api/pyzk/devices/{device_id}/
```

#### 3. Test Connection
```http
POST /api/pyzk/devices/{device_id}/test-connection/
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "data": {
    "device_info": {
      "serial_number": "ABCD1234",
      "device_name": "Main Gate",
      "platform": "ZEM560",
      "firmware_version": "Ver 6.60",
      "mac_address": "00:17:61:12:34:56"
    },
    "device_time": "2024-01-15 10:30:00",
    "server_time": "2024-01-15T10:30:00Z"
  }
}
```

---

### User Operations

#### 1. Fetch Users from Device
```http
POST /api/pyzk/devices/{device_id}/fetch-users/
```

**Request Body:**
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
  "message": "Fetched 150 users from device",
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

#### 2. Import Users (Explicit)
```http
POST /api/pyzk/devices/{device_id}/import-users/
```

**Request Body:**
```json
{
  "auto_create_employees": true
}
```

#### 3. Get Device Users (from Database)
```http
GET /api/pyzk/devices/{device_id}/users/?page=1&per_page=50
```

**Query Parameters:**
- `is_active` - Filter by active status (true/false)
- `has_fingerprint` - Filter by fingerprint enrollment (true/false)
- `has_face` - Filter by face enrollment (true/false)
- `page` - Page number (default: 1)
- `per_page` - Records per page (default: 50, max: 200)

---

### Attendance Operations

#### 1. Fetch Attendance from Device
```http
POST /api/pyzk/devices/{device_id}/fetch-attendance/
```

**Request Body:**
```json
{
  "date_range": "today",
  "user_id": "",
  "import_new": true
}
```

**Date Range Options:**
- `today` - Today's records
- `7days` - Last 7 days
- `30days` - Last 30 days
- `month` - Current month
- `custom` - Custom range (requires date_from and date_to)

**Custom Range Example:**
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
  "message": "Fetched 250 attendance records",
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

#### 2. Import All Attendance
```http
POST /api/pyzk/devices/{device_id}/import-attendance/
```

**Request Body:**
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
    "failed": 0
  }
}
```

#### 3. Get Attendance Logs (from Database)
```http
GET /api/pyzk/devices/{device_id}/attendance-logs/
```

**Query Parameters:**
- `date_range` - today|7days|30days|month|custom
- `date_from` - YYYY-MM-DD (for custom range)
- `date_to` - YYYY-MM-DD (for custom range)
- `user_id` - Filter by specific user
- `page` - Page number
- `per_page` - Records per page

**Example:**
```http
GET /api/pyzk/devices/1/attendance-logs/?date_range=7days&user_id=123&page=1&per_page=50
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z",
  "date_range": {
    "from": "2024-01-09",
    "to": "2024-01-15"
  },
  "total": 150,
  "page": 1,
  "per_page": 50,
  "total_pages": 3,
  "data": [
    {
      "id": 1001,
      "device": 1,
      "device_name": "Main Gate",
      "user_id": "123",
      "punch_time": "2024-01-15T09:00:00Z",
      "punch_type": 0,
      "punch_type_display": "Check In",
      "verify_type": 1,
      "verify_type_display": "Fingerprint",
      "source": "tcp",
      "temperature": 36.5,
      "is_synced": false,
      "created_at": "2024-01-15T09:00:05Z"
    }
  ]
}
```

---

### Device Commands

#### Execute Command
```http
POST /api/pyzk/devices/{device_id}/execute-command/
```

**Request Body:**
```json
{
  "command": "reboot"
}
```

**Available Commands:**
- `reboot` - Restart device
- `sync_time` - Synchronize device time with server
- `clear_attendance` - Clear all attendance logs from device
- `get_info` - Get device information
- `get_time` - Get device current time
- `test_connection` - Test connection

**Response:**
```json
{
  "success": true,
  "message": "Device restart command sent",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Sync All Data

#### Sync Users + Attendance
```http
POST /api/pyzk/devices/{device_id}/sync-all/
```

**Request Body:**
```json
{
  "clear_attendance": false,
  "auto_create_employees": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Sync completed successfully",
  "data": {
    "users": {
      "success": true,
      "total": 150,
      "imported": 10,
      "skipped": 140
    },
    "attendance": {
      "success": true,
      "total": 5000,
      "imported": 50,
      "skipped": 4950
    },
    "employees_created": 8
  }
}
```

---

### Sync Logs

#### Get Sync History
```http
GET /api/pyzk/devices/{device_id}/sync-logs/
```

**Query Parameters:**
- `sync_type` - users|attendance|all
- `status` - pending|running|completed|failed

**Response:**
```json
{
  "success": true,
  "count": 10,
  "data": [
    {
      "id": 1,
      "device": 1,
      "device_name": "Main Gate",
      "sync_type": "attendance",
      "status": "completed",
      "records_found": 5000,
      "records_synced": 50,
      "records_failed": 0,
      "duration": "2.35s",
      "started_at": "2024-01-15T10:00:00Z",
      "completed_at": "2024-01-15T10:00:02Z"
    }
  ]
}
```

---

## Common Concepts

### Date Ranges

All attendance fetch APIs support these date ranges:

1. **today** - Today's records only
2. **7days** - Last 7 days (including today)
3. **30days** - Last 30 days (including today)
4. **month** - Current month from 1st to today
5. **custom** - Specify exact dates

### Import Behavior

**Import Only New Data:**
- Users: Only creates new users, never updates existing
- Attendance: Only imports new records, skips duplicates
- Uses `get_or_create` to prevent duplicates

### Auto-Create Employees

When `auto_create_employees: true`:
- Automatically creates Employee records for new DeviceUsers
- Splits name into first_name and last_name
- Sets user_id to match device user_id
- Enables immediate attendance tracking

---

## Examples

### Example 1: Daily Attendance Import

```bash
# Fetch today's attendance from all TCP devices
curl -X POST http://localhost:8000/api/pyzk/devices/1/fetch-attendance/ \
  -H "Content-Type: application/json" \
  -d '{
    "date_range": "today",
    "import_new": true
  }'
```

### Example 2: Weekly Attendance Report

```bash
# Get last 7 days attendance
curl -X GET "http://localhost:8000/api/pyzk/devices/1/attendance-logs/?date_range=7days&page=1&per_page=100"
```

### Example 3: Import New Users

```bash
# Import users and auto-create employees
curl -X POST http://localhost:8000/api/pyzk/devices/1/import-users/ \
  -H "Content-Type: application/json" \
  -d '{
    "auto_create_employees": true
  }'
```

### Example 4: Full Device Sync

```bash
# Sync everything (users + attendance)
curl -X POST http://localhost:8000/api/pyzk/devices/1/sync-all/ \
  -H "Content-Type: application/json" \
  -d '{
    "clear_attendance": false,
    "auto_create_employees": true
  }'
```

### Example 5: Custom Date Range

```bash
# Fetch specific date range
curl -X POST http://localhost:8000/api/pyzk/devices/1/fetch-attendance/ \
  -H "Content-Type: application/json" \
  -d '{
    "date_range": "custom",
    "date_from": "2024-01-01",
    "date_to": "2024-01-31",
    "import_new": true
  }'
```

---

## Error Handling

All APIs return consistent error responses:

```json
{
  "success": false,
  "message": "Connection failed: Device not reachable",
  "timestamp": "2024-01-15T10:30:00Z",
  "errors": ["Timeout after 5 seconds"]
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (device doesn't exist)
- `503` - Service Unavailable (device offline/unreachable)

---

## Best Practices

1. **Test Connection First**
   - Always test connection before bulk operations
   - Verify device is online and reachable

2. **Use Date Ranges**
   - Don't fetch all attendance at once
   - Use appropriate date ranges (today, 7days, 30days)

3. **Import Only New**
   - Always use `import_new: true`
   - Prevents duplicate records

4. **Auto-Create Employees**
   - Enable for first-time setup
   - Disable if you manage employees separately

5. **Monitor Sync Logs**
   - Check sync logs for failures
   - Review error messages

6. **Clear Device Memory**
   - Use `clear_after_sync: true` periodically
   - Prevents device memory overflow

---

## Support

For issues or questions:
- Check device connection settings (IP, port, password)
- Verify device supports TCP/IP connection
- Review sync logs for detailed error messages
- Ensure `pyzk` library is installed: `pip install pyzk`
