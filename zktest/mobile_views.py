# ==================== zktest/mobile_views.py ====================
"""
ZKTest Mobile Views - Complete HRM Mobile Interface
Responsive for both Mobile and Desktop with Dark/Light Mode
"""

from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
from django.db.models import Q, Count, Sum, Avg
from datetime import date, timedelta, datetime
from decimal import Decimal

from zktest.models import AttendanceLog, Employee, EmployeeSalary, Attendance, ZKDevice


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
    """Mobile Dashboard - Complete HRM Overview"""
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        today = date.today()
        
        # Today's Statistics
        today_logs = AttendanceLog.objects.filter(punch_time__date=today)
        total_logs_today = today_logs.count()
        unique_employees_today = today_logs.values('user_id').distinct().count()
        
        # Employee Statistics
        total_employees = Employee.objects.filter(is_active=True).count()
        total_devices = ZKDevice.objects.filter(is_active=True).count()
        online_devices = ZKDevice.objects.filter(is_active=True, is_online=True).count()
        
        # This Month Statistics
        month_start = today.replace(day=1)
        month_logs = AttendanceLog.objects.filter(punch_time__date__gte=month_start)
        total_logs_month = month_logs.count()
        
        # Recent Activity (Last 10 logs)
        recent_logs = AttendanceLog.objects.select_related('device').order_by('-punch_time')[:10]
        user_ids = [log.user_id for log in recent_logs]
        employees_dict = {}
        if user_ids:
            employees = Employee.objects.filter(user_id__in=user_ids)
            employees_dict = {emp.user_id: emp for emp in employees}
        
        for log in recent_logs:
            log.employee_obj = employees_dict.get(log.user_id)
        
        # Quick Stats Cards
        context = {
            'today': today,
            'total_employees': total_employees,
            'present_today': unique_employees_today,
            'absent_today': total_employees - unique_employees_today,
            'total_logs_today': total_logs_today,
            'total_logs_month': total_logs_month,
            'total_devices': total_devices,
            'online_devices': online_devices,
            'recent_logs': recent_logs,
        }
        
        return render(request, 'zktest/mobile/dashboard.html', context)


