# ==================== hr/utils/zk_device_manager.py ====================
"""
ZKTeco Device Manager - Connect and sync with multiple ZKTeco devices
"""

from zk import ZK
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import logging

from hr.models import ZkDevice, Employee, AttendanceLog

logger = logging.getLogger(__name__)


class ZKDeviceManager:
    """Manager for ZKTeco device operations"""
    
    def __init__(self, device):
        """
        Initialize device manager
        :param device: ZkDevice model instance
        """
        self.device = device
        self.zk = ZK(
            ip=device.ip_address,
            port=device.port,
            timeout=5,
            password=device.password if device.password else 0,
            force_udp=False,
            ommit_ping=False
        )
        self.conn = None
    
    def connect(self):
        """Connect to device"""
        try:
            self.conn = self.zk.connect()
            logger.info(f"Connected to device: {self.device.name} ({self.device.ip_address})")
            return True, "Connected successfully"
        except Exception as e:
            logger.error(f"Failed to connect to {self.device.name}: {str(e)}")
            return False, f"Connection failed: {str(e)}"
    
    def disconnect(self):
        """Disconnect from device"""
        try:
            if self.conn:
                self.conn.disconnect()
                logger.info(f"Disconnected from device: {self.device.name}")
        except Exception as e:
            logger.error(f"Error disconnecting from {self.device.name}: {str(e)}")
    
    def get_device_info(self):
        """Get device information"""
        if not self.conn:
            return None
        
        try:
            return {
                'firmware_version': self.conn.get_firmware_version(),
                'serialnumber': self.conn.get_serialnumber(),
                'platform': self.conn.get_platform(),
                'device_name': self.conn.get_device_name(),
                'face_version': self.conn.get_face_version(),
                'fp_version': self.conn.get_fp_version(),
                'extend_fmt': self.conn.get_extend_fmt(),
                'user_extend_fmt': self.conn.get_user_extend_fmt(),
                'face_fun_on': self.conn.get_face_fun_on(),
                'compat_old_firmware': self.conn.get_compat_old_firmware(),
                'network_params': self.conn.get_network_params(),
                'pin_width': self.conn.get_pin_width(),
            }
        except Exception as e:
            logger.error(f"Error getting device info from {self.device.name}: {str(e)}")
            return None
    
    def import_users(self):
        """
        Import users from device and create/update Employee records
        Returns: (success_count, error_count, messages)
        """
        if not self.conn:
            return 0, 0, ["Not connected to device"]
        
        success_count = 0
        error_count = 0
        messages = []
        
        try:
            users = self.conn.get_users()
            logger.info(f"Found {len(users)} users on device {self.device.name}")
            
            with transaction.atomic():
                for user in users:
                    try:
                        # Check if employee exists by zkteco_id
                        employee = Employee.objects.filter(
                            zkteco_id=str(user.user_id),
                            company=self.device.company
                        ).first()
                        
                        if employee:
                            # Update existing employee
                            if user.name:
                                employee.first_name = user.name
                            employee.save()
                            messages.append(f"Updated employee: {user.user_id} - {user.name}")
                            success_count += 1
                        else:
                            # Check if employee_id already exists
                            emp_id = f"EMP-{user.user_id}"
                            if Employee.objects.filter(employee_id=emp_id, company=self.device.company).exists():
                                emp_id = f"EMP-{user.user_id}-{self.device.id}"
                            
                            # Create new employee
                            employee = Employee.objects.create(
                                company=self.device.company,
                                employee_id=emp_id,
                                zkteco_id=str(user.user_id),
                                first_name=user.name or f"User {user.user_id}",
                                is_active=True
                            )
                            messages.append(f"Created employee: {user.user_id} - {user.name}")
                            success_count += 1
                    
                    except Exception as e:
                        error_count += 1
                        messages.append(f"Error importing user {user.user_id}: {str(e)}")
                        logger.error(f"Error importing user {user.user_id}: {str(e)}")
            
            return success_count, error_count, messages
        
        except Exception as e:
            logger.error(f"Error importing users from {self.device.name}: {str(e)}")
            return 0, 1, [f"Error importing users: {str(e)}"]
    
    def import_attendance_logs(self, days=None):
        """
        Import attendance logs from device
        :param days: Number of days to filter (0=today, 7=last 7 days, 30=last 30 days, None=all)
        Returns: (success_count, duplicate_count, error_count, messages)
        """
        if not self.conn:
            return 0, 0, 0, ["Not connected to device"]
        
        success_count = 0
        duplicate_count = 0
        error_count = 0
        messages = []
        
        try:
            from datetime import datetime, timedelta
            from django.utils.timezone import make_aware, is_naive
            
            attendances = self.conn.get_attendance()
            logger.info(f"Found {len(attendances)} attendance records on device {self.device.name}")
            
            # Filter by date if days parameter is provided
            if days is not None:
                if days == 0:
                    # Today only - make naive for comparison
                    start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    start_date_naive = timezone.localtime(start_date).replace(tzinfo=None)
                else:
                    # Last N days - make naive for comparison
                    start_date = timezone.now() - timedelta(days=days)
                    start_date_naive = timezone.localtime(start_date).replace(tzinfo=None)
                
                # Filter attendances - compare naive datetimes
                filtered_attendances = []
                for att in attendances:
                    att_timestamp = att.timestamp
                    if is_naive(att_timestamp):
                        # Device timestamp is naive, compare directly
                        if att_timestamp >= start_date_naive:
                            filtered_attendances.append(att)
                    else:
                        # Device timestamp is aware, make it naive for comparison
                        att_timestamp_naive = timezone.localtime(att_timestamp).replace(tzinfo=None)
                        if att_timestamp_naive >= start_date_naive:
                            filtered_attendances.append(att)
                
                logger.info(f"Filtered to {len(filtered_attendances)} records for last {days if days > 0 else 'today'} days")
                attendances = filtered_attendances
            
            with transaction.atomic():
                for att in attendances:
                    try:
                        # Find employee by zkteco_id
                        employee = Employee.objects.filter(
                            zkteco_id=str(att.user_id),
                            company=self.device.company
                        ).first()
                        
                        if not employee:
                            error_count += 1
                            messages.append(f"Employee not found for ZKTeco ID: {att.user_id}")
                            continue
                        
                        # Check for duplicate - ALWAYS SKIP DUPLICATES
                        existing_log = AttendanceLog.objects.filter(
                            device=self.device,
                            employee=employee,
                            timestamp=att.timestamp,
                            company=self.device.company
                        ).exists()
                        
                        if existing_log:
                            duplicate_count += 1
                            continue
                        
                        # Determine attendance type
                        attendance_type = ''
                        if att.status == 0:
                            attendance_type = 'in'
                        elif att.status == 1:
                            attendance_type = 'out'
                        
                        # Make timestamp timezone-aware
                        timestamp = att.timestamp
                        if is_naive(timestamp):
                            timestamp = make_aware(timestamp)
                        
                        # Create attendance log
                        AttendanceLog.objects.create(
                            company=self.device.company,
                            device=self.device,
                            employee=employee,
                            timestamp=timestamp,
                            source_type='zk',
                            attendance_type=attendance_type,
                            status_code=att.status,
                            punch_type=str(att.punch)
                        )
                        success_count += 1
                    
                    except Exception as e:
                        error_count += 1
                        messages.append(f"Error importing attendance for user {att.user_id}: {str(e)}")
                        logger.error(f"Error importing attendance: {str(e)}")
            
            # Update last synced time
            self.device.last_synced = timezone.now()
            self.device.save()
            
            messages.append(f"Imported {success_count} new records, {duplicate_count} duplicates skipped, {error_count} errors")
            return success_count, duplicate_count, error_count, messages
        
        except Exception as e:
            logger.error(f"Error importing attendance from {self.device.name}: {str(e)}")
            return 0, 0, 1, [f"Error importing attendance: {str(e)}"]
    
    def clear_attendance_logs(self):
        """Clear attendance logs from device"""
        if not self.conn:
            return False, "Not connected to device"
        
        try:
            self.conn.clear_attendance()
            logger.info(f"Cleared attendance logs from device: {self.device.name}")
            return True, "Attendance logs cleared successfully"
        except Exception as e:
            logger.error(f"Error clearing attendance from {self.device.name}: {str(e)}")
            return False, f"Error clearing attendance: {str(e)}"
    
    def test_voice(self):
        """Test device voice"""
        if not self.conn:
            return False, "Not connected to device"
        
        try:
            self.conn.test_voice()
            return True, "Voice test successful"
        except Exception as e:
            logger.error(f"Error testing voice on {self.device.name}: {str(e)}")
            return False, f"Error testing voice: {str(e)}"
    
    def restart_device(self):
        """Restart device"""
        if not self.conn:
            return False, "Not connected to device"
        
        try:
            self.conn.restart()
            return True, "Device restart command sent"
        except Exception as e:
            logger.error(f"Error restarting {self.device.name}: {str(e)}")
            return False, f"Error restarting device: {str(e)}"
    
    def poweroff_device(self):
        """Power off device"""
        if not self.conn:
            return False, "Not connected to device"
        
        try:
            self.conn.poweroff()
            return True, "Device poweroff command sent"
        except Exception as e:
            logger.error(f"Error powering off {self.device.name}: {str(e)}")
            return False, f"Error powering off device: {str(e)}"


