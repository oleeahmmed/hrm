from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    RangeDateFilter,
    RangeDateTimeFilter,
    ChoicesDropdownFilter,
    RelatedDropdownFilter,
    MultipleRelatedDropdownFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget, ArrayWidget
from django import forms

from .models import (
    Department, Designation, Shift, Employee, EmployeePersonalInfo,
    EmployeeEducation, EmployeeSalary, EmployeeSkill, AttendanceLog,
    Attendance, LeaveType, LeaveBalance, LeaveApplication, Holiday,
    Overtime, Notice, Location, UserLocation, Roster, RosterAssignment,
    RosterDay
)


# ==================== BASIC MODELS ADMIN ====================

@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = ('code', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', ('created_at', RangeDateTimeFilter))
    search_fields = ('name', 'code', 'description')
    list_editable = ('is_active',)
    ordering = ('name',)


@admin.register(Designation)
class DesignationAdmin(ModelAdmin):
    list_display = ('code', 'name', 'level', 'is_active', 'created_at')
    list_filter = ('is_active', 'level', ('created_at', RangeDateTimeFilter))
    search_fields = ('name', 'code', 'description')
    list_editable = ('is_active', 'level')
    ordering = ('level', 'name')


@admin.register(Shift)
class ShiftAdmin(ModelAdmin):
    list_display = ('code', 'name', 'start_time', 'end_time', 'break_time', 'grace_time', 'is_night_shift', 'is_active')
    list_filter = ('is_active', 'is_night_shift', ('created_at', RangeDateTimeFilter))
    search_fields = ('name', 'code')
    list_editable = ('is_active', 'is_night_shift')
    ordering = ('start_time',)


# ==================== EMPLOYEE ADMIN ====================

class EmployeePersonalInfoInline(admin.StackedInline):
    model = EmployeePersonalInfo
    extra = 0
    can_delete = False


class EmployeeSalaryInline(admin.StackedInline):
    model = EmployeeSalary
    extra = 0
    can_delete = False


class EmployeeEducationInline(admin.TabularInline):
    model = EmployeeEducation
    extra = 0


class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ('user_id', 'employee_id', 'get_full_name', 'department_code', 'designation_code', 'employment_status', 'is_active')
    list_filter = (
        'is_active', 
        ('employment_status', ChoicesDropdownFilter),
        'department_code',
        'designation_code',
        ('joining_date', RangeDateFilter),
        ('created_at', RangeDateTimeFilter)
    )
    search_fields = ('user_id', 'employee_id', 'first_name', 'last_name', 'email')
    list_editable = ('is_active',)
    ordering = ('employee_id',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_id', 'employee_id', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Organizational Details', {
            'fields': ('department_code', 'designation_code', 'shift_code')
        }),
        ('Employment Details', {
            'fields': ('joining_date', 'employment_status', 'is_active')
        }),
    )
    
    inlines = [EmployeePersonalInfoInline, EmployeeSalaryInline, EmployeeEducationInline, EmployeeSkillInline]


@admin.register(EmployeePersonalInfo)
class EmployeePersonalInfoAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'gender', 'marital_status', 'blood_group', 'city')
    list_filter = (
        ('gender', ChoicesDropdownFilter),
        ('marital_status', ChoicesDropdownFilter),
        ('blood_group', ChoicesDropdownFilter)
    )
    search_fields = ('user_id__first_name', 'user_id__last_name', 'nid', 'passport_no')
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'


@admin.register(EmployeeEducation)
class EmployeeEducationAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'education_level', 'degree_title', 'institution', 'passing_year')
    list_filter = (
        ('education_level', ChoicesDropdownFilter),
        'passing_year',
        ('created_at', RangeDateTimeFilter)
    )
    search_fields = ('user_id__first_name', 'user_id__last_name', 'degree_title', 'institution')
    ordering = ('-passing_year',)
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'base_salary', 'per_hour_rate', 'expected_working_hours', 'payment_method')
    list_filter = ('payment_method', ('effective_from', RangeDateFilter))
    search_fields = ('user_id__first_name', 'user_id__last_name', 'bank_name')
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'


@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'skill_name', 'skill_level', 'years_of_experience')
    list_filter = (
        ('skill_level', ChoicesDropdownFilter),
        'years_of_experience',
        ('created_at', RangeDateTimeFilter)
    )
    search_fields = ('user_id__first_name', 'user_id__last_name', 'skill_name')
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'


# ==================== ATTENDANCE ADMIN ====================

