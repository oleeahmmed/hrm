# ==================== hr/admin/hr_admin.py ====================
"""
HR Admin - Main HR models administration
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from unfold.admin import ModelAdmin, TabularInline

from hr.models import (
    Department, Designation, Shift, Employee,
    AttendanceLog, Attendance, Overtime,
    LeaveType, LeaveBalance, LeaveApplication,
    Holiday, Roster, RosterAssignment, RosterDay, Notice
)


# ==================== BASE ADMIN ====================

class HRBaseAdmin(ModelAdmin):
    """Base admin for HR models with auto-set company"""
    
    def save_model(self, request, obj, form, change):
        """Auto-set company from user profile"""
        if not change:
            if hasattr(request.user, 'profile'):
                if not obj.company_id and request.user.profile.company:
                    obj.company = request.user.profile.company
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Filter queryset by user's company for non-superusers"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'profile'):
            if request.user.profile.company:
                return qs.filter(company=request.user.profile.company)
        
        return qs.none()
    
    def get_exclude(self, request, obj=None):
        """Exclude company from forms if user has company in profile"""
        excluded = list(super().get_exclude(request, obj) or [])
        
        if hasattr(request.user, 'profile'):
            if request.user.profile.company:
                if hasattr(self.model, 'company'):
                    excluded.append('company')
        
        return excluded
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter foreign key choices by user's company"""
        if hasattr(request.user, 'profile') and request.user.profile.company:
            company = request.user.profile.company
            
            if db_field.name == "department":
                kwargs["queryset"] = Department.objects.filter(company=company)
            elif db_field.name == "designation":
                kwargs["queryset"] = Designation.objects.filter(company=company)
            elif db_field.name == "shift" or db_field.name == "default_shift":
                kwargs["queryset"] = Shift.objects.filter(company=company)
            elif db_field.name == "employee" or db_field.name == "reporting_to":
                kwargs["queryset"] = Employee.objects.filter(company=company)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ==================== DEPARTMENT ADMIN ====================

@admin.register(Department)
class DepartmentAdmin(HRBaseAdmin):
    list_display = ['code', 'name', 'company', 'head', 'is_active']
    list_filter = ['company', 'is_active']
    search_fields = ['code', 'name', 'description']
    list_editable = ['is_active']
    autocomplete_fields = ['head']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('code', 'name'),),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('👤 Management'), {
            'fields': (('head',),),
            'classes': ('tab',),
        }),
        (_('📝 Details'), {
            'fields': (('description',),),
            'classes': ('tab',),
        }),
        (_('⚙️ Status'), {
            'fields': (('is_active',), ('created_at', 'updated_at')),
            'classes': ('tab',),
        }),
    )


# ==================== DESIGNATION ADMIN ====================

@admin.register(Designation)
class DesignationAdmin(HRBaseAdmin):
    list_display = ['code', 'name', 'department', 'company', 'level', 'is_active']
    list_filter = ['company', 'department', 'is_active', 'level']
    search_fields = ['code', 'name', 'description']
    list_editable = ['is_active']
    autocomplete_fields = ['department']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('code', 'name'), ('department', 'level')),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('📝 Details'), {
            'fields': (('description',),),
            'classes': ('tab',),
        }),
        (_('⚙️ Status'), {
            'fields': (('is_active',), ('created_at', 'updated_at')),
            'classes': ('tab',),
        }),
    )


# ==================== SHIFT ADMIN ====================

@admin.register(Shift)
class ShiftAdmin(HRBaseAdmin):
    list_display = ['code', 'name', 'company', 'start_time', 'end_time', 'break_time', 'is_night_shift', 'is_active']
    list_filter = ['company', 'is_night_shift', 'is_active']
    search_fields = ['code', 'name']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('code', 'name'),),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('⏰ Timing'), {
            'fields': (('start_time', 'end_time'), ('break_time', 'grace_time'), ('is_night_shift',)),
            'classes': ('tab',),
        }),
        (_('⚙️ Status'), {
            'fields': (('is_active',), ('created_at', 'updated_at')),
            'classes': ('tab',),
        }),
    )