class MyAttendanceView(View):
    """My Attendance - Logged in user's attendance report
    
    Permission Logic:
    - Normal users: Can only see their own attendance
    - Staff/Superadmin: Can see all employees' attendance with filter
    """
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_employee(self, user):
        """Get employee record for logged in user"""
        try:
            return Employee.objects.get(portal_user=user)
        except Employee.DoesNotExist:
            try:
                return Employee.objects.get(user_id=user.username)
            except Employee.DoesNotExist:
                return None
    
    def get_date_range(self, request):
        """Parse date range from request or return default (last 30 days)"""
        start_str = request.GET.get('start_date')
        end_str = request.GET.get('end_date')
        
        if start_str and end_str:
            try:
                return (
                    datetime.strptime(start_str, '%Y-%m-%d').date(),
                    datetime.strptime(end_str, '%Y-%m-%d').date()
                )
            except ValueError:
                pass
        
        return date.today() - timedelta(days=30), date.today()
    
    def get(self, request):
        # Check if user is staff or superadmin
        is_admin = request.user.is_staff or request.user.is_superuser
        
        # Get employee filter (admin only)
        employee_id = request.GET.get('employee')
        
        # Determine which employee to show
        if is_admin and employee_id:
            # Admin viewing specific employee
            try:
                employee = Employee.objects.get(user_id=employee_id)
            except Employee.DoesNotExist:
                return render(request, 'zktest/mobile/my_attendance.html', {
                    'error': 'Employee not found.',
                    'is_admin': is_admin,
                })
        else:
            # Normal user or admin viewing own attendance
            employee = self.get_employee(request.user)
            if not employee:
                return render(request, 'zktest/mobile/my_attendance.html', {
                    'error': 'Employee record not found. Please contact admin.',
                    'is_admin': is_admin,
                })
        
        start_date, end_date = self.get_date_range(request)
        
        # Get data
        logs = AttendanceLog.objects.filter(
            user_id=employee.user_id,
            punch_time__date__range=[start_date, end_date]
        ).order_by('-punch_time')[:100]
        
        attendance = Attendance.objects.filter(
            user_id=employee,
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        # Calculate stats
        stats = attendance.aggregate(
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            work_hours=Sum('work_hours'),
            overtime=Sum('overtime_hours')
        )
        
        # Get all employees for filter (admin only)
        all_employees = None
        if is_admin:
            all_employees = Employee.objects.filter(is_active=True).order_by('employee_id')
        
        context = {
            'is_admin': is_admin,
            'employee': employee,
            'selected_employee': employee_id,
            'all_employees': all_employees,
            'start_date': start_date,
            'end_date': end_date,
            'logs': logs,
            'attendance_records': attendance,
            'total_days': (end_date - start_date).days + 1,
            'present_days': stats['present'] or 0,
            'absent_days': stats['absent'] or 0,
            'total_work_hours': round(stats['work_hours'] or 0, 2),
            'total_overtime': round(stats['overtime'] or 0, 2),
        }
        
        return render(request, 'zktest/mobile/my_attendance.html', context)


class AttendanceSummaryView(View):
    """Attendance Summary - All employees attendance summary"""
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Get date or date range
        report_type = request.GET.get('type', 'single')  # single or range
        
        if report_type == 'range':
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')
            
            if start_date_str and end_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    start_date = date.today()
                    end_date = date.today()
            else:
                start_date = date.today()
                end_date = date.today()
        else:
            # Single date
            selected_date_str = request.GET.get('date')
            if selected_date_str:
                try:
                    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                except ValueError:
                    selected_date = date.today()
            else:
                selected_date = date.today()
            
            start_date = selected_date
            end_date = selected_date
        
        # Get all active employees
        employees = Employee.objects.filter(is_active=True).order_by('employee_id')
        
        # Get attendance records for date range
        attendance_records = Attendance.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).select_related('user_id')
        
        # Calculate summary
        total_present = attendance_records.filter(status='present').values('user_id').distinct().count()
        total_absent = employees.count() - total_present
        total_work_hours = attendance_records.aggregate(Sum('work_hours'))['work_hours__sum'] or 0
        total_overtime = attendance_records.aggregate(Sum('overtime_hours'))['overtime_hours__sum'] or 0
        
        # Group by employee
        employee_summary = []
        for emp in employees[:50]:  # Limit to 50 for mobile
            emp_records = attendance_records.filter(user_id=emp)
            present_count = emp_records.filter(status='present').count()
            absent_count = emp_records.filter(status='absent').count()
            work_hours = emp_records.aggregate(Sum('work_hours'))['work_hours__sum'] or 0
            
            employee_summary.append({
                'employee': emp,
                'present_days': present_count,
                'absent_days': absent_count,
                'total_work_hours': round(work_hours, 2),
                'attendance_percentage': round((present_count / max((end_date - start_date).days + 1, 1)) * 100, 1)
            })
        
        context = {
            'report_type': report_type,
            'start_date': start_date,
            'end_date': end_date,
            'total_employees': employees.count(),
            'total_present': total_present,
            'total_absent': total_absent,
            'total_work_hours': round(total_work_hours, 2),
            'total_overtime': round(total_overtime, 2),
            'employee_summary': employee_summary,
        }
        
        return render(request, 'zktest/mobile/attendance_summary.html', context)


class AbsentReportView(View):
    """Absent Report - Shows absent employees"""
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Get date
        selected_date_str = request.GET.get('date')
        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = date.today()
        else:
            selected_date = date.today()
        
        # Get all active employees
        all_employees = Employee.objects.filter(is_active=True)
        
        # Get present employees (who have logs today)
        present_user_ids = AttendanceLog.objects.filter(
            punch_time__date=selected_date
        ).values_list('user_id', flat=True).distinct()
        
        # Get absent employees
        absent_employees = all_employees.exclude(user_id__in=present_user_ids).order_by('employee_id')
        
        # Get attendance records for absent employees
        absent_records = []
        for emp in absent_employees:
            # Check if there's a processed attendance record
            try:
                attendance = Attendance.objects.get(user_id=emp, date=selected_date)
                status = attendance.get_status_display()
            except Attendance.DoesNotExist:
                status = 'No Record'
            
            absent_records.append({
                'employee': emp,
                'status': status,
            })
        
        context = {
            'selected_date': selected_date,
            'total_employees': all_employees.count(),
            'present_count': len(present_user_ids),
            'absent_count': absent_employees.count(),
            'absent_records': absent_records,
        }
        
        return render(request, 'zktest/mobile/absent_report.html', context)


