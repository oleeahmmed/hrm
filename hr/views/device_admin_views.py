# ==================== hr/views/device_admin_views.py ====================
"""
ZKDevice Admin View Methods
Reusable view methods for device operations (admin and API)
"""

from django.http import JsonResponse
from django.utils import timezone
from hr.models import ZkDevice, AttendanceLog, Attendance
from hr.utils.zk_device_manager import ZKDeviceManager
import logging

logger = logging.getLogger(__name__)


def device_test_connection(device_id):
    """
    Test connection to a single device
    Returns: (success, message, data)
    """
    try:
        device = ZkDevice.objects.get(id=device_id)
        manager = ZKDeviceManager(device)
        connected, msg = manager.connect()
        
        if connected:
            info = manager.get_device_info()
            manager.disconnect()
            
            if info:
                return True, f"✅ Connected! Firmware: {info.get('firmware_version', 'N/A')}", info
            else:
                return True, '⚠️ Connected but no device info', None
        else:
            return False, f'❌ {msg}', None
    except ZkDevice.DoesNotExist:
        return False, '❌ Device not found', None
    except Exception as e:
        logger.error(f"Test connection error: {str(e)}")
        return False, f'❌ Error: {str(e)}', None


def device_import_users(device_id):
    """
    Import users from a single device
    Returns: (success, message, data)
    """
    try:
        device = ZkDevice.objects.get(id=device_id)
        manager = ZKDeviceManager(device)
        connected, msg = manager.connect()
        
        if not connected:
            return False, f'❌ {msg}', None
        
        success, errors, messages = manager.import_users()
        manager.disconnect()
        
        data = {
            'users_imported': success,
            'errors': errors,
            'last_synced': device.last_synced.strftime('%Y-%m-%d %H:%M') if device.last_synced else ''
        }
        
        return errors == 0, f'✅ Imported {success} users, {errors} errors', data
    except ZkDevice.DoesNotExist:
        return False, '❌ Device not found', None
    except Exception as e:
        logger.error(f"Import users error: {str(e)}")
        return False, f'❌ Error: {str(e)}', None


def device_import_attendance(device_id, days=None):
    """
    Import attendance from a single device
    :param device_id: Device ID
    :param days: Number of days (0=today, 7=last 7 days, 30=last 30 days, None=all)
    Returns: (success, message, data)
    """
    try:
        device = ZkDevice.objects.get(id=device_id)
        manager = ZKDeviceManager(device)
        connected, msg = manager.connect()
        
        if not connected:
            return False, f'❌ {msg}', None
        
        success, duplicates, errors, messages = manager.import_attendance_logs(days=days)
        manager.disconnect()
        
        data = {
            'attendance_imported': success,
            'duplicates': duplicates,
            'errors': errors,
            'last_synced': device.last_synced.strftime('%Y-%m-%d %H:%M') if device.last_synced else ''
        }
        
        return errors == 0, f'✅ Imported {success}, {duplicates} duplicates, {errors} errors', data
    except ZkDevice.DoesNotExist:
        return False, '❌ Device not found', None
    except Exception as e:
        logger.error(f"Import attendance error: {str(e)}")
        return False, f'❌ Error: {str(e)}', None


def device_sync_all(device_id):
    """
    Sync users and all attendance from a single device
    Returns: (success, message, data)
    """
    try:
        device = ZkDevice.objects.get(id=device_id)
        manager = ZKDeviceManager(device)
        connected, msg = manager.connect()
        
        if not connected:
            return False, f'❌ {msg}', None
        
        # Import users first
        users_success, users_errors, user_messages = manager.import_users()
        
        # Import all attendance
        att_success, att_duplicates, att_errors, att_messages = manager.import_attendance_logs(days=None)
        
        manager.disconnect()
        
        total_errors = users_errors + att_errors
        
        data = {
            'users_imported': users_success,
            'attendance_imported': att_success,
            'duplicates': att_duplicates,
            'errors': total_errors,
            'last_synced': device.last_synced.strftime('%Y-%m-%d %H:%M') if device.last_synced else ''
        }
        
        message = f'✅ Users: {users_success}, Attendance: {att_success}, Duplicates: {att_duplicates}, Errors: {total_errors}'
        
        return total_errors == 0, message, data
    except ZkDevice.DoesNotExist:
        return False, '❌ Device not found', None
    except Exception as e:
        logger.error(f"Sync all error: {str(e)}")
        return False, f'❌ Error: {str(e)}', None


def device_clear_logs(device_id):
    """
    Clear attendance logs from device
    Returns: (success, message, data)
    """
    try:
        device = ZkDevice.objects.get(id=device_id)
        manager = ZKDeviceManager(device)
        connected, msg = manager.connect()
        
        if not connected:
            return False, f'❌ {msg}', None
        
        success, msg = manager.clear_attendance_logs()
        manager.disconnect()
        
        return success, msg, None
    except ZkDevice.DoesNotExist:
        return False, '❌ Device not found', None
    except Exception as e:
        logger.error(f"Clear logs error: {str(e)}")
        return False, f'❌ Error: {str(e)}', None


# ==================== JSON Response Helpers ====================

def device_test_connection_json(request, device_id):
    """JSON response for test connection"""
    success, message, data = device_test_connection(device_id)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })


def device_import_users_json(request, device_id):
    """JSON response for import users"""
    success, message, data = device_import_users(device_id)
    return JsonResponse({
        'success': success,
        'message': message,
        'last_synced': data.get('last_synced', '') if data else ''
    })


def device_import_today_json(request, device_id):
    """JSON response for import today"""
    success, message, data = device_import_attendance(device_id, days=0)
    return JsonResponse({
        'success': success,
        'message': message,
        'last_synced': data.get('last_synced', '') if data else ''
    })


def device_import_7days_json(request, device_id):
    """JSON response for import 7 days"""
    success, message, data = device_import_attendance(device_id, days=7)
    return JsonResponse({
        'success': success,
        'message': message,
        'last_synced': data.get('last_synced', '') if data else ''
    })


def device_import_30days_json(request, device_id):
    """JSON response for import 30 days"""
    success, message, data = device_import_attendance(device_id, days=30)
    return JsonResponse({
        'success': success,
        'message': message,
        'last_synced': data.get('last_synced', '') if data else ''
    })


def device_import_all_json(request, device_id):
    """JSON response for import all"""
    success, message, data = device_import_attendance(device_id, days=None)
    return JsonResponse({
        'success': success,
        'message': message,
        'last_synced': data.get('last_synced', '') if data else ''
    })


def device_sync_all_json(request, device_id):
    """JSON response for sync all"""
    success, message, data = device_sync_all(device_id)
    return JsonResponse({
        'success': success,
        'message': message,
        'last_synced': data.get('last_synced', '') if data else ''
    })