# ==================== EMPLOYEE ADMIN ====================

@admin.register(Employee)
class EmployeeAdmin(HRBaseAdmin):
    list_display = ['employee_id', 'get_full_name', 'company', 'department', 'designation', 'employment_status', 'is_active']
    list_filter = ['company', 'department', 'designation', 'employment_status', 'is_active', 'job_type', 'gender']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone_number', 'zkteco_id']
    list_editable = ['is_active']
    autocomplete_fields = ['department', 'designation', 'default_shift', 'reporting_to', 'user']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('employee_id', 'zkteco_id'), ('first_name', 'last_name'), ('user',)),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('💼 Organization'), {
            'fields': (('department', 'designation'), ('default_shift', 'reporting_to')),
            'classes': ('tab',),
        }),
        (_('👤 Personal'), {
            'fields': (('gender', 'date_of_birth'), ('blood_group', 'marital_status'), ('nid', 'passport_no')),
            'classes': ('tab',),
        }),
        (_('📞 Contact'), {
            'fields': (('phone_number', 'email'), ('emergency_contact_name', 'emergency_contact_phone'), ('emergency_contact_relation',)),
            'classes': ('tab',),
        }),
        (_('📍 Address'), {
            'fields': (('present_address',), ('permanent_address',), ('city',)),
            'classes': ('tab',),
        }),
        (_('💼 Employment'), {
            'fields': (('joining_date', 'confirmation_date'), ('job_type', 'employment_status'), ('resignation_date', 'termination_date')),
            'classes': ('tab',),
        }),
        (_('🎓 Education'), {
            'fields': (('highest_education', 'university'), ('passing_year',)),
            'classes': ('tab',),
        }),
        (_('💰 Payroll'), {
            'fields': (('base_salary', 'per_hour_rate'), ('expected_working_hours',), ('overtime_rate', 'overtime_grace_minutes')),
            'classes': ('tab',),
        }),
        (_('🏦 Banking'), {
            'fields': (('bank_name', 'bank_account_no'), ('bank_branch', 'payment_method')),
            'classes': ('tab',),
        }),
        (_('⚙️ Status'), {
            'fields': (('is_active',), ('created_at', 'updated_at')),
            'classes': ('tab',),
        }),
    )


# ==================== ATTENDANCE LOG ADMIN ====================

@admin.register(AttendanceLog)
class AttendanceLogAdmin(HRBaseAdmin):
    list_display = ['employee', 'timestamp', 'device', 'source_type', 'attendance_type', 'company']
    list_filter = ['company', 'device', 'source_type', 'attendance_type', 'timestamp']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name', 'device__name']
    date_hierarchy = 'timestamp'
    autocomplete_fields = ['device', 'employee']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('employee', 'device'), ('timestamp',)),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('📊 Details'), {
            'fields': (('source_type', 'attendance_type'), ('status_code', 'punch_type')),
            'classes': ('tab',),
        }),
        (_('📍 Location'), {
            'fields': (('latitude', 'longitude'), ('is_within_radius', 'distance'), ('device_info', 'ip_address')),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('tab',),
        }),
    )


# ==================== ATTENDANCE ADMIN ====================

@admin.register(Attendance)
class AttendanceAdmin(HRBaseAdmin):
    list_display = ['employee', 'date', 'shift', 'status', 'check_in_time', 'check_out_time', 'work_hours', 'overtime_hours', 'company']
    list_filter = ['company', 'status', 'date', 'shift']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    date_hierarchy = 'date'
    autocomplete_fields = ['employee', 'shift']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('employee', 'date'), ('shift',)),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('⏰ Timing'), {
            'fields': (('check_in_time', 'check_out_time'), ('work_hours', 'overtime_hours'), ('late_minutes', 'early_out_minutes')),
            'classes': ('tab',),
        }),
        (_('📊 Status'), {
            'fields': (('status',), ('remarks',)),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('tab',),
        }),
    )


