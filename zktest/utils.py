# ==================== zktest/utils.py ====================
"""
Utility functions for attendance calculation
"""

from datetime import datetime, timedelta, time
from decimal import Decimal
from django.utils import timezone


def get_work_day_range(date):
    """
    Get work day range: 6:00 AM to next day 4:00 AM
    
    Args:
        date: The work date
    
    Returns:
        tuple: (start_datetime, end_datetime)
    """
    # Work day starts at 6:00 AM
    start_datetime = datetime.combine(date, time(6, 0, 0))
    
    # Work day ends at 4:00 AM next day
    next_day = date + timedelta(days=1)
    end_datetime = datetime.combine(next_day, time(4, 0, 0))
    
    return start_datetime, end_datetime


def calculate_work_hours(punches, break_time_minutes=60, pair_threshold_minutes=30):
    """
    Calculate work hours for hourly-based employees
    
    CORRECT LOGIC:
    1. Total Work Time = Last Punch - First Punch
    2. Calculate breaks between ALL consecutive punches (excluding first and last)
    3. If gap ≤ 30 min = Actual break time (use the gap duration)
    4. If gap > 30 min = Employee forgot to punch, add only 30 min break
    5. Work Hours = Total Time - Total Breaks
    
    Args:
        punches: List of punch datetime objects (sorted)
        break_time_minutes: Not used, calculated automatically
        pair_threshold_minutes: Threshold to detect forgotten punches (default 30)
    
    Returns:
        dict with calculation details
    """
    if not punches or len(punches) == 0:
        return {
            'work_hours': Decimal('0.00'),
            'total_punches': 0,
            'paired_punches': 0,
            'unpaired_punches': 0,
            'paired_time_minutes': 0,
            'break_time_minutes': 0,
            'unpaired_penalty_minutes': 0,
            'first_punch': None,
            'last_punch': None,
            'punch_pairs': [],
            'unpaired_punch_times': [],
            'break_periods': []
        }
    
    # Sort punches
    sorted_punches = sorted(punches)
    total_punches = len(sorted_punches)
    first_punch = sorted_punches[0]
    last_punch = sorted_punches[-1]
    
    # Calculate total work duration (last - first)
    total_duration = last_punch - first_punch
    total_duration_minutes = int(total_duration.total_seconds() / 60)
    
    # Group consecutive punches within 30 min as break periods
    # If punches: 15:00, 15:07, 15:23, 15:28 (all within 30 min)
    # This is ONE break: 15:00 → 15:28 (28 min)
    
    punch_pairs = []
    break_periods = []
    unpaired_punch_times = []
    total_break_minutes = 0
    
    i = 1  # Start from second punch (skip first)
    while i < len(sorted_punches) - 1:  # Stop before last punch
        # Start a potential break group
        break_start = sorted_punches[i]
        break_end = sorted_punches[i]
        group_size = 1
        
        # Look ahead to find all punches within 30 min of break_start
        j = i + 1
        while j < len(sorted_punches) - 1:  # Don't include last punch
            time_diff = sorted_punches[j] - break_start
            diff_minutes = int(time_diff.total_seconds() / 60)
            
            if diff_minutes <= pair_threshold_minutes:
                # This punch is part of the same break group
                break_end = sorted_punches[j]
                group_size += 1
                j += 1
            else:
                # Gap > 30 min, end this break group
                break
        
        # Calculate break duration
        break_duration = break_end - break_start
        break_minutes = int(break_duration.total_seconds() / 60)
        
        # Add this break period
        if break_minutes >= 0:
            # This is a break period (grouped punches)
            punch_pairs.append((break_start, break_end, break_minutes))
            break_periods.append((break_start, break_end, break_minutes))
            total_break_minutes += break_minutes
            
            # Only mark as unpaired if it's a single punch (not part of a group)
            # Actually, these are all part of break periods, so don't mark as unpaired
            # Unpaired means: punch that has no pair and creates a 30 min penalty
            # But in our case, we're grouping them as breaks, so they're not "unpaired"
        
        # Move to next ungrouped punch
        i = j if j > i else i + 1
    
    # Unpaired punches are those that couldn't be grouped
    # In this logic, we don't have unpaired punches because we group everything
    # The "unpaired" concept doesn't apply here since we're calculating breaks differently
    
    # Calculate work minutes
    # Formula: Total Duration - Total Breaks
    work_minutes = total_duration_minutes - total_break_minutes
    
    # Ensure work_minutes is not negative
    if work_minutes < 0:
        work_minutes = 0
    
    # Convert to hours
    work_hours = Decimal(str(work_minutes / 60)).quantize(Decimal('0.01'))
    
    # Count paired punches (those with gaps ≤ 30 min)
    paired_count = len(punch_pairs) * 2 if punch_pairs else 0
    
    return {
        'work_hours': work_hours,
        'total_punches': total_punches,
        'paired_punches': paired_count,
        'unpaired_punches': len(unpaired_punch_times),
        'paired_time_minutes': sum(duration for _, _, duration in punch_pairs),
        'break_time_minutes': total_break_minutes,
        'unpaired_penalty_minutes': len(unpaired_punch_times) * 30,
        'first_punch': first_punch,
        'last_punch': last_punch,
        'punch_pairs': punch_pairs,
        'unpaired_punch_times': unpaired_punch_times,
        'break_periods': break_periods
    }