def sync_multiple_devices(device_ids):
    """
    Sync multiple devices
    :param device_ids: List of device IDs
    :return: Dictionary with results for each device
    """
    results = {}
    
    for device_id in device_ids:
        try:
            device = ZkDevice.objects.get(id=device_id, is_active=True)
            manager = ZKDeviceManager(device)
            
            # Connect
            connected, msg = manager.connect()
            if not connected:
                results[device.name] = {
                    'success': False,
                    'message': msg,
                    'users_imported': 0,
                    'attendance_imported': 0,
                    'duplicates': 0,
                    'errors': 0
                }
                continue
            
            # Import users
            users_success, users_error, user_messages = manager.import_users()
            
            # Import attendance
            att_success, att_duplicates, att_error, att_messages = manager.import_attendance_logs()
            
            # Disconnect
            manager.disconnect()
            
            results[device.name] = {
                'success': True,
                'message': 'Sync completed',
                'users_imported': users_success,
                'users_errors': users_error,
                'attendance_imported': att_success,
                'duplicates': att_duplicates,
                'attendance_errors': att_error,
                'messages': user_messages + att_messages
            }
        
        except ZkDevice.DoesNotExist:
            results[f"Device {device_id}"] = {
                'success': False,
                'message': 'Device not found or inactive'
            }
        except Exception as e:
            results[f"Device {device_id}"] = {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    return results