# ==================== OVERTIME ADMIN ====================

@admin.register(Overtime)
class OvertimeAdmin(HRBaseAdmin):
    list_display = ['employee', 'date', 'overtime_hours', 'overtime_type', 'hourly_rate', 'total_amount', 'status', 'company']
    list_filter = ['company', 'status', 'overtime_type', 'date', 'is_paid']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    date_hierarchy = 'date'
    autocomplete_fields = ['employee', 'shift', 'attendance', 'approved_by']
    readonly_fields = ['total_amount', 'approved_at', 'created_at', 'updated_at']
    list_editable = ['status']
    actions = ['approve_selected', 'mark_as_paid']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('employee', 'date'), ('shift', 'attendance')),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('⏰ Time'), {
            'fields': (('start_time', 'end_time'), ('overtime_hours', 'overtime_type')),
            'classes': ('tab',),
        }),
        (_('💰 Payment'), {
            'fields': (('hourly_rate', 'overtime_rate_multiplier'), ('total_amount',)),
            'classes': ('tab',),
            'description': _('Total amount is calculated automatically'),
        }),
        (_('✅ Approval'), {
            'fields': (('status',), ('approved_by', 'approved_at'), ('is_paid', 'paid_date')),
            'classes': ('tab',),
        }),
        (_('📝 Remarks'), {
            'fields': (('remarks',),),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('tab',),
        }),
    )
    
    @admin.action(description=_('Approve Selected Overtime'))
    def approve_selected(self, request, queryset):
        """Approve selected overtime records"""
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(
            request,
            _('Successfully approved {} overtime record(s)').format(updated),
            level='success'
        )
    
    @admin.action(description=_('Mark as Paid'))
    def mark_as_paid(self, request, queryset):
        """Mark selected overtime as paid"""
        updated = queryset.filter(status='approved').update(
            status='paid',
            is_paid=True,
            paid_date=timezone.now().date()
        )
        self.message_user(
            request,
            _('Successfully marked {} overtime record(s) as paid').format(updated),
            level='success'
        )


# ==================== LEAVE TYPE ADMIN ====================

@admin.register(LeaveType)
class LeaveTypeAdmin(HRBaseAdmin):
    list_display = ['code', 'name', 'company', 'max_days', 'paid', 'carry_forward', 'is_active']
    list_filter = ['company', 'paid', 'carry_forward', 'is_active']
    search_fields = ['code', 'name', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('code', 'name'),),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('⚙️ Configuration'), {
            'fields': (('max_days',), ('paid', 'requires_approval'), ('carry_forward', 'max_carry_forward_days')),
            'classes': ('tab',),
        }),
        (_('📝 Details'), {
            'fields': (('description',),),
            'classes': ('tab',),
        }),
        (_('⚙️ Status'), {
            'fields': (('is_active',), ('created_at', 'updated_at')),
            'classes': ('tab',),
        }),
    )


# ==================== LEAVE BALANCE ADMIN ====================

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(HRBaseAdmin):
    list_display = ['employee', 'leave_type', 'year', 'entitled_days', 'used_days', 'remaining_days', 'company']
    list_filter = ['company', 'leave_type', 'year']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    autocomplete_fields = ['employee', 'leave_type']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('employee', 'leave_type'), ('year',)),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('📊 Balance'), {
            'fields': (('entitled_days', 'used_days'), ('carried_forward_days',)),
            'classes': ('tab',),
            'description': _('Used days are automatically updated when leave applications are approved/rejected'),
        }),
        (_('ℹ️ Info'), {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('tab',),
        }),
    )


