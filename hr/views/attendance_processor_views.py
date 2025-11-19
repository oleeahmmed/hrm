# ==================== hr/views/attendance_processor_views.py ====================
"""
Attendance Processor Views - Generate attendance based on configuration
"""

from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from hr.models import (
    AttendanceProcessorConfiguration, Employee, Attendance, AttendanceLog,
    Shift, Holiday, LeaveApplication, RosterDay, Overtime
)

logger = logging.getLogger(__name__)


def generate_attendance_for_config(config_id, days=0):
    """
    Generate attendance for a configuration
    :param config_id: AttendanceProcessorConfiguration ID
    :param days: Number of days (0=today, 7=last 7 days, etc., None=all available logs)
    Returns: (success, message, data)
    """
    try:
        config = AttendanceProcessorConfiguration.objects.get(id=config_id)
        company = config.company
        
        # Determine date range
        end_date = timezone.now().date()
        if days == 0:
            start_date = end_date
        elif days is None:
            # Get earliest attendance log date
            earliest_log = AttendanceLog.objects.filter(
                company=company
            ).order_by('timestamp').first()
            
            if earliest_log:
                start_date = earliest_log.timestamp.date()
            else:
                start_date = end_date - timedelta(days=30)  # Default to 30 days
        else:
            start_date = end_date - timedelta(days=days-1)
        
        # Get configuration settings
        config_dict = config.get_config_dict()
        weekend_days = config.weekend_days
        
        # Get active employees
        employees = Employee.objects.filter(
            company=company,
            is_active=True
        ).select_related('default_shift', 'department')
        
        if not employees.exists():
            return False, "No active employees found", None
        
        # Load holidays
        holidays = set(
            Holiday.objects.filter(
                company=company,
                date__range=[start_date, end_date]
            ).values_list('date', flat=True)
        )
        
        # Load leaves
        leaves = {}
        leave_apps = LeaveApplication.objects.filter(
            employee__company=company,
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        ).select_related('employee')
        
        for leave in leave_apps:
            if leave.employee_id not in leaves:
                leaves[leave.employee_id] = set()
            
            current = max(leave.start_date, start_date)
            end = min(leave.end_date, end_date)
            while current <= end:
                leaves[leave.employee_id].add(current)
                current += timedelta(days=1)
        
        # Generate attendance
        generated_count = 0
        updated_count = 0
        error_count = 0
        
        current_date = start_date
        
        with transaction.atomic():
            while current_date <= end_date:
                is_weekend = current_date.weekday() in weekend_days
                is_holiday = current_date in holidays
                
                for employee in employees:
                    try:
                        # Get logs for the day - ordered by timestamp ascending (earliest first)
                        logs = AttendanceLog.objects.filter(
                            employee=employee,
                            timestamp__date=current_date
                        ).order_by('timestamp')
                        
                        # First log of the day = Check In
                        # Last log of the day = Check Out
                        if logs.exists():
                            check_in = logs.first().timestamp  # Earliest timestamp = Check In
                            if logs.count() > 1:
                                check_out = logs.last().timestamp  # Latest timestamp = Check Out
                            else:
                                check_out = None  # Only one log, no check out
                        else:
                            check_in = None
                            check_out = None
                        
                        # Determine shift
                        shift = employee.default_shift
                        
                        # Check if employee has roster for this day
                        roster_day = RosterDay.objects.filter(
                            employee=employee,
                            date=current_date
                        ).first()
                        
                        if roster_day:
                            shift = roster_day.shift
                            if roster_day.is_off:
                                is_weekend = True
                        
                        # Check leave
                        has_leave = current_date in leaves.get(employee.id, set())
                        
                        # Calculate working hours
                        working_hours = 0.0
                        if check_in and check_out:
                            # Ensure both are timezone-aware
                            if timezone.is_naive(check_in):
                                check_in = timezone.make_aware(check_in)
                            if timezone.is_naive(check_out):
                                check_out = timezone.make_aware(check_out)
                            
                            total_seconds = (check_out - check_in).total_seconds()
                            total_hours = total_seconds / 3600
                            
                            # Deduct break
                            if config_dict.get('use_shift_break_time') and shift:
                                break_minutes = shift.break_time
                            else:
                                break_minutes = config_dict.get('default_break_minutes', 60)
                            
                            working_hours = max(0, total_hours - (break_minutes / 60))
                        
                        # Determine status
                        if is_weekend:
                            status = 'weekend'
                        elif is_holiday:
                            status = 'holiday'
                        elif has_leave:
                            status = 'leave'
                        elif not check_in and not check_out:
                            status = 'absent'
                        elif config_dict.get('require_both_in_and_out') and (not check_in or not check_out):
                            status = 'absent'
                        elif config_dict.get('enable_minimum_working_hours_rule'):
                            min_hours = config_dict.get('minimum_working_hours_for_present', 4.0)
                            if working_hours < min_hours:
                                status = 'absent'
                            else:
                                status = 'present'
                        else:
                            status = 'present' if (check_in or check_out) else 'absent'
                        
                        # Calculate overtime
                        overtime_hours = 0.0
                        if status == 'present' and working_hours > 0:
                            expected_hours = employee.expected_working_hours
                            if working_hours > expected_hours:
                                overtime_hours = working_hours - expected_hours
                                
                                # Check minimum overtime
                                min_ot = config_dict.get('minimum_overtime_minutes', 60) / 60
                                if overtime_hours < min_ot:
                                    overtime_hours = 0
                        
                        # Calculate late minutes
                        late_minutes = 0
                        if check_in and shift:
                            # Ensure check_in is timezone-aware
                            if timezone.is_naive(check_in):
                                check_in = timezone.make_aware(check_in)
                            
                            grace_minutes = config_dict.get('grace_minutes', 15)
                            shift_start = timezone.make_aware(
                                datetime.combine(current_date, shift.start_time)
                            )
                            grace_end = shift_start + timedelta(minutes=grace_minutes)
                            
                            if check_in > grace_end:
                                late_minutes = int((check_in - grace_end).total_seconds() / 60)
                        
                        # Calculate early out minutes
                        early_out_minutes = 0
                        if check_out and shift:
                            # Ensure check_out is timezone-aware
                            if timezone.is_naive(check_out):
                                check_out = timezone.make_aware(check_out)
                            
                            threshold = config_dict.get('early_out_threshold_minutes', 30)
                            shift_end = timezone.make_aware(
                                datetime.combine(current_date, shift.end_time)
                            )
                            early_threshold = shift_end - timedelta(minutes=threshold)
                            
                            if check_out < early_threshold:
                                early_out_minutes = int((early_threshold - check_out).total_seconds() / 60)
                        
                        # Create or update attendance
                        attendance, created = Attendance.objects.update_or_create(
                            company=company,
                            employee=employee,
                            date=current_date,
                            defaults={
                                'shift': shift,
                                'check_in_time': check_in,
                                'check_out_time': check_out,
                                'status': status,
                                'work_hours': Decimal(str(round(working_hours, 2))),
                                'overtime_hours': Decimal(str(round(overtime_hours, 2))),
                                'late_minutes': late_minutes,
                                'early_out_minutes': early_out_minutes,
                                'remarks': f'Generated using config: {config.name}'
                            }
                        )
                        
                        if created:
                            generated_count += 1
                        else:
                            updated_count += 1
                    
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error generating attendance for {employee.employee_id}: {str(e)}")
                
                current_date += timedelta(days=1)
        
        data = {
            'generated': generated_count,
            'updated': updated_count,
            'errors': error_count,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'config_name': config.name
        }
        
        message = f"Generated {generated_count}, Updated {updated_count}"
        if error_count > 0:
            message += f", Errors {error_count}"
        
        return True, message, data
    
    except AttendanceProcessorConfiguration.DoesNotExist:
        return False, "Configuration not found", None
    except Exception as e:
        logger.error(f"Generate attendance error: {str(e)}")
        return False, f"Error: {str(e)}", None


