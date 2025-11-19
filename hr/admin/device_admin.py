# ==================== hr/admin/device_admin.py ====================
"""
ZKDevice Admin with Device Operations
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import path
from unfold.admin import ModelAdmin

from hr.models import ZkDevice
from hr.views.device_admin_views import (
    device_test_connection_json,
    device_import_users_json,
    device_import_today_json,
    device_import_7days_json,
    device_import_30days_json,
    device_import_all_json,
    device_sync_all_json
)


@admin.register(ZkDevice)
class ZkDeviceAdmin(ModelAdmin):
    """ZKDevice Admin with row-level device actions"""
    
    list_display = ['name', 'ip_address', 'port', 'company', 'is_active', 'last_synced', 'device_actions']
    list_filter = ['company', 'is_active']
    search_fields = ['name', 'ip_address', 'description']
    list_editable = ['is_active']
    readonly_fields = ['last_synced', 'created_at', 'updated_at']
    
    change_list_template = 'admin/hr/zkdevice/change_list.html'
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (('name',), ('ip_address', 'port'), ('password',)),
            'classes': ('tab',),
            'description': _('Company is auto-set from your profile'),
        }),
        (_('📝 Description'), {
            'fields': (('description',),),
            'classes': ('tab',),
        }),
        (_('⚙️ Status'), {
            'fields': (('is_active', 'last_synced'), ('created_at', 'updated_at')),
            'classes': ('tab',),
        }),
    )
    
    def device_actions(self, obj):
        """Display device action buttons for each device"""
        return format_html(
            '''
            <div class="device-actions">
                <button class="device-action-btn btn-test" data-device-id="{}" data-action="test" title="Test Connection">
                    <span class="material-symbols-outlined">wifi_tethering</span>
                    <span class="btn-text">Test</span>
                </button>
                <button class="device-action-btn btn-users" data-device-id="{}" data-action="import_users" title="Import Users">
                    <span class="material-symbols-outlined">group</span>
                    <span class="btn-text">Users</span>
                </button>
                <button class="device-action-btn btn-today" data-device-id="{}" data-action="import_today" title="Import Today">
                    <span class="material-symbols-outlined">today</span>
                    <span class="btn-text">Today</span>
                </button>
                <button class="device-action-btn btn-week" data-device-id="{}" data-action="import_7days" title="Import 7 Days">
                    <span class="material-symbols-outlined">date_range</span>
                    <span class="btn-text">7d</span>
                </button>
                <button class="device-action-btn btn-month" data-device-id="{}" data-action="import_30days" title="Import 30 Days">
                    <span class="material-symbols-outlined">event</span>
                    <span class="btn-text">30d</span>
                </button>
                <button class="device-action-btn btn-all" data-device-id="{}" data-action="import_all" title="Import All">
                    <span class="material-symbols-outlined">calendar_view_month</span>
                    <span class="btn-text">All</span>
                </button>
                <button class="device-action-btn btn-sync" data-device-id="{}" data-action="sync_all" title="Sync All">
                    <span class="material-symbols-outlined">sync</span>
                    <span class="btn-text">Sync</span>
                </button>
            </div>
            <div class="action-result"></div>
            ''',
            obj.id, obj.id, obj.id, obj.id, obj.id, obj.id, obj.id
        )
    device_actions.short_description = _('Device Actions')
    device_actions.allow_tags = True
    
    def get_urls(self):
        """Add custom URLs for device actions"""
        urls = super().get_urls()
        custom_urls = [
            path('<int:device_id>/test/', self.admin_site.admin_view(device_test_connection_json), name='zkdevice_test'),
            path('<int:device_id>/import_users/', self.admin_site.admin_view(device_import_users_json), name='zkdevice_import_users'),
            path('<int:device_id>/import_today/', self.admin_site.admin_view(device_import_today_json), name='zkdevice_import_today'),
            path('<int:device_id>/import_7days/', self.admin_site.admin_view(device_import_7days_json), name='zkdevice_import_7days'),
            path('<int:device_id>/import_30days/', self.admin_site.admin_view(device_import_30days_json), name='zkdevice_import_30days'),
            path('<int:device_id>/import_all/', self.admin_site.admin_view(device_import_all_json), name='zkdevice_import_all'),
            path('<int:device_id>/sync_all/', self.admin_site.admin_view(device_sync_all_json), name='zkdevice_sync_all'),
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
