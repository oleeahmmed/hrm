# ==================== hr/admin/attendance_config_admin.py ====================
"""
AttendanceProcessorConfiguration Admin with Generation Actions
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import path
from unfold.admin import ModelAdmin

from hr.models import AttendanceProcessorConfiguration
from hr.views.attendance_processor_views import (
    generate_attendance_today_json,
    generate_attendance_7days_json,
    generate_attendance_15days_json,
    generate_attendance_30days_json,
    generate_attendance_all_json,
    generate_overtime_today_json,
    generate_overtime_7days_json,
    generate_overtime_15days_json,
    generate_overtime_30days_json,
    generate_overtime_all_json
)


@admin.register(AttendanceProcessorConfiguration)
class AttendanceProcessorConfigurationAdmin(ModelAdmin):
    """AttendanceProcessorConfiguration Admin with row-level generation actions"""
    
    list_display = ['name', 'company', 'is_active', 'grace_minutes', 'overtime_start_after_minutes', 'generation_actions', 'overtime_generation_actions']
    list_filter = ['company', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    change_list_template = 'admin/hr/attendanceprocessorconfiguration/change_list.html'
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('name', 'is_active'),),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile. Only one active config per company.'),
        }),
        (_('⏰ Basic Attendance'), {
            'fields': (('grace_minutes', 'early_out_threshold_minutes'), ('overtime_start_after_minutes', 'minimum_overtime_minutes')),
            'classes': ('tab',),
        }),
        (_('📅 Weekend'), {
            'fields': (('weekend_friday', 'weekend_saturday', 'weekend_sunday'), ('weekend_monday', 'weekend_tuesday', 'weekend_wednesday', 'weekend_thursday')),
            'classes': ('tab',),
        }),
        (_('☕ Break Time'), {
            'fields': (('default_break_minutes', 'use_shift_break_time'), ('break_deduction_method',)),
            'classes': ('tab',),
        }),
        (_('⏱️ Working Hours'), {
            'fields': (
                ('enable_minimum_working_hours_rule', 'minimum_working_hours_for_present'),
                ('enable_working_hours_half_day_rule',),
                ('half_day_minimum_hours', 'half_day_maximum_hours'),
                ('require_both_in_and_out',),
                ('enable_maximum_working_hours_rule', 'maximum_allowable_working_hours'),
            ),
            'classes': ('tab',),
        }),
        (_('🔄 Dynamic Shift'), {
            'fields': (
                ('enable_dynamic_shift_detection', 'dynamic_shift_tolerance_minutes'),
                ('multiple_shift_priority',),
                ('dynamic_shift_fallback_to_default', 'dynamic_shift_fallback_shift'),
                ('use_shift_grace_time',),
            ),
            'classes': ('tab',),
        }),
        (_('⚠️ Absence & Early Out'), {
            'fields': (
                ('enable_consecutive_absence_flagging', 'consecutive_absence_termination_risk_days'),
                ('enable_max_early_out_flagging',),
                ('max_early_out_threshold_minutes', 'max_early_out_occurrences'),
            ),
            'classes': ('tab',),
        }),
        (_('💰 Overtime'), {
            'fields': (
                ('overtime_calculation_method',),
                ('holiday_overtime_full_day', 'weekend_overtime_full_day'),
                ('late_affects_overtime', 'separate_ot_break_time'),
            ),
            'classes': ('tab',),
        }),
        (_('👤 Employee-Specific'), {
            'fields': (
                ('use_employee_specific_grace',),
                ('use_employee_specific_overtime',),
                ('use_employee_expected_hours',),
            ),
            'classes': ('tab',),
        }),
        (_('🔧 Advanced'), {
            'fields': (
                ('late_to_absent_days',),
                ('holiday_before_after_absent', 'weekend_before_after_absent'),
                ('require_holiday_presence',),
                ('include_holiday_analysis', 'holiday_buffer_days'),
            ),
            'classes': ('tab',),
        }),
        (_('👁️ Display'), {
            'fields': (
                ('show_absent_employees', 'show_leave_employees'),
                ('show_holiday_status', 'include_roster_info'),
            ),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('tab',),
        }),
    )
    
    def generation_actions(self, obj):
        """Display generation action buttons for each config"""
        return format_html(
            '''
            <div class="config-actions">
                <button class="config-action-btn btn-today" data-config-id="{}" data-action="generate_today" title="Generate Today">
                    <span class="material-symbols-outlined">today</span>
                    <span class="btn-text">Today</span>
                </button>
                <button class="config-action-btn btn-week" data-config-id="{}" data-action="generate_7days" title="Generate Last 7 Days">
                    <span class="material-symbols-outlined">date_range</span>
                    <span class="btn-text">7d</span>
                </button>
                <button class="config-action-btn btn-15days" data-config-id="{}" data-action="generate_15days" title="Generate Last 15 Days">
                    <span class="material-symbols-outlined">calendar_month</span>
                    <span class="btn-text">15d</span>
                </button>
                <button class="config-action-btn btn-month" data-config-id="{}" data-action="generate_30days" title="Generate Last 30 Days">
                    <span class="material-symbols-outlined">event</span>
                    <span class="btn-text">30d</span>
                </button>
                <button class="config-action-btn btn-all" data-config-id="{}" data-action="generate_all" title="Generate All">
                    <span class="material-symbols-outlined">calendar_view_month</span>
                    <span class="btn-text">All</span>
                </button>
            </div>
            <div class="action-result"></div>
            ''',
            obj.id, obj.id, obj.id, obj.id, obj.id
        )
    generation_actions.short_description = _('Generate Attendance')
    generation_actions.allow_tags = True
    
    def overtime_generation_actions(self, obj):
        """Display overtime generation action buttons for each config"""
        return format_html(
            '''
            <div class="config-actions overtime-actions">
                <button class="config-action-btn btn-today overtime-btn" data-config-id="{}" data-action="generate_overtime_today" title="Generate Overtime Today">
                    <span class="material-symbols-outlined">schedule</span>
                    <span class="btn-text">Today</span>
                </button>
                <button class="config-action-btn btn-week overtime-btn" data-config-id="{}" data-action="generate_overtime_7days" title="Generate Overtime Last 7 Days">
                    <span class="material-symbols-outlined">schedule</span>
                    <span class="btn-text">7d</span>
                </button>
                <button class="config-action-btn btn-15days overtime-btn" data-config-id="{}" data-action="generate_overtime_15days" title="Generate Overtime Last 15 Days">
                    <span class="material-symbols-outlined">schedule</span>
                    <span class="btn-text">15d</span>
                </button>
                <button class="config-action-btn btn-month overtime-btn" data-config-id="{}" data-action="generate_overtime_30days" title="Generate Overtime Last 30 Days">
                    <span class="material-symbols-outlined">schedule</span>
                    <span class="btn-text">30d</span>
                </button>
                <button class="config-action-btn btn-all overtime-btn" data-config-id="{}" data-action="generate_overtime_all" title="Generate Overtime All">
                    <span class="material-symbols-outlined">schedule</span>
                    <span class="btn-text">All</span>
                </button>
            </div>
            <div class="action-result overtime-result"></div>
            ''',
            obj.id, obj.id, obj.id, obj.id, obj.id
        )
    overtime_generation_actions.short_description = _('Generate Overtime')
    overtime_generation_actions.allow_tags = True
    
    def get_urls(self):
        """Add custom URLs for generation actions"""
        urls = super().get_urls()
        custom_urls = [
            # Attendance generation
            path('<int:config_id>/generate_today/', self.admin_site.admin_view(generate_attendance_today_json), name='attendance_config_generate_today'),
            path('<int:config_id>/generate_7days/', self.admin_site.admin_view(generate_attendance_7days_json), name='attendance_config_generate_7days'),
            path('<int:config_id>/generate_15days/', self.admin_site.admin_view(generate_attendance_15days_json), name='attendance_config_generate_15days'),
            path('<int:config_id>/generate_30days/', self.admin_site.admin_view(generate_attendance_30days_json), name='attendance_config_generate_30days'),
            path('<int:config_id>/generate_all/', self.admin_site.admin_view(generate_attendance_all_json), name='attendance_config_generate_all'),
            # Overtime generation
            path('<int:config_id>/generate_overtime_today/', self.admin_site.admin_view(generate_overtime_today_json), name='attendance_config_generate_overtime_today'),
            path('<int:config_id>/generate_overtime_7days/', self.admin_site.admin_view(generate_overtime_7days_json), name='attendance_config_generate_overtime_7days'),
            path('<int:config_id>/generate_overtime_15days/', self.admin_site.admin_view(generate_overtime_15days_json), name='attendance_config_generate_overtime_15days'),
            path('<int:config_id>/generate_overtime_30days/', self.admin_site.admin_view(generate_overtime_30days_json), name='attendance_config_generate_overtime_30days'),
            path('<int:config_id>/generate_overtime_all/', self.admin_site.admin_view(generate_overtime_all_json), name='attendance_config_generate_overtime_all'),
        ]
        return custom_urls + urls
    
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
                excluded.append('company')
        
        return excluded
