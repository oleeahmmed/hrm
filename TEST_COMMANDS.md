# 🧪 Test Commands

## Quick Tests

### 1. Check for errors
```bash
python3 manage.py check
```
**Expected:** `System check identified no issues (0 silenced).`

### 2. Test imports
```bash
# Test utils imports
python3 -c "from zktest.utils import get_work_day_range; print('✅ attendance_utils OK')"
python3 -c "from zktest.utils import ZKDeviceConnection; print('✅ pyzk_utils OK')"
python3 -c "from zktest.utils import success_response; print('✅ api_utils OK')"

# Test API imports
python3 -c "from zktest.api import api_views; print('✅ api_views OK')"
python3 -c "from zktest.api import pyzk_views; print('✅ pyzk_views OK')"

# Test mobile/report imports
python3 -c "from zktest import mobile_views; print('✅ mobile_views OK')"
python3 -c "from zktest import report_views; print('✅ report_views OK')"
```

### 3. Run server
```bash
python3 manage.py runserver
```
**Expected:** Server starts without errors

### 4. Test ADMS endpoint
```bash
curl -X GET "http://localhost:8000/iclock/cdata?SN=TEST001"
```
**Expected:** Response with device settings

### 5. Test PyZK endpoint (if device exists)
```bash
curl -X POST "http://localhost:8000/api/pyzk/devices/1/fetch-users/" \
  -H "Content-Type: application/json" \
  -d '{"import_new": false}'
```
**Expected:** JSON response with users or error if device not found

## Full Test Suite

```bash
# 1. Check Django
python3 manage.py check

# 2. Run migrations (if needed)
python3 manage.py makemigrations
python3 manage.py migrate

# 3. Create superuser (if needed)
python3 manage.py createsuperuser

# 4. Collect static files (if needed)
python3 manage.py collectstatic --noinput

# 5. Run server
python3 manage.py runserver
```

## Expected Results

### ✅ All Tests Pass
- No import errors
- Server starts successfully
- All endpoints accessible
- ADMS and PyZK work independently

### ✅ File Structure
```
zktest/
├── utils/
│   ├── __init__.py          ✅
│   ├── attendance_utils.py  ✅
│   ├── pyzk_utils.py        ✅
│   └── api_utils.py         ✅
├── api/
│   ├── api_views.py         ✅ (ADMS only)
│   ├── pyzk_views.py        ✅ (PyZK only)
│   └── urls.py              ✅
├── mobile_views.py          ✅
└── report_views.py          ✅
```

### ✅ No Errors
- ❌ No `ImportError`
- ❌ No `ModuleNotFoundError`
- ❌ No circular imports
- ❌ No missing functions

## Troubleshooting

### If you see import errors:
```bash
# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Check if utils folder exists
ls -la zktest/utils/

# Check if __init__.py exists
cat zktest/utils/__init__.py
```

### If server won't start:
```bash
# Check for syntax errors
python3 -m py_compile zktest/utils/*.py
python3 -m py_compile zktest/api/*.py

# Check Django settings
python3 manage.py check --deploy
```

## Success Indicators

✅ `python3 manage.py check` - No issues  
✅ `python3 manage.py runserver` - Server starts  
✅ All imports work without errors  
✅ ADMS endpoints respond  
✅ PyZK endpoints respond  
✅ Mobile views work  
✅ Report views work  

Done! 🎉