def calculate_daily_amount(work_hours, per_hour_rate):
    """
    Calculate daily amount
    
    Args:
        work_hours: Decimal work hours
        per_hour_rate: Decimal per hour rate
    
    Returns:
        Decimal: daily amount
    """
    return (work_hours * per_hour_rate).quantize(Decimal('0.01'))


def generate_attendance_from_logs(user_id, date, attendance_logs, per_hour_rate, break_time_minutes=60):
    """
    Generate attendance record from attendance logs for a specific date
    
    Args:
        user_id: Employee user_id
        date: Work date
        attendance_logs: QuerySet of AttendanceLog for this employee and date range
        per_hour_rate: Employee's per hour rate
        break_time_minutes: Break time in minutes
    
    Returns:
        dict: Attendance data or None if no valid attendance
    """
    # Get work day range
    start_datetime, end_datetime = get_work_day_range(date)
    
    # Make timezone aware if needed
    if timezone.is_naive(start_datetime):
        start_datetime = timezone.make_aware(start_datetime)
    if timezone.is_naive(end_datetime):
        end_datetime = timezone.make_aware(end_datetime)
    
    # Filter logs within work day range
    valid_logs = attendance_logs.filter(
        punch_time__gte=start_datetime,
        punch_time__lt=end_datetime
    ).order_by('punch_time')
    
    if not valid_logs.exists():
        return None
    
    # Extract punch times - ensure they're timezone aware
    punches = []
    for log in valid_logs:
        punch_time = log.punch_time
        # Ensure timezone aware
        if timezone.is_naive(punch_time):
            punch_time = timezone.make_aware(punch_time)
        punches.append(punch_time)
    
    # Calculate work hours
    calc_result = calculate_work_hours(punches, break_time_minutes)
    
    # Calculate daily amount
    daily_amount = calculate_daily_amount(calc_result['work_hours'], per_hour_rate)
    
    # Determine status - present if work_hours > 0
    status = 'present' if calc_result['work_hours'] > 0 else 'absent'
    
    # Return data even if work_hours is 0 (to show punch details)
    return {
        'user_id': user_id,
        'date': date,
        'status': status,
        'check_in_time': calc_result['first_punch'],
        'check_out_time': calc_result['last_punch'],
        'work_hours': calc_result['work_hours'],
        'total_punches': calc_result['total_punches'],
        'paired_punches': calc_result['paired_punches'],
        'unpaired_punches': calc_result['unpaired_punches'],
        'paired_time_minutes': calc_result['paired_time_minutes'],
        'break_time_minutes': calc_result['break_time_minutes'],
        'unpaired_penalty_minutes': calc_result['unpaired_penalty_minutes'],
        'daily_amount': daily_amount,
        'per_hour_rate': per_hour_rate,
        'punch_pairs': calc_result['punch_pairs'],
        'unpaired_punch_times': calc_result['unpaired_punch_times'],
        'break_periods': calc_result['break_periods'],
    }


"""
ZKTeco Device Utilities
Supports both ADMS (push-based) and PyZK (TCP pull-based) connections
"""

import logging
from datetime import datetime, timedelta, time
from decimal import Decimal
from django.utils import timezone
from django.db import IntegrityError

logger = logging.getLogger(__name__)


