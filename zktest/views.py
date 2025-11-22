# ==================== zktest/views.py ====================
"""
ZKTest Views - Attendance Log Report Views
"""

from django.contrib import admin
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, date

from zktest.models import AttendanceLog, Employee, Department, Shift, EmployeeSalary
from zktest.utils import generate_attendance_from_logs
from datetime import timedelta
from decimal import Decimal

class AttendanceLogReportView(View):
    """Attendance Log Report View - Raw punch data from ZKTeco devices"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        from zktest.forms import AttendanceLogReportForm
        
        form = AttendanceLogReportForm(data=request.GET or None)
        
        # Default queryset - user_id is a CharField, not a ForeignKey
        logs = AttendanceLog.objects.all().order_by('-punch_time')
        
        # Apply filters if form is valid
        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            employee = form.cleaned_data.get('employee')
            device_sn = form.cleaned_data.get('device_sn')
            is_processed = form.cleaned_data.get('is_processed')
            
            if from_date:
                logs = logs.filter(punch_time__date__gte=from_date)
            if to_date:
                logs = logs.filter(punch_time__date__lte=to_date)
            if employee:
                # Filter by employee's user_id (CharField)
                logs = logs.filter(user_id=employee.user_id)
            if device_sn:
                logs = logs.filter(device_sn__icontains=device_sn)
            if is_processed != '':
                logs = logs.filter(is_processed=(is_processed == 'true'))
        
        # Calculate statistics
        total_logs = logs.count()
        processed_logs = logs.filter(is_processed=True).count()
        unprocessed_logs = logs.filter(is_processed=False).count()
        
        # Get unique employees count
        unique_employees = logs.values('user_id').distinct().count()
        
        # Get unique devices count
        unique_devices = logs.values('device_sn').distinct().count()
        
        # Get logs by status
        status_breakdown = {}
        for status_val in logs.values_list('status', flat=True).distinct():
            if status_val:
                status_breakdown[status_val] = logs.filter(status=status_val).count()
        
        # Get logs by verify type
        verify_type_breakdown = {}
        for verify_val in logs.values_list('verify_type', flat=True).distinct():
            if verify_val:
                verify_type_breakdown[verify_val] = logs.filter(verify_type=verify_val).count()
        
        # Processing rate
        processing_rate = 0
        if total_logs > 0:
            processing_rate = round((processed_logs / total_logs) * 100, 2)
        
        # Get employee lookup dictionary for display
        log_list = logs[:200]  # Limit to 200 records
        user_ids = [log.user_id for log in log_list if log.user_id]
        employees_dict = {}
        if user_ids:
            employees = Employee.objects.filter(user_id__in=user_ids)
            employees_dict = {emp.user_id: emp for emp in employees}
        
        # Attach employee objects to logs for template
        for log in log_list:
            log.employee_obj = employees_dict.get(log.user_id)
        
        context = {
            **admin.site.each_context(request),
            'title': 'Attendance Log Report',
            'subtitle': 'Raw punch data from ZKTeco devices',
            'form': form,
            'logs': log_list,
            'total_logs': total_logs,
            'processed_logs': processed_logs,
            'unprocessed_logs': unprocessed_logs,
            'unique_employees': unique_employees,
            'unique_devices': unique_devices,
            'status_breakdown': status_breakdown,
            'verify_type_breakdown': verify_type_breakdown,
            'processing_rate': processing_rate,
        }
        
        return render(request, 'admin/zktest/attendance_log_report.html', context)



class DailyAttendanceReportView(View):
    """Daily Attendance Report - Generated from AttendanceLog with specific rules"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        from zktest.forms import DailyAttendanceReportForm
        from collections import defaultdict
        
        form = DailyAttendanceReportForm(data=request.GET or None)
        
        attendance_records = []
        total_present = 0
        total_absent = 0
        total_work_hours = Decimal('0.00')
        total_amount = Decimal('0.00')
        
        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            employee = form.cleaned_data.get('employee')
            break_time = form.cleaned_data.get('break_time_minutes', 60)
            
            if from_date and to_date:
                # Get employees to process
                employees = Employee.objects.filter(is_active=True)
                if employee:
                    employees = employees.filter(user_id=employee.user_id)
                
                # Get all attendance logs in the date range
                # We need to extend the range to cover cross-day punches
                extended_from = from_date - timedelta(days=1)
                extended_to = to_date + timedelta(days=1)
                
                all_logs = AttendanceLog.objects.filter(
                    punch_time__date__gte=extended_from,
                    punch_time__date__lte=extended_to
                ).order_by('user_id', 'punch_time')
                
                # Group logs by user_id
                logs_by_user = defaultdict(list)
                for log in all_logs:
                    logs_by_user[log.user_id].append(log)
                
                # Process each employee for each date
                for emp in employees:
                    # Get employee salary info
                    try:
                        salary_info = EmployeeSalary.objects.get(user_id=emp)
                        per_hour_rate = salary_info.per_hour_rate
                    except EmployeeSalary.DoesNotExist:
                        per_hour_rate = Decimal('0.00')
                    
                    # Get logs for this employee (force fresh query)
                    emp_logs = AttendanceLog.objects.filter(user_id=emp.user_id).order_by('punch_time')
                    
                    # Process each date in range
                    current_date = from_date
                    while current_date <= to_date:
                        # Get work day range for this date
                        from zktest.utils import get_work_day_range
                        start_datetime, end_datetime = get_work_day_range(current_date)
                        
                        # Make timezone aware if needed
                        if timezone.is_naive(start_datetime):
                            start_datetime = timezone.make_aware(start_datetime)
                        if timezone.is_naive(end_datetime):
                            end_datetime = timezone.make_aware(end_datetime)
                        
                        # Get punch logs for this work day
                        day_logs = emp_logs.filter(
                            punch_time__gte=start_datetime,
                            punch_time__lt=end_datetime
                        ).order_by('punch_time')
                        
                        # Generate attendance for this date
                        attendance_data = generate_attendance_from_logs(
                            user_id=emp.user_id,
                            date=current_date,
                            attendance_logs=emp_logs,
                            per_hour_rate=per_hour_rate,
                            break_time_minutes=break_time
                        )
                        
                        # Always add record, even if absent
                        if attendance_data:
                            # Add employee object and punch logs for display
                            attendance_data['employee'] = emp
                            attendance_data['punch_logs'] = list(day_logs)
                            attendance_records.append(attendance_data)
                            
                            # Update statistics
                            if attendance_data['status'] == 'present':
                                total_present += 1
                                total_work_hours += attendance_data['work_hours']
                                total_amount += attendance_data['daily_amount']
                            else:
                                total_absent += 1
                        elif day_logs.exists():
                            # Has punches but work_hours = 0 (all penalties/breaks)
                            # Still show the record with punch details
                            total_absent += 1
                            attendance_records.append({
                                'employee': emp,
                                'user_id': emp.user_id,
                                'date': current_date,
                                'status': 'absent',
                                'check_in_time': day_logs.first().punch_time if day_logs.exists() else None,
                                'check_out_time': day_logs.last().punch_time if day_logs.exists() else None,
                                'work_hours': Decimal('0.00'),
                                'total_punches': day_logs.count(),
                                'paired_punches': 0,
                                'unpaired_punches': day_logs.count(),
                                'paired_time_minutes': 0,
                                'break_time_minutes': 0,
                                'unpaired_penalty_minutes': day_logs.count() * 30,
                                'daily_amount': Decimal('0.00'),
                                'per_hour_rate': per_hour_rate,
                                'punch_logs': list(day_logs),
                                'punch_pairs': [],
                                'unpaired_punch_times': [log.punch_time for log in day_logs],
                                'break_periods': [],
                            })
                        else:
                            # No punches at all - truly absent
                            total_absent += 1
                            attendance_records.append({
                                'employee': emp,
                                'user_id': emp.user_id,
                                'date': current_date,
                                'status': 'absent',
                                'check_in_time': None,
                                'check_out_time': None,
                                'work_hours': Decimal('0.00'),
                                'total_punches': 0,
                                'paired_punches': 0,
                                'unpaired_punches': 0,
                                'paired_time_minutes': 0,
                                'break_time_minutes': 0,
                                'unpaired_penalty_minutes': 0,
                                'daily_amount': Decimal('0.00'),
                                'per_hour_rate': per_hour_rate,
                                'punch_logs': [],
                                'punch_pairs': [],
                                'unpaired_punch_times': [],
                                'break_periods': [],
                            })
                        
                        current_date += timedelta(days=1)
        
        # Sort by date and employee
        attendance_records.sort(key=lambda x: (x['date'], x['employee'].employee_id))
        
        context = {
            **admin.site.each_context(request),
            'title': 'Daily Attendance Report',
            'subtitle': 'Generated from AttendanceLog with work day rules (6 AM - 4 AM)',
            'form': form,
            'attendance_records': attendance_records[:500],  # Limit to 500 records
            'total_records': len(attendance_records),
            'total_present': total_present,
            'total_absent': total_absent,
            'total_work_hours': round(total_work_hours, 2),
            'total_amount': round(total_amount, 2),
        }
        
        return render(request, 'admin/zktest/daily_attendance_report.html', context)