class EmployeeListView(View):
    """Employee List - All employees with search"""
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        search_query = request.GET.get('q', '')
        
        employees = Employee.objects.filter(is_active=True).order_by('employee_id')
        
        if search_query:
            employees = employees.filter(
                Q(employee_id__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(user_id__icontains=search_query)
            )
        
        # Get today's attendance
        today = date.today()
        today_logs = AttendanceLog.objects.filter(
            punch_time__date=today
        ).values_list('user_id', flat=True).distinct()
        
        # Mark present/absent
        for emp in employees:
            emp.is_present_today = emp.user_id in today_logs
        
        context = {
            'employees': employees[:100],  # Limit to 100
            'search_query': search_query,
            'total_employees': Employee.objects.filter(is_active=True).count(),
        }
        
        return render(request, 'zktest/mobile/employees.html', context)



class MobileAttendanceLogReportView(View):
    """Mobile Attendance Log Report - Raw punch data from ZKTeco devices
    
    Permission Logic:
    - Normal users: Can only see their own attendance logs
    - Staff/Superadmin: Can see all employees' attendance logs
    """
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Check if user is staff or superadmin
        is_admin = request.user.is_staff or request.user.is_superuser
        
        # Get filter parameters
        from_date_str = request.GET.get('from_date')
        to_date_str = request.GET.get('to_date')
        employee_id = request.GET.get('employee')
        device_sn = request.GET.get('device_sn')
        is_processed = request.GET.get('is_processed', '')
        
        # Parse dates
        if from_date_str:
            try:
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            except ValueError:
                from_date = date.today() - timedelta(days=7)
        else:
            from_date = date.today() - timedelta(days=7)
        
        if to_date_str:
            try:
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            except ValueError:
                to_date = date.today()
        else:
            to_date = date.today()
        
        # Base queryset
        logs = AttendanceLog.objects.all().order_by('-punch_time')
        
        # Permission-based filtering
        if not is_admin:
            # Normal user - only show their own logs
            logs = logs.filter(user_id=request.user.username)
        else:
            # Admin - can filter by employee
            if employee_id:
                logs = logs.filter(user_id=employee_id)
        
        # Apply date filters
        if from_date:
            logs = logs.filter(punch_time__date__gte=from_date)
        if to_date:
            logs = logs.filter(punch_time__date__lte=to_date)
        
        # Apply device filter
        if device_sn:
            logs = logs.filter(device__serial_number__icontains=device_sn)
        
        # Apply processing status filter
        if is_processed == 'true':
            logs = logs.filter(is_synced=True)
        elif is_processed == 'false':
            logs = logs.filter(is_synced=False)
        
        # Calculate statistics
        total_logs = logs.count()
        processed_logs = logs.filter(is_synced=True).count()
        unprocessed_logs = logs.filter(is_synced=False).count()
        unique_employees = logs.values('user_id').distinct().count()
        unique_devices = logs.values('device').distinct().count()
        
        # Processing rate
        processing_rate = 0
        if total_logs > 0:
            processing_rate = round((processed_logs / total_logs) * 100, 1)
        
        # Get status breakdown (punch_type)
        status_breakdown = {}
        for log in logs.values('punch_type').annotate(count=Count('id')):
            punch_type = log['punch_type']
            if punch_type is not None:
                status_name = dict(AttendanceLog.PUNCH_TYPES).get(punch_type, 'Unknown')
                status_breakdown[status_name] = log['count']
        
        # Limit logs for display (mobile optimization)
        log_list = logs[:100]
        
        # Get employee lookup dictionary
        user_ids = [log.user_id for log in log_list if log.user_id]
        employees_dict = {}
        if user_ids:
            employees = Employee.objects.filter(user_id__in=user_ids)
            employees_dict = {emp.user_id: emp for emp in employees}
        
        # Attach employee objects to logs
        for log in log_list:
            log.employee_obj = employees_dict.get(log.user_id)
        
        # Get all employees for filter (admin only)
        all_employees = None
        if is_admin:
            all_employees = Employee.objects.filter(is_active=True).order_by('employee_id')
        
        # Get all devices for filter
        all_devices = ZKDevice.objects.filter(is_active=True).order_by('device_name')
        
        context = {
            'is_admin': is_admin,
            'from_date': from_date,
            'to_date': to_date,
            'selected_employee': employee_id,
            'device_sn': device_sn,
            'is_processed': is_processed,
            'logs': log_list,
            'total_logs': total_logs,
            'processed_logs': processed_logs,
            'unprocessed_logs': unprocessed_logs,
            'unique_employees': unique_employees,
            'unique_devices': unique_devices,
            'processing_rate': processing_rate,
            'status_breakdown': status_breakdown,
            'all_employees': all_employees,
            'all_devices': all_devices,
        }
        
        return render(request, 'zktest/mobile/attendance_log_report.html', context)