# =============================================================================
# PyZK Connection Manager - For TCP/IP based old devices
# =============================================================================

class ZKDeviceConnection:
    """
    PyZK wrapper for TCP connection to ZKTeco devices
    
    Usage:
        with ZKDeviceConnection(ip='192.168.1.201', port=4370) as conn:
            users = conn.get_users()
            attendance = conn.get_attendance()
    """
    
    def __init__(self, ip, port=4370, timeout=5, password=0):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.password = password
        self.conn = None
        self.zk = None
        
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
    
    def connect(self):
        """Establish TCP connection to device"""
        try:
            from zk import ZK
            self.zk = ZK(self.ip, port=self.port, timeout=self.timeout, password=self.password)
            self.conn = self.zk.connect()
            logger.info(f"[PyZK] Connected to {self.ip}:{self.port}")
            return True
        except ImportError:
            logger.error("[PyZK] pyzk library not installed. Run: pip install pyzk")
            raise ImportError("pyzk library not installed. Run: pip install pyzk")
        except Exception as e:
            logger.error(f"[PyZK] Connection failed to {self.ip}:{self.port} - {str(e)}")
            raise ConnectionError(f"Cannot connect to device at {self.ip}:{self.port}: {str(e)}")
    
    def disconnect(self):
        """Disconnect from device"""
        if self.conn:
            try:
                self.conn.disconnect()
                logger.info(f"[PyZK] Disconnected from {self.ip}")
            except Exception as e:
                logger.warning(f"[PyZK] Disconnect error: {str(e)}")
    
    def get_device_info(self):
        """Get device information"""
        if not self.conn:
            raise ConnectionError("Not connected to device")
        
        try:
            return {
                'serial_number': self.conn.get_serialnumber(),
                'device_name': self.conn.get_device_name(),
                'platform': self.conn.get_platform(),
                'firmware_version': self.conn.get_firmware_version(),
                'mac_address': self.conn.get_mac(),
            }
        except Exception as e:
            logger.error(f"[PyZK] Get device info error: {str(e)}")
            return {}
    
    def get_users(self):
        """Get all users from device"""
        if not self.conn:
            raise ConnectionError("Not connected to device")
        
        try:
            users = self.conn.get_users()
            logger.info(f"[PyZK] Found {len(users)} users on device")
            return users
        except Exception as e:
            logger.error(f"[PyZK] Get users error: {str(e)}")
            return []
    
    def get_attendance(self):
        """Get all attendance records from device"""
        if not self.conn:
            raise ConnectionError("Not connected to device")
        
        try:
            attendance = self.conn.get_attendance()
            logger.info(f"[PyZK] Found {len(attendance)} attendance records")
            return attendance
        except Exception as e:
            logger.error(f"[PyZK] Get attendance error: {str(e)}")
            return []
    
    def set_user(self, uid, name, privilege=0, password='', card_number='', user_id=''):
        """Add or update user on device"""
        if not self.conn:
            raise ConnectionError("Not connected to device")
        
        try:
            self.conn.set_user(
                uid=uid,
                name=name,
                privilege=privilege,
                password=password,
                card=card_number,
                user_id=user_id or str(uid)
            )
            logger.info(f"[PyZK] User {uid} set successfully")
            return True
        except Exception as e:
            logger.error(f"[PyZK] Set user error: {str(e)}")
            return False
    
    def delete_user(self, uid=0, user_id=''):
        """Delete user from device"""
        if not self.conn:
            raise ConnectionError("Not connected to device")
        
        try:
            self.conn.delete_user(uid=uid, user_id=user_id)
            logger.info(f"[PyZK] User {uid or user_id} deleted")
            return True
        except Exception as e:
            logger.error(f"[PyZK] Delete user error: {str(e)}")
            return False
    
    def clear_attendance(self):
        """Clear all attendance records from device"""
        if not self.conn:
            raise ConnectionError("Not connected to device")
        
        try:
            self.conn.clear_attendance()
            logger.info(f"[PyZK] Attendance cleared")
            return True
        except Exception as e:
            logger.error(f"[PyZK] Clear attendance error: {str(e)}")
            return False
    
    def restart(self):
        """Restart device"""
        if not self.conn:
            raise ConnectionError("Not connected to device")
        
        try:
            self.conn.restart()
            logger.info(f"[PyZK] Device restart command sent")
            return True
        except Exception as e:
            logger.error(f"[PyZK] Restart error: {str(e)}")
            return False
    
    def sync_time(self):
        """Sync device time with server"""
        if not self.conn:
            raise ConnectionError("Not connected to device")
        
        try:
            self.conn.set_time(datetime.now())
            logger.info(f"[PyZK] Time synced")
            return True
        except Exception as e:
            logger.error(f"[PyZK] Sync time error: {str(e)}")
            return False
    
    def get_time(self):
        """Get device time"""
        if not self.conn:
            raise ConnectionError("Not connected to device")
        
        try:
            return self.conn.get_time()
        except Exception as e:
            logger.error(f"[PyZK] Get time error: {str(e)}")
            return None