# ==================== JSON Response Helpers ====================

def generate_attendance_today_json(request, config_id):
    """Generate attendance for today"""
    success, message, data = generate_attendance_for_config(config_id, days=0)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })


def generate_attendance_7days_json(request, config_id):
    """Generate attendance for last 7 days"""
    success, message, data = generate_attendance_for_config(config_id, days=7)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })


def generate_attendance_15days_json(request, config_id):
    """Generate attendance for last 15 days"""
    success, message, data = generate_attendance_for_config(config_id, days=15)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })


def generate_attendance_30days_json(request, config_id):
    """Generate attendance for last 30 days"""
    success, message, data = generate_attendance_for_config(config_id, days=30)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })


def generate_attendance_all_json(request, config_id):
    """Generate attendance for all available logs"""
    success, message, data = generate_attendance_for_config(config_id, days=None)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })



# ==================== OVERTIME GENERATION ====================

def generate_overtime_for_config(config_id, days=0):
    """
    Generate overtime records from attendance data
    :param config_id: AttendanceProcessorConfiguration ID
    :param days: Number of days (0=today, 7=last 7 days, etc., None=all available attendance)
    Returns: (success, message, data)
    """
    try:
        config = AttendanceProcessorConfiguration.objects.get(id=config_id)
        company = config.company
        
        # Determine date range
        end_date = timezone.now().date()
        if days == 0:
            start_date = end_date
        elif days is None:
            # Get earliest attendance date
            earliest_attendance = Attendance.objects.filter(
                company=company
            ).order_by('date').first()
            
            if earliest_attendance:
                start_date = earliest_attendance.date
            else:
                start_date = end_date - timedelta(days=30)  # Default to 30 days
        else:
            start_date = end_date - timedelta(days=days-1)
        
        # Get configuration settings
        config_dict = config.get_config_dict()
        weekend_days = config.weekend_days
        
        # Load holidays
        holidays = set(
            Holiday.objects.filter(
                company=company,
                date__range=[start_date, end_date]
            ).values_list('date', flat=True)
        )
        
        # Get attendance records with overtime
        attendances = Attendance.objects.filter(
            company=company,
            date__range=[start_date, end_date],
            overtime_hours__gt=0
        ).select_related('employee', 'shift')
        
        if not attendances.exists():
            return False, "No attendance records with overtime found", None
        
        generated_count = 0
        updated_count = 0
        error_count = 0
        
        with transaction.atomic():
            for attendance in attendances:
                try:
                    employee = attendance.employee
                    
                    # Determine overtime type
                    is_weekend = attendance.date.weekday() in weekend_days
                    is_holiday = attendance.date in holidays
                    
                    if is_holiday:
                        overtime_type = 'holiday'
                        rate_multiplier = Decimal('2.0')  # Double time for holidays
                    elif is_weekend:
                        overtime_type = 'weekend'
                        rate_multiplier = Decimal('1.75')  # Time and 3/4 for weekends
                    elif attendance.shift and attendance.shift.is_night_shift:
                        overtime_type = 'night'
                        rate_multiplier = Decimal('1.5')  # Time and a half for night
                    else:
                        overtime_type = 'regular'
                        rate_multiplier = Decimal('1.5')  # Time and a half for regular
                    
                    # Calculate hourly rate
                    if employee.per_hour_rate > 0:
                        hourly_rate = employee.per_hour_rate
                    elif employee.base_salary > 0 and employee.expected_working_hours > 0:
                        # Calculate from monthly salary (assuming 26 working days)
                        daily_rate = employee.base_salary / 26
                        hourly_rate = daily_rate / Decimal(str(employee.expected_working_hours))
                    else:
                        hourly_rate = Decimal('0.00')
                    
                    # Use employee-specific overtime rate if available
                    if employee.overtime_rate > 0:
                        hourly_rate = employee.overtime_rate
                    
                    # Create or update overtime record
                    overtime, created = Overtime.objects.update_or_create(
                        company=company,
                        employee=employee,
                        date=attendance.date,
                        defaults={
                            'attendance': attendance,
                            'shift': attendance.shift,
                            'start_time': attendance.check_out_time if attendance.check_out_time else None,
                            'end_time': None,  # Can be set manually later
                            'overtime_hours': attendance.overtime_hours,
                            'overtime_type': overtime_type,
                            'hourly_rate': hourly_rate,
                            'overtime_rate_multiplier': rate_multiplier,
                            'status': 'pending',
                            'remarks': f'Generated from attendance using config: {config.name}'
                        }
                    )
                    
                    if created:
                        generated_count += 1
                    else:
                        updated_count += 1
                
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error generating overtime for {employee.employee_id}: {str(e)}")
        
        data = {
            'generated': generated_count,
            'updated': updated_count,
            'errors': error_count,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'config_name': config.name
        }
        
        message = f"Generated {generated_count}, Updated {updated_count}"
        if error_count > 0:
            message += f", Errors {error_count}"
        
        return True, message, data
    
    except AttendanceProcessorConfiguration.DoesNotExist:
        return False, "Configuration not found", None
    except Exception as e:
        logger.error(f"Generate overtime error: {str(e)}")
        return False, f"Error: {str(e)}", None


# ==================== OVERTIME JSON Response Helpers ====================

def generate_overtime_today_json(request, config_id):
    """Generate overtime for today"""
    success, message, data = generate_overtime_for_config(config_id, days=0)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })


def generate_overtime_7days_json(request, config_id):
    """Generate overtime for last 7 days"""
    success, message, data = generate_overtime_for_config(config_id, days=7)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })


def generate_overtime_15days_json(request, config_id):
    """Generate overtime for last 15 days"""
    success, message, data = generate_overtime_for_config(config_id, days=15)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })


def generate_overtime_30days_json(request, config_id):
    """Generate overtime for last 30 days"""
    success, message, data = generate_overtime_for_config(config_id, days=30)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })


def generate_overtime_all_json(request, config_id):
    """Generate overtime for all available attendance"""
    success, message, data = generate_overtime_for_config(config_id, days=None)
    return JsonResponse({
        'success': success,
        'message': message,
        'data': data
    })
