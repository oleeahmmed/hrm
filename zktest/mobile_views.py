# ==================== zktest/mobile_views.py ====================
"""
ZKTest Mobile Views - Mobile Interface Views
"""

from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
from datetime import date, timedelta, datetime
from decimal import Decimal

from zktest.models import AttendanceLog, Employee, EmployeeSalary
from zktest.utils import generate_attendance_from_logs, get_work_day_range


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
    """Mobile Dashboard View - Shows today's summary"""
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        today = date.today()
        
        # Get today's attendance logs
        today_logs = AttendanceLog.objects.filter(
            punch_time__date=today
        ).order_by('-punch_time')
        
        # Get statistics
        total_logs = today_logs.count()
        unique_employees = today_logs.values('user_id').distinct().count()
        processed_logs = today_logs.filter(is_synced=True).count()
        unprocessed_logs = today_logs.filter(is_synced=False).count()
        
        # Get total employees
        total_employees = Employee.objects.filter(is_active=True).count()
        
        # Get recent logs (last 10)
        recent_logs = today_logs[:10]
        user_ids = [log.user_id for log in recent_logs]
        employees_dict = {}
        if user_ids:
            employees = Employee.objects.filter(user_id__in=user_ids)
            employees_dict = {emp.user_id: emp for emp in employees}
        
        # Attach employee objects to logs
        for log in recent_logs:
            log.employee_obj = employees_dict.get(log.user_id)
        
        context = {
            'today': today,
            'total_logs': total_logs,
            'unique_employees': unique_employees,
            'total_employees': total_employees,
            'processed_logs': processed_logs,
            'unprocessed_logs': unprocessed_logs,
            'recent_logs': recent_logs,
        }
        
        return render(request, 'zktest/mobile/dashboard.html', context)


class MobileAttendanceView(View):
    """Mobile Attendance View - Shows attendance logs by date"""
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Get date from query parameter or use today
        selected_date_str = request.GET.get('date')
        if selected_date_str:
            try:
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
        processed_logs = date_logs.filter(is_synced=True).count()
        unprocessed_logs = date_logs.filter(is_synced=False).count()
        
        # Get employee lookup dictionary
        user_ids = [log.user_id for log in date_logs[:100]]
        employees_dict = {}
        if user_ids:
            employees = Employee.objects.filter(user_id__in=user_ids)
            employees_dict = {emp.user_id: emp for emp in employees}
        
        # Attach employee objects to logs
        log_list = date_logs[:100]
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
        
        return render(request, 'zktest/mobile/attendance.html', context)


class MobileEmployeeListView(View):
    """Mobile Employee List View"""
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Get search query
        search_query = request.GET.get('q', '')
        
        # Get employees
        employees = Employee.objects.filter(is_active=True).order_by('employee_id')
        
        if search_query:
            employees = employees.filter(
                models.Q(employee_id__icontains=search_query) |
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(user_id__icontains=search_query)
            )
        
        # Limit to 50 employees for mobile
        employees = employees[:50]
        
        # Get today's attendance for these employees
        today = date.today()
        today_logs = AttendanceLog.objects.filter(
            punch_time__date=today,
            user_id__in=[emp.user_id for emp in employees]
        ).values('user_id').distinct()
        
        present_user_ids = set([log['user_id'] for log in today_logs])
        
        # Mark employees as present/absent
        for emp in employees:
            emp.is_present_today = emp.user_id in present_user_ids
        
        context = {
            'employees': employees,
            'search_query': search_query,
            'total_employees': Employee.objects.filter(is_active=True).count(),
        }
        
        return render(request, 'zktest/mobile/employees.html', context)


class MobileReportsView(View):
    """Mobile Reports View - Simple daily report"""
    
    @method_decorator(login_required(login_url='zktest:mobile-login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Get date from query parameter or use today
        selected_date_str = request.GET.get('date')
        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = date.today()
        else:
            selected_date = date.today()
        
        # Get active employees
        employees = Employee.objects.filter(is_active=True).order_by('employee_id')[:20]
        
        # Generate attendance for each employee
        attendance_records = []
        total_present = 0
        total_absent = 0
        total_work_hours = Decimal('0.00')
        
        for emp in employees:
            # Get employee salary info
            try:
                salary_info = EmployeeSalary.objects.get(user_id=emp)
                per_hour_rate = salary_info.per_hour_rate
            except EmployeeSalary.DoesNotExist:
                per_hour_rate = Decimal('0.00')
            
            # Get logs for this employee
            emp_logs = AttendanceLog.objects.filter(user_id=emp.user_id).order_by('punch_time')
            
            # Generate attendance for this date
            attendance_data = generate_attendance_from_logs(
                user_id=emp.user_id,
                date=selected_date,
                attendance_logs=emp_logs,
                per_hour_rate=per_hour_rate,
                break_time_minutes=60
            )
            
            if attendance_data:
                attendance_data['employee'] = emp
                attendance_records.append(attendance_data)
                
                if attendance_data['status'] == 'present':
                    total_present += 1
                    total_work_hours += attendance_data['work_hours']
                else:
                    total_absent += 1
            else:
                total_absent += 1
                attendance_records.append({
                    'employee': emp,
                    'user_id': emp.user_id,
                    'date': selected_date,
                    'status': 'absent',
                    'check_in_time': None,
                    'check_out_time': None,
                    'work_hours': Decimal('0.00'),
                    'daily_amount': Decimal('0.00'),
                })
        
        context = {
            'selected_date': selected_date,
            'today': date.today(),
            'attendance_records': attendance_records,
            'total_present': total_present,
            'total_absent': total_absent,
            'total_work_hours': round(total_work_hours, 2),
        }
        
        return render(request, 'zktest/mobile/reports.html', context)