# =============================================================================
# Device Sync Functions - Simple Import Operations
# =============================================================================

def sync_users_from_device_tcp(device):
    """
    Import users from device via TCP (PyZK)
    Only imports NEW users - does NOT update existing users
    
    Args:
        device: ZKDevice model instance
    
    Returns:
        dict: Import result with counts
    """
    from zktest.models import DeviceUser, TCPSyncLog
    
    if not device.ip_address:
        return {'success': False, 'error': 'Device IP address not configured'}
    
    # Create sync log
    sync_log = TCPSyncLog.objects.create(
        device=device,
        sync_type='users',
        status='running',
        started_at=timezone.now()
    )
    
    result = {
        'success': False,
        'imported': 0,
        'skipped': 0,
        'failed': 0,
        'total': 0,
        'errors': []
    }
    
    try:
        with ZKDeviceConnection(
            ip=device.ip_address, 
            port=device.port,
            timeout=device.tcp_timeout,
            password=int(device.tcp_password) if device.tcp_password else 0
        ) as conn:
            users = conn.get_users()
            result['total'] = len(users)
            sync_log.records_found = len(users)
            
            for user in users:
                try:
                    user_id = str(user.user_id)
                    
                    # Check if user already exists - if yes, SKIP (don't update)
                    existing = DeviceUser.objects.filter(
                        device=device,
                        user_id=user_id
                    ).exists()
                    
                    if existing:
                        result['skipped'] += 1
                        continue
                    
                    # Only create NEW users
                    DeviceUser.objects.create(
                        device=device,
                        user_id=user_id,
                        name=user.name or '',
                        privilege=user.privilege or 0,
                        password=user.password or '',
                        card_number=str(user.card) if user.card else '',
                    )
                    result['imported'] += 1
                    
                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append(f"User {user.user_id}: {str(e)}")
            
            # Update device stats
            device.user_count = device.users.count()
            device.last_activity = timezone.now()
            device.is_online = True
            device.save(update_fields=['user_count', 'last_activity', 'is_online'])
            
            result['success'] = True
            sync_log.status = 'completed'
            sync_log.records_synced = result['imported']
            sync_log.records_failed = result['failed']
            
    except Exception as e:
        result['error'] = str(e)
        sync_log.status = 'failed'
        sync_log.error_message = str(e)
        logger.error(f"[PyZK] User import failed for {device}: {str(e)}")
    
    sync_log.completed_at = timezone.now()
    sync_log.save()
    
    return result