# ==================== LEAVE APPLICATION ADMIN ====================

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(HRBaseAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'company']
    list_filter = ['company', 'leave_type', 'status', 'start_date']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name', 'reason']
    date_hierarchy = 'start_date'
    autocomplete_fields = ['employee', 'leave_type', 'approved_by']
    readonly_fields = ['total_days', 'approved_at', 'created_at', 'updated_at']
    list_editable = ['status']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('employee', 'leave_type'), ('start_date', 'end_date'), ('total_days',)),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile. Total days calculated automatically.'),
        }),
        (_('📝 Reason'), {
            'fields': (('reason',),),
            'classes': ('tab',),
        }),
        (_('✅ Approval'), {
            'fields': (('status',), ('approved_by', 'approved_at'), ('rejection_reason',)),
            'classes': ('tab',),
            'description': _('Approved At is set automatically when status changes to Approved'),
        }),
        (_('ℹ️ Info'), {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('tab',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-set approved_by when status changes to approved"""
        if obj.status == 'approved' and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)


# ==================== HOLIDAY ADMIN ====================

@admin.register(Holiday)
class HolidayAdmin(HRBaseAdmin):
    list_display = ['name', 'date', 'company', 'is_optional']
    list_filter = ['company', 'is_optional', 'date']
    search_fields = ['name', 'description']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('name', 'date'), ('is_optional',)),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('📝 Description'), {
            'fields': (('description',),),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('tab',),
        }),
    )


# ==================== ROSTER INLINE ====================

class RosterAssignmentInline(TabularInline):
    model = RosterAssignment
    extra = 1
    fields = ['employee', 'shift']
    autocomplete_fields = ['employee', 'shift']


# ==================== ROSTER ADMIN ====================

@admin.register(Roster)
class RosterAdmin(HRBaseAdmin):
    list_display = ['name', 'company', 'start_date', 'end_date', 'is_active']
    list_filter = ['company', 'is_active', 'start_date']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_date'
    inlines = [RosterAssignmentInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('name',), ('start_date', 'end_date')),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('📝 Description'), {
            'fields': (('description',),),
            'classes': ('tab',),
        }),
        (_('⚙️ Status'), {
            'fields': (('is_active',), ('created_at', 'updated_at')),
            'classes': ('tab',),
        }),
    )


# ==================== ROSTER ASSIGNMENT ADMIN ====================

@admin.register(RosterAssignment)
class RosterAssignmentAdmin(HRBaseAdmin):
    list_display = ['employee', 'roster', 'shift', 'company']
    list_filter = ['company', 'roster', 'shift']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name', 'roster__name']
    autocomplete_fields = ['roster', 'employee', 'shift']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('roster', 'employee'), ('shift',)),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('ℹ️ Info'), {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('tab',),
        }),
    )


# ==================== ROSTER DAY ADMIN ====================

@admin.register(RosterDay)
class RosterDayAdmin(HRBaseAdmin):
    list_display = ['employee', 'date', 'shift', 'is_off', 'company']
    list_filter = ['company', 'is_off', 'date', 'shift']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    date_hierarchy = 'date'
    autocomplete_fields = ['employee', 'shift']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('employee', 'date'), ('shift', 'is_off')),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('ℹ️ Info'), {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('tab',),
        }),
    )


# ==================== NOTICE ADMIN ====================

@admin.register(Notice)
class NoticeAdmin(HRBaseAdmin):
    list_display = ['title', 'company', 'priority', 'published_date', 'expiry_date', 'is_active']
    list_filter = ['company', 'priority', 'is_active', 'published_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'published_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('title',), ('priority',)),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('📝 Content'), {
            'fields': (('description',),),
            'classes': ('tab',),
        }),
        (_('📅 Dates'), {
            'fields': (('published_date', 'expiry_date'),),
            'classes': ('tab',),
        }),
        (_('⚙️ Status'), {
            'fields': (('is_active',), ('created_at', 'updated_at')),
            'classes': ('tab',),
        }),
    )
