# ==================== hr/views/attendance_report_views.py ====================
"""
Attendance Report Views
"""

from django.contrib import admin
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from hr.models import Attendance, Employee, Department, Shift
from hr.forms import AttendanceReportForm


class AttendanceReportView(View):
    """Attendance Report View"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        form = AttendanceReportForm(user=request.user, data=request.GET or None)
        
        # Default queryset
        attendances = Attendance.objects.select_related(
            'employee', 'employee__department', 'shift', 'company'
        ).order_by('-date', 'employee__employee_id')
        
        # Filter by user's company
        if hasattr(request.user, 'profile'):
            attendances = attendances.filter(company=request.user.profile.company)
        elif not request.user.is_superuser:
            attendances = attendances.none()
        
        # Apply filters if form is valid
        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            employee = form.cleaned_data.get('employee')
            department = form.cleaned_data.get('department')
            shift = form.cleaned_data.get('shift')
            status = form.cleaned_data.get('status')
            
            if from_date:
                attendances = attendances.filter(date__gte=from_date)
            if to_date:
                attendances = attendances.filter(date__lte=to_date)
            if employee:
                attendances = attendances.filter(employee=employee)
            if department:
                attendances = attendances.filter(employee__department=department)
            if shift:
                attendances = attendances.filter(shift=shift)
            if status:
                attendances = attendances.filter(status=status)
        
        # Calculate statistics
        total_records = attendances.count()
        present_count = attendances.filter(status='present').count()
        absent_count = attendances.filter(status='absent').count()
        half_day_count = attendances.filter(status='half_day').count()
        leave_count = attendances.filter(status='leave').count()
        holiday_count = attendances.filter(status='holiday').count()
        weekend_count = attendances.filter(status='weekend').count()
        
        # Calculate hours
        total_work_hours = attendances.aggregate(
            total=Sum('work_hours')
        )['total'] or Decimal('0.00')
        
        total_overtime_hours = attendances.aggregate(
            total=Sum('overtime_hours')
        )['total'] or Decimal('0.00')
        
        # Calculate average work hours
        avg_work_hours = attendances.filter(
            status='present'
        ).aggregate(
            avg=Avg('work_hours')
        )['avg'] or Decimal('0.00')
        
        # Late arrivals
        late_count = attendances.filter(late_minutes__gt=0).count()
        
        # Early departures
        early_out_count = attendances.filter(early_out_minutes__gt=0).count()
        
        # Attendance rate (present / total working days)
        working_days = attendances.exclude(
            status__in=['holiday', 'weekend']
        ).count()
        attendance_rate = 0
        if working_days > 0:
            attendance_rate = round((present_count / working_days) * 100, 2)
        
        context = {
            **admin.site.each_context(request),
            'title': 'Attendance Report',
            'subtitle': 'View and filter attendance records',
            'form': form,
            'attendances': attendances[:200],  # Limit to 200 records
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'half_day_count': half_day_count,
            'leave_count': leave_count,
            'holiday_count': holiday_count,
            'weekend_count': weekend_count,
            'total_work_hours': total_work_hours,
            'total_overtime_hours': total_overtime_hours,
            'avg_work_hours': round(avg_work_hours, 2) if avg_work_hours else 0,
            'late_count': late_count,
            'early_out_count': early_out_count,
            'attendance_rate': attendance_rate,
        }
        
        return render(request, 'admin/hr/attendance_report.html', context)



class AttendanceSummaryReportView(View):
    """Attendance Summary Report View - Aggregated by Employee"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        from hr.forms import AttendanceSummaryReportForm
        
        form = AttendanceSummaryReportForm(user=request.user, data=request.GET or None)
        
        # Default queryset
        attendances = Attendance.objects.select_related(
            'employee', 'employee__department', 'shift', 'company'
        )
        
        # Filter by user's company
        if hasattr(request.user, 'profile'):
            attendances = attendances.filter(company=request.user.profile.company)
            company = request.user.profile.company
        elif not request.user.is_superuser:
            attendances = attendances.none()
            company = None
        else:
            company = None
        
        # Apply filters if form is valid
        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            department = form.cleaned_data.get('department')
            
            if from_date:
                attendances = attendances.filter(date__gte=from_date)
            if to_date:
                attendances = attendances.filter(date__lte=to_date)
            if department:
                attendances = attendances.filter(employee__department=department)
        
        # Get active employees
        employees = Employee.objects.filter(
            company=company,
            is_active=True
        ).select_related('department', 'designation', 'default_shift')
        
        if form.is_valid() and form.cleaned_data.get('department'):
            employees = employees.filter(department=form.cleaned_data.get('department'))
        
        # Calculate summary for each employee
        employee_summaries = []
        
        for employee in employees:
            emp_attendances = attendances.filter(employee=employee)
            
            total_days = emp_attendances.count()
            present_days = emp_attendances.filter(status='present').count()
            absent_days = emp_attendances.filter(status='absent').count()
            half_days = emp_attendances.filter(status='half_day').count()
            leave_days = emp_attendances.filter(status='leave').count()
            holiday_days = emp_attendances.filter(status='holiday').count()
            weekend_days = emp_attendances.filter(status='weekend').count()
            
            # Calculate hours
            total_work_hours = emp_attendances.aggregate(
                total=Sum('work_hours')
            )['total'] or Decimal('0.00')
            
            total_overtime_hours = emp_attendances.aggregate(
                total=Sum('overtime_hours')
            )['total'] or Decimal('0.00')
            
            # Calculate late and early out
            late_count = emp_attendances.filter(late_minutes__gt=0).count()
            early_out_count = emp_attendances.filter(early_out_minutes__gt=0).count()
            
            # Calculate attendance rate (present / working days)
            working_days = emp_attendances.exclude(
                status__in=['holiday', 'weekend']
            ).count()
            
            attendance_rate = 0
            if working_days > 0:
                attendance_rate = round((present_days / working_days) * 100, 2)
            
            employee_summaries.append({
                'employee': employee,
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'half_days': half_days,
                'leave_days': leave_days,
                'holiday_days': holiday_days,
                'weekend_days': weekend_days,
                'total_work_hours': round(total_work_hours, 2),
                'total_overtime_hours': round(total_overtime_hours, 2),
                'late_count': late_count,
                'early_out_count': early_out_count,
                'attendance_rate': attendance_rate,
                'working_days': working_days,
            })
        
        # Calculate overall statistics
        total_employees = len(employee_summaries)
        total_present = sum(s['present_days'] for s in employee_summaries)
        total_absent = sum(s['absent_days'] for s in employee_summaries)
        total_leave = sum(s['leave_days'] for s in employee_summaries)
        total_work_hours = sum(s['total_work_hours'] for s in employee_summaries)
        total_overtime_hours = sum(s['total_overtime_hours'] for s in employee_summaries)
        
        # Calculate average attendance rate
        avg_attendance_rate = 0
        if employee_summaries:
            avg_attendance_rate = round(
                sum(s['attendance_rate'] for s in employee_summaries) / len(employee_summaries),
                2
            )
        
        context = {
            **admin.site.each_context(request),
            'title': 'Attendance Summary Report',
            'subtitle': 'Employee-wise attendance summary',
            'form': form,
            'employee_summaries': employee_summaries,
            'total_employees': total_employees,
            'total_present': total_present,
            'total_absent': total_absent,
            'total_leave': total_leave,
            'total_work_hours': total_work_hours,
            'total_overtime_hours': total_overtime_hours,
            'avg_attendance_rate': avg_attendance_rate,
        }
        
        return render(request, 'admin/hr/attendance_summary_report.html', context)