def sync_attendance_from_device_tcp(device, clear_after_sync=False):
    """
    Import attendance from device via TCP (PyZK)
    Skips duplicates automatically
    
    Args:
        device: ZKDevice model instance
        clear_after_sync: Clear attendance on device after sync
    
    Returns:
        dict: Import result with counts
    """
    from zktest.models import AttendanceLog, TCPSyncLog
    
    if not device.ip_address:
        return {'success': False, 'error': 'Device IP address not configured'}
    
    sync_log = TCPSyncLog.objects.create(
        device=device,
        sync_type='attendance',
        status='running',
        started_at=timezone.now()
    )
    
    result = {
        'success': False,
        'imported': 0,
        'skipped': 0,
        'failed': 0,
        'total': 0,
        'errors': []
    }
    
    try:
        with ZKDeviceConnection(
            ip=device.ip_address, 
            port=device.port,
            timeout=device.tcp_timeout,
            password=int(device.tcp_password) if device.tcp_password else 0
        ) as conn:
            attendance = conn.get_attendance()
            result['total'] = len(attendance)
            sync_log.records_found = len(attendance)
            
            for record in attendance:
                try:
                    # Try to create - if exists, will be skipped
                    _, created = AttendanceLog.objects.get_or_create(
                        device=device,
                        user_id=str(record.user_id),
                        punch_time=record.timestamp,
                        defaults={
                            'punch_type': record.punch if hasattr(record, 'punch') else 0,
                            'verify_type': record.status if hasattr(record, 'status') else 1,
                            'source': 'tcp',
                        }
                    )
                    if created:
                        result['imported'] += 1
                    else:
                        result['skipped'] += 1
                except IntegrityError:
                    result['skipped'] += 1
                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append(str(e))
            
            # Clear attendance if requested
            if clear_after_sync and result['imported'] > 0:
                conn.clear_attendance()
                logger.info(f"[PyZK] Cleared attendance on device after sync")
            
            # Update device stats
            device.transaction_count = device.attendance_logs.count()
            device.last_activity = timezone.now()
            device.is_online = True
            device.save(update_fields=['transaction_count', 'last_activity', 'is_online'])
            
            result['success'] = True
            sync_log.status = 'completed'
            sync_log.records_synced = result['imported']
            sync_log.records_failed = result['failed']
            
    except Exception as e:
        result['error'] = str(e)
        sync_log.status = 'failed'
        sync_log.error_message = str(e)
        logger.error(f"[PyZK] Attendance import failed for {device}: {str(e)}")
    
    sync_log.completed_at = timezone.now()
    sync_log.save()
    
    return result


def sync_all_from_device_tcp(device, clear_attendance=False):
    """
    Import all data (users + attendance) from device via TCP
    """
    result = {
        'users': sync_users_from_device_tcp(device),
        'attendance': sync_attendance_from_device_tcp(device, clear_attendance),
    }
    
    result['success'] = result['users']['success'] and result['attendance']['success']
    return result


def execute_tcp_command(device, command_type, **kwargs):
    """
    Execute a command on device via TCP (PyZK)
    """
    if not device.ip_address:
        return {'success': False, 'error': 'Device IP address not configured'}
    
    result = {'success': False, 'message': ''}
    
    try:
        with ZKDeviceConnection(
            ip=device.ip_address, 
            port=device.port,
            timeout=device.tcp_timeout,
            password=int(device.tcp_password) if device.tcp_password else 0
        ) as conn:
            
            if command_type == 'REBOOT':
                conn.restart()
                result['message'] = 'Device restart command sent'
                result['success'] = True
                
            elif command_type == 'UPDATE_TIME':
                conn.sync_time()
                result['message'] = 'Time synchronized'
                result['success'] = True
                
            elif command_type == 'CLEAR_LOG':
                conn.clear_attendance()
                result['message'] = 'Attendance cleared'
                result['success'] = True
                
            elif command_type == 'INFO':
                info = conn.get_device_info()
                result['data'] = info
                result['message'] = 'Device info retrieved'
                result['success'] = True
                
            else:
                result['error'] = f'Unknown command type: {command_type}'
        
        # Update device activity on success
        if result['success']:
            device.last_activity = timezone.now()
            device.is_online = True
            device.save(update_fields=['last_activity', 'is_online'])
            
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"[PyZK] Command {command_type} failed: {str(e)}")
        
        # Mark device offline on connection error
        device.is_online = False
        device.save(update_fields=['is_online'])
    
    return result


# =============================================================================
# Attendance Calculation Utilities
# =============================================================================

def get_work_day_range(date):
    """Get work day range: 6:00 AM to next day 4:00 AM"""
    start_datetime = datetime.combine(date, time(6, 0, 0))
    next_day = date + timedelta(days=1)
    end_datetime = datetime.combine(next_day, time(4, 0, 0))
    return start_datetime, end_datetime