# ==================== MOBILE VIEWS ====================

class MobileLoginView(View):
    """Mobile Login View"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('zktest:mobile-dashboard')
        return render(request, 'zktest/mobile/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('zktest:mobile-dashboard')
        else:
            return render(request, 'zktest/mobile/login.html', {
                'error': 'Invalid username or password'
            })


class MobileLogoutView(View):
    """Mobile Logout View"""
    
    def get(self, request):
        logout(request)
        return redirect('zktest:mobile-login')


class MobileDashboardView(View):
    """Mobile Dashboard View - Shows attendance logs by date"""
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Get date from query parameter or use today
        selected_date_str = request.GET.get('date')
        if selected_date_str:
            try:
                from datetime import datetime
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = date.today()
        else:
            selected_date = date.today()
        
        # Get attendance logs for selected date
        date_logs = AttendanceLog.objects.filter(
            punch_time__date=selected_date
        ).order_by('-punch_time')
        
        # Get statistics
        total_logs = date_logs.count()
        unique_employees = date_logs.values('user_id').distinct().count()
        processed_logs = date_logs.filter(is_processed=True).count()
        unprocessed_logs = date_logs.filter(is_processed=False).count()
        
        # Get employee lookup dictionary
        user_ids = [log.user_id for log in date_logs[:50]]  # Limit to 50 for mobile
        employees_dict = {}
        if user_ids:
            employees = Employee.objects.filter(user_id__in=user_ids)
            employees_dict = {emp.user_id: emp for emp in employees}
        
        # Attach employee objects to logs
        log_list = date_logs[:50]
        for log in log_list:
            log.employee_obj = employees_dict.get(log.user_id)
        
        context = {
            'selected_date': selected_date,
            'today': date.today(),
            'is_today': selected_date == date.today(),
            'logs': log_list,
            'total_logs': total_logs,
            'unique_employees': unique_employees,
            'processed_logs': processed_logs,
            'unprocessed_logs': unprocessed_logs,
        }
        
        return render(request, 'zktest/mobile/dashboard.html', context)