class PayrollSummaryReportView(View):
    """Payroll Summary Report View - Bangladesh Payslip Format"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        from hr.forms import PayrollSummaryReportForm
        from calendar import monthrange
        
        form = PayrollSummaryReportForm(user=request.user, data=request.GET or None)
        
        # Get filter values
        if form.is_valid():
            month = int(form.cleaned_data.get('month'))
            year = int(form.cleaned_data.get('year'))
            department = form.cleaned_data.get('department')
        else:
            # Default to current month/year
            month = timezone.now().month
            year = timezone.now().year
            department = None
        
        # Calculate date range for the month
        first_day = timezone.datetime(year, month, 1).date()
        last_day = timezone.datetime(year, month, monthrange(year, month)[1]).date()
        
        # Filter by user's company
        if hasattr(request.user, 'profile'):
            company = request.user.profile.company
        elif not request.user.is_superuser:
            company = None
        else:
            company = None
        
        # Get active employees
        employees = Employee.objects.filter(
            company=company,
            is_active=True
        ).select_related('department', 'designation', 'default_shift')
        
        if department:
            employees = employees.filter(department=department)
        
        # Calculate payroll for each employee
        payroll_summaries = []
        
        for employee in employees:
            # Get attendance data for the month
            attendances = Attendance.objects.filter(
                employee=employee,
                date__range=[first_day, last_day]
            )
            
            # Calculate attendance stats
            total_days = (last_day - first_day).days + 1
            present_days = attendances.filter(status='present').count()
            absent_days = attendances.filter(status='absent').count()
            leave_days = attendances.filter(status='leave').count()
            
            # Calculate working days (exclude weekends and holidays)
            working_days = attendances.exclude(
                status__in=['weekend', 'holiday']
            ).count()
            
            # Calculate hours
            total_work_hours = attendances.aggregate(
                total=Sum('work_hours')
            )['total'] or Decimal('0.00')
            
            total_overtime_hours = attendances.aggregate(
                total=Sum('overtime_hours')
            )['total'] or Decimal('0.00')
            
            # Get approved overtime for the month
            overtime_records = Overtime.objects.filter(
                employee=employee,
                date__range=[first_day, last_day],
                status__in=['approved', 'paid']
            )
            
            overtime_amount = overtime_records.aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0.00')
            
            # Calculate salary components (Bangladesh format)
            base_salary = employee.base_salary
            
            # Basic Salary (typically 60% of gross in Bangladesh)
            basic_salary = base_salary * Decimal('0.60')
            
            # House Rent Allowance (typically 30% of basic)
            house_rent = basic_salary * Decimal('0.30')
            
            # Medical Allowance (typically 10% of basic)
            medical_allowance = basic_salary * Decimal('0.10')
            
            # Conveyance Allowance (fixed amount or percentage)
            conveyance = basic_salary * Decimal('0.05')
            
            # Gross Salary
            gross_salary = basic_salary + house_rent + medical_allowance + conveyance
            
            # Deductions
            # Absent deduction (per day rate * absent days)
            if working_days > 0:
                per_day_rate = gross_salary / Decimal(str(working_days))
                absent_deduction = per_day_rate * Decimal(str(absent_days))
            else:
                per_day_rate = Decimal('0.00')
                absent_deduction = Decimal('0.00')
            
            # Tax deduction (simplified - actual would be based on tax slabs)
            tax_deduction = Decimal('0.00')
            if gross_salary > 25000:
                tax_deduction = (gross_salary - Decimal('25000')) * Decimal('0.05')
            
            # Provident Fund (if applicable - typically 10% of basic)
            provident_fund = Decimal('0.00')  # Can be enabled based on company policy
            
            # Total Deductions
            total_deductions = absent_deduction + tax_deduction + provident_fund
            
            # Net Salary
            net_salary = gross_salary - total_deductions + overtime_amount
            
            payroll_summaries.append({
                'employee': employee,
                'month': month,
                'year': year,
                'total_days': total_days,
                'working_days': working_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'leave_days': leave_days,
                'total_work_hours': round(total_work_hours, 2),
                'total_overtime_hours': round(total_overtime_hours, 2),
                # Earnings
                'basic_salary': round(basic_salary, 2),
                'house_rent': round(house_rent, 2),
                'medical_allowance': round(medical_allowance, 2),
                'conveyance': round(conveyance, 2),
                'overtime_amount': round(overtime_amount, 2),
                'gross_salary': round(gross_salary, 2),
                # Deductions
                'absent_deduction': round(absent_deduction, 2),
                'tax_deduction': round(tax_deduction, 2),
                'provident_fund': round(provident_fund, 2),
                'total_deductions': round(total_deductions, 2),
                # Net
                'net_salary': round(net_salary, 2),
                'per_day_rate': round(per_day_rate, 2),
            })
        
        # Calculate overall statistics
        total_employees = len(payroll_summaries)
        total_gross = sum(s['gross_salary'] for s in payroll_summaries)
        total_deductions_all = sum(s['total_deductions'] for s in payroll_summaries)
        total_overtime = sum(s['overtime_amount'] for s in payroll_summaries)
        total_net = sum(s['net_salary'] for s in payroll_summaries)
        
        # Month name
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]
        
        context = {
            **admin.site.each_context(request),
            'title': 'Payroll Summary Report',
            'subtitle': f'Salary summary for {month_name} {year}',
            'form': form,
            'payroll_summaries': payroll_summaries,
            'month': month,
            'year': year,
            'month_name': month_name,
            'total_employees': total_employees,
            'total_gross': total_gross,
            'total_deductions_all': total_deductions_all,
            'total_overtime': total_overtime,
            'total_net': total_net,
        }
        
        return render(request, 'admin/hr/payroll_summary_report.html', context)