@admin.register(AttendanceLog)
class AttendanceLogAdmin(ModelAdmin):
    list_display = ('user_id', 'punch_time', 'device_sn', 'status', 'verify_type', 'is_processed', 'created_at')
    list_filter = (
        'is_processed',
        'device_sn',
        'status',
        'verify_type',
        ('punch_time', RangeDateTimeFilter),
        ('created_at', RangeDateTimeFilter)
    )
    search_fields = ('user_id', 'device_sn')
    list_editable = ('is_processed',)
    ordering = ('-punch_time',)
    readonly_fields = ('raw_data', 'created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_id', 'punch_time', 'device_sn')
        }),
        ('Attendance Details', {
            'fields': ('status', 'verify_type', 'work_code')
        }),
        ('Processing', {
            'fields': ('is_processed', 'processed_at')
        }),
        ('Raw Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def changelist_view(self, request, extra_context=None):
        """Add report link to changelist view"""
        extra_context = extra_context or {}
        extra_context['report_url'] = reverse('zktest:attendance-log-report')
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'date', 'status', 'check_in_time', 'check_out_time', 'work_hours', 'shift_code')
    list_filter = (
        ('status', ChoicesDropdownFilter),
        'shift_code',
        ('date', RangeDateFilter),
        'processed_from_logs',
        ('created_at', RangeDateTimeFilter)
    )
    search_fields = ('user_id__first_name', 'user_id__last_name', 'user_id__employee_id')
    ordering = ('-date',)
    
    fieldsets = (
        ('Employee & Date', {
            'fields': ('user_id', 'date', 'shift_code')
        }),
        ('Attendance Times', {
            'fields': ('check_in_time', 'check_out_time')
        }),
        ('Status & Hours', {
            'fields': ('status', 'work_hours', 'overtime_hours')
        }),
        ('Late & Early Out', {
            'fields': ('late_minutes', 'early_out_minutes')
        }),
        ('Processing Info', {
            'fields': ('processed_from_logs', 'last_processed_at', 'remarks'),
            'classes': ('collapse',)
        }),
    )
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'


# ==================== LEAVE MANAGEMENT ADMIN ====================

@admin.register(LeaveType)
class LeaveTypeAdmin(ModelAdmin):
    list_display = ('code', 'name', 'max_days', 'paid', 'carry_forward', 'requires_approval', 'is_active')
    list_filter = ('is_active', 'paid', 'carry_forward', 'requires_approval')
    search_fields = ('name', 'code', 'description')
    list_editable = ('is_active', 'paid', 'requires_approval')
    ordering = ('name',)


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'leave_type_code', 'year', 'entitled_days', 'used_days', 'get_remaining_days')
    list_filter = ('leave_type_code', 'year', ('created_at', RangeDateTimeFilter))
    search_fields = ('user_id__first_name', 'user_id__last_name')
    ordering = ('-year', 'user_id')
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'
    
    def get_remaining_days(self, obj):
        return obj.remaining_days
    get_remaining_days.short_description = 'Remaining Days'


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'leave_type_code', 'start_date', 'end_date', 'total_days', 'status')
    list_filter = (
        ('status', ChoicesDropdownFilter),
        'leave_type_code',
        ('start_date', RangeDateFilter),
        ('created_at', RangeDateTimeFilter)
    )
    search_fields = ('user_id__first_name', 'user_id__last_name', 'reason')
    ordering = ('-start_date',)
    
    fieldsets = (
        ('Employee & Leave Type', {
            'fields': ('user_id', 'leave_type_code')
        }),
        ('Leave Period', {
            'fields': ('start_date', 'end_date', 'total_days')
        }),
        ('Application Details', {
            'fields': ('reason', 'status')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
    )
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'


# ==================== OTHER MODELS ADMIN ====================

@admin.register(Holiday)
class HolidayAdmin(ModelAdmin):
    list_display = ('name', 'date', 'is_optional')
    list_filter = ('is_optional', ('date', RangeDateFilter))
    search_fields = ('name', 'description')
    ordering = ('-date',)


@admin.register(Overtime)
class OvertimeAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'date', 'overtime_hours', 'overtime_type', 'status', 'total_amount')
    list_filter = (
        ('status', ChoicesDropdownFilter),
        ('overtime_type', ChoicesDropdownFilter),
        ('date', RangeDateFilter),
        'is_paid'
    )
    search_fields = ('user_id__first_name', 'user_id__last_name')
    ordering = ('-date',)
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'


@admin.register(Notice)
class NoticeAdmin(ModelAdmin):
    list_display = ('title', 'priority', 'published_date', 'expiry_date', 'is_active')
    list_filter = (
        ('priority', ChoicesDropdownFilter),
        'is_active',
        ('published_date', RangeDateFilter)
    )
    search_fields = ('title', 'description')
    ordering = ('-published_date',)
    
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


@admin.register(Location)
class LocationAdmin(ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'radius', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    ordering = ('name',)


@admin.register(UserLocation)
class UserLocationAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'get_location_name', 'is_primary')
    list_filter = ('is_primary', 'location')
    search_fields = ('user_id__first_name', 'user_id__last_name', 'location__name')
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'
    
    def get_location_name(self, obj):
        return obj.location.name
    get_location_name.short_description = 'Location'


@admin.register(Roster)
class RosterAdmin(ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', ('start_date', RangeDateFilter))
    search_fields = ('name', 'description')
    ordering = ('-start_date',)


@admin.register(RosterAssignment)
class RosterAssignmentAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'get_roster_name', 'shift_code')
    list_filter = ('roster', 'shift_code')
    search_fields = ('user_id__first_name', 'user_id__last_name', 'roster__name')
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'
    
    def get_roster_name(self, obj):
        return obj.roster.name
    get_roster_name.short_description = 'Roster'


@admin.register(RosterDay)
class RosterDayAdmin(ModelAdmin):
    list_display = ('get_employee_name', 'date', 'shift_code', 'is_off')
    list_filter = ('is_off', 'shift_code', ('date', RangeDateFilter))
    search_fields = ('user_id__first_name', 'user_id__last_name')
    ordering = ('date',)
    
    def get_employee_name(self, obj):
        return obj.user_id.get_full_name()
    get_employee_name.short_description = 'Employee'