def calculate_work_hours(punches, break_time_minutes=60, pair_threshold_minutes=30):
    """Calculate work hours from punch list"""
    if not punches or len(punches) == 0:
        return {
            'work_hours': Decimal('0.00'),
            'total_punches': 0,
            'first_punch': None,
            'last_punch': None,
            'break_time_minutes': 0,
        }
    
    sorted_punches = sorted(punches)
    total_punches = len(sorted_punches)
    first_punch = sorted_punches[0]
    last_punch = sorted_punches[-1]
    
    total_duration = last_punch - first_punch
    total_duration_minutes = int(total_duration.total_seconds() / 60)
    
    total_break_minutes = 0
    i = 1
    while i < len(sorted_punches) - 1:
        break_start = sorted_punches[i]
        break_end = sorted_punches[i]
        
        j = i + 1
        while j < len(sorted_punches) - 1:
            time_diff = sorted_punches[j] - break_start
            diff_minutes = int(time_diff.total_seconds() / 60)
            
            if diff_minutes <= pair_threshold_minutes:
                break_end = sorted_punches[j]
                j += 1
            else:
                break
        
        break_duration = break_end - break_start
        break_minutes = int(break_duration.total_seconds() / 60)
        total_break_minutes += break_minutes
        
        i = j if j > i else i + 1
    
    work_minutes = max(0, total_duration_minutes - total_break_minutes)
    work_hours = Decimal(str(work_minutes / 60)).quantize(Decimal('0.01'))
    
    return {
        'work_hours': work_hours,
        'total_punches': total_punches,
        'first_punch': first_punch,
        'last_punch': last_punch,
        'break_time_minutes': total_break_minutes,
    }


# =============================================================================
# Employee-Device Sync Functions
# =============================================================================

def sync_device_users_to_employees(auto_create=True):
    """
    Sync device users to employees
    
    Args:
        auto_create: If True, create employee records for device users without employees
    
    Returns:
        dict: Statistics about sync operation
    """
    from zktest.models import DeviceUser, Employee
    from django.db import transaction
    
    stats = {
        'total_device_users': 0,
        'existing_employees': 0,
        'created_employees': 0,
        'updated_employees': 0,
        'errors': []
    }
    
    device_users = DeviceUser.objects.all()
    stats['total_device_users'] = device_users.count()
    
    for du in device_users:
        try:
            employee = du.get_employee()
            
            if employee:
                stats['existing_employees'] += 1
            elif auto_create:
                # Create new employee
                new_employee = du.create_employee_if_not_exists()
                if new_employee:
                    stats['created_employees'] += 1
        except Exception as e:
            stats['errors'].append({
                'user_id': du.user_id,
                'device': str(du.device),
                'error': str(e)
            })
    
    return stats


def sync_employees_to_device(device, employee_queryset=None):
    """
    Sync employees to a specific device
    
    Args:
        device: ZKDevice instance
        employee_queryset: QuerySet of employees to sync (default: all active employees)
    
    Returns:
        dict: Statistics about sync operation
    """
    from zktest.models import Employee, DeviceCommand
    
    stats = {
        'total_employees': 0,
        'already_enrolled': 0,
        'commands_created': 0,
        'errors': []
    }
    
    if employee_queryset is None:
        employee_queryset = Employee.objects.filter(is_active=True)
    
    stats['total_employees'] = employee_queryset.count()
    
    for emp in employee_queryset:
        try:
            # Check if already enrolled
            if emp.is_enrolled_in_device(device):
                stats['already_enrolled'] += 1
                continue
            
            # Create command to enroll user
            DeviceCommand.objects.create(
                device=device,
                command_type='SET_USER',
                command_content=f"PIN={emp.user_id}\tName={emp.get_full_name()}\tPri=0"
            )
            stats['commands_created'] += 1
            
        except Exception as e:
            stats['errors'].append({
                'employee_id': emp.employee_id,
                'user_id': emp.user_id,
                'error': str(e)
            })
    
    return stats


