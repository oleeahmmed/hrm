# 🚀 Utils Quick Reference

## Import Everything You Need

```python
from zktest.utils import (
    # Attendance calculations
    get_work_day_range,
    calculate_work_hours,
    calculate_daily_amount,
    generate_attendance_from_logs,
    
    # PyZK TCP operations
    ZKDeviceConnection,
    import_users_from_device,
    import_attendance_from_device,
    execute_device_command,
    
    # API helpers
    get_date_range,
    success_response,
    error_response,
    auto_create_employee_from_device_user,
)
```

## File Locations

| Utility Type | File | Used By |
|-------------|------|---------|
| Attendance calculations | `utils/attendance_utils.py` | mobile_views.py, report_views.py |
| PyZK TCP operations | `utils/pyzk_utils.py` | api/pyzk_views.py |
| API helpers | `utils/api_utils.py` | api/pyzk_views.py, other APIs |

## Common Usage

### Attendance Calculations
```python
from zktest.utils import get_work_day_range, generate_attendance_from_logs

# Get work day range
start, end = get_work_day_range(date)

# Generate attendance from logs
attendance = generate_attendance_from_logs(
    user_id='123',
    date=date.today(),
    attendance_logs=logs,
    per_hour_rate=Decimal('50.00')
)
```

### PyZK Operations
```python
from zktest.utils import ZKDeviceConnection, import_users_from_device

# Connect to device
with ZKDeviceConnection(ip='192.168.1.201', port=4370) as conn:
    users = conn.get_users()
    attendance = conn.get_attendance()

# Import users
result = import_users_from_device(device)
```

### API Responses
```python
from zktest.utils import success_response, error_response

# Success
return Response(success_response(
    message='Operation successful',
    data={'count': 10}
))

# Error
return Response(error_response(
    message='Operation failed',
    errors=['Error 1', 'Error 2']
))
```

## All Available Functions

### Attendance Utils (`attendance_utils.py`)
- ✅ `get_work_day_range(date)` - Returns (start_datetime, end_datetime)
- ✅ `calculate_work_hours(punches, ...)` - Returns work hours dict
- ✅ `calculate_daily_amount(work_hours, rate)` - Returns Decimal amount
- ✅ `generate_attendance_from_logs(...)` - Returns attendance dict

### PyZK Utils (`pyzk_utils.py`)
- ✅ `ZKDeviceConnection(ip, port, ...)` - Context manager for TCP connection
- ✅ `import_users_from_device(device)` - Import users from device
- ✅ `import_attendance_from_device(device, ...)` - Import attendance from device
- ✅ `execute_device_command(device, command_type)` - Execute device command

### API Utils (`api_utils.py`)
- ✅ `get_date_range(range_type)` - Returns (date_from, date_to)
- ✅ `success_response(message, data, ...)` - Returns success dict
- ✅ `error_response(message, data, errors, ...)` - Returns error dict
- ✅ `auto_create_employee_from_device_user(device_user)` - Returns Employee or None

## Quick Tips

1. **Import from `zktest.utils`** - Not from individual files
2. **All functions are exported** - Available in `__init__.py`
3. **No circular imports** - Clean dependency structure
4. **Type hints available** - Check function docstrings

## Testing

```bash
# Test imports
python3 -c "from zktest.utils import get_work_day_range; print('✅')"

# Check Django
python3 manage.py check

# Run server
python3 manage.py runserver
```

Done! 🎉