def process_attendance_logs(date=None, user_id=None):
    """
    Process attendance logs into attendance records
    
    Args:
        date: Specific date to process (default: all unsynced)
        user_id: Specific user_id to process (default: all)
    
    Returns:
        dict: Statistics about processing
    """
    from zktest.models import AttendanceLog, Attendance, Employee
    
    stats = {
        'total_logs': 0,
        'processed': 0,
        'skipped_no_employee': 0,
        'errors': []
    }
    
    # Get unsynced logs
    logs = AttendanceLog.objects.filter(is_synced=False)
    
    if date:
        logs = logs.filter(punch_time__date=date)
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    stats['total_logs'] = logs.count()
    
    for log in logs:
        try:
            # Check if employee exists
            try:
                employee = Employee.objects.get(user_id=log.user_id)
            except Employee.DoesNotExist:
                stats['skipped_no_employee'] += 1
                continue
            
            # Get or create attendance record for the date
            date = log.punch_time.date()
            attendance, created = Attendance.objects.get_or_create(
                user_id=employee,
                date=date,
                defaults={
                    'shift_code': employee.shift_code or '',
                    'status': 'present',
                }
            )
            
            # Update check-in/check-out based on punch type
            if log.punch_type == 0:  # Check In
                if not attendance.check_in_time or log.punch_time < attendance.check_in_time:
                    attendance.check_in_time = log.punch_time
            elif log.punch_type == 1:  # Check Out
                if not attendance.check_out_time or log.punch_time > attendance.check_out_time:
                    attendance.check_out_time = log.punch_time
            
            # Calculate work hours if both times exist
            if attendance.check_in_time and attendance.check_out_time:
                duration = attendance.check_out_time - attendance.check_in_time
                attendance.work_hours = duration.total_seconds() / 3600
            
            attendance.processed_from_logs = True
            attendance.last_processed_at = timezone.now()
            attendance.save()
            
            # Mark log as synced
            log.is_synced = True
            log.synced_at = timezone.now()
            log.save()
            
            stats['processed'] += 1
            
        except Exception as e:
            stats['errors'].append({
                'log_id': log.id,
                'user_id': log.user_id,
                'punch_time': str(log.punch_time),
                'error': str(e)
            })
    
    return stats


def get_orphan_device_users():
    """
    Get device users that don't have corresponding employee records
    
    Returns:
        QuerySet: DeviceUser objects without employees
    """
    from zktest.models import DeviceUser, Employee
    
    all_device_users = DeviceUser.objects.all()
    employee_user_ids = set(Employee.objects.values_list('user_id', flat=True))
    
    orphan_users = []
    for du in all_device_users:
        if du.user_id not in employee_user_ids:
            orphan_users.append(du.id)
    
    return DeviceUser.objects.filter(id__in=orphan_users)


def get_unenrolled_employees(device):
    """
    Get employees that are not enrolled in a specific device
    
    Args:
        device: ZKDevice instance
    
    Returns:
        QuerySet: Employee objects not enrolled in device
    """
    from zktest.models import DeviceUser, Employee
    
    enrolled_user_ids = DeviceUser.objects.filter(
        device=device
    ).values_list('user_id', flat=True)
    
    return Employee.objects.filter(
        is_active=True
    ).exclude(user_id__in=enrolled_user_ids)


def bulk_create_employees_from_device_users():
    """
    Bulk create employee records for all orphan device users
    
    Returns:
        int: Number of employees created
    """
    from zktest.models import Employee
    from django.db import transaction
    
    orphan_users = get_orphan_device_users()
    employees_to_create = []
    
    for du in orphan_users:
        names = du.name.split(' ', 1) if du.name else ['', '']
        employees_to_create.append(
            Employee(
                user_id=du.user_id,
                employee_id=du.user_id,
                first_name=names[0],
                last_name=names[1] if len(names) > 1 else '',
                is_active=du.is_active
            )
        )
    
    if employees_to_create:
        with transaction.atomic():
            Employee.objects.bulk_create(employees_to_create, ignore_conflicts=True)
    
    return len(employees_to_create)


def sync_report():
    """
    Generate a comprehensive sync report
    
    Returns:
        dict: Report with various statistics
    """
    from zktest.models import Employee, DeviceUser, AttendanceLog
    
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(is_active=True).count()
    total_device_users = DeviceUser.objects.count()
    orphan_device_users = get_orphan_device_users().count()
    
    # Count employees enrolled in at least one device
    enrolled_employees = Employee.objects.filter(
        user_id__in=DeviceUser.objects.values_list('user_id', flat=True)
    ).count()
    
    return {
        'employees': {
            'total': total_employees,
            'active': active_employees,
            'enrolled_in_devices': enrolled_employees,
            'not_enrolled': active_employees - enrolled_employees,
        },
        'device_users': {
            'total': total_device_users,
            'with_employee': total_device_users - orphan_device_users,
            'without_employee': orphan_device_users,
        },
        'attendance_logs': {
            'total': AttendanceLog.objects.count(),
            'unsynced': AttendanceLog.objects.filter(is_synced=False).count(),
            'synced': AttendanceLog.objects.filter(is_synced=True).count(),
        }
    }
