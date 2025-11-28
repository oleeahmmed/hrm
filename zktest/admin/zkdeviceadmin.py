from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta

from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action
from unfold.contrib.filters.admin import (
    RangeDateTimeFilter,
    ChoicesDropdownFilter,
    RelatedDropdownFilter,
)

from zktest.models import (
    ZKDevice, AttendanceLog, DeviceUser, 
    DeviceCommand, OperationLog, DeviceHeartbeat,
    FingerprintTemplate, FaceTemplate
)


# ==================== INLINE CLASSES ====================

class DeviceUserInline(TabularInline):
    model = DeviceUser
    extra = 0
    fields = ('user_id', 'name', 'privilege', 'has_fingerprint', 'has_face', 'is_active')
    readonly_fields = ('has_fingerprint', 'has_face')
    show_change_link = True
    tab = True


class DeviceCommandInline(TabularInline):
    model = DeviceCommand
    extra = 0
    fields = ('command_type', 'status', 'created_at', 'executed_at')
    readonly_fields = ('created_at', 'executed_at')
    show_change_link = True
    max_num = 10
    tab = True


# ==================== ZK DEVICE ADMIN ====================

@admin.register(ZKDevice)
class ZKDeviceAdmin(ModelAdmin):
    list_display = (
        'serial_number', 'device_name', 'ip_address', 
        'display_online_status', 'display_device_type',
        'user_count', 'fp_count', 'face_count', 'transaction_count', 
        'last_activity'
    )
    list_filter = (
        'is_active', 
        'is_online',
        ('device_type', ChoicesDropdownFilter),
        ('last_activity', RangeDateTimeFilter),
        ('registered_at', RangeDateTimeFilter),
    )
    search_fields = ('serial_number', 'device_name', 'ip_address', 'mac_address')
    list_editable = ('device_name',)
    ordering = ('-last_activity',)
    readonly_fields = ('registered_at', 'last_activity', 'created_at', 'updated_at')
    list_per_page = 25
    inlines = [DeviceUserInline, DeviceCommandInline]
    
    fieldsets = (
        ('Device Information', {
            'fields': (
                ('serial_number', 'device_name'),
                ('device_type', 'oem_vendor'),
            ),
            'description': 'Basic device identification',
            'classes': ['tab'],
        }),
        ('Network Configuration', {
            'fields': (
                ('ip_address', 'mac_address'),
            ),
            'classes': ['tab'],
        }),
        ('Device Details', {
            'fields': (
                ('firmware_version', 'platform'),
                ('push_version',),
            ),
            'classes': ['tab'],
        }),
        ('Status', {
            'fields': (
                ('is_active', 'is_online'),
                ('last_activity', 'registered_at'),
            ),
            'classes': ['tab'],
        }),
        ('Capabilities & Statistics', {
            'fields': (
                ('user_count', 'fp_count'),
                ('face_count', 'palm_count'),
                ('transaction_count',),
            ),
            'classes': ['tab'],
        }),
        ('ADMS Settings', {
            'fields': (
                ('push_interval', 'heartbeat_interval'),
                ('timezone_offset',),
            ),
            'classes': ['tab'],
        }),
    )
    
    actions = ['reboot_devices', 'sync_time', 'get_users_from_device', 'get_logs_from_device', 'mark_offline', 'clear_attendance_logs']
    
    @display(description='Status', label={
        True: 'success',
        False: 'danger'
    })
    def display_online_status(self, obj):
        if obj.last_activity:
            is_online = (timezone.now() - obj.last_activity) < timedelta(minutes=5)
            return is_online
        return False
    
    @display(description='Type', label={
        'attendance': 'info',
        'access': 'warning',
        'multi': 'success'
    })
    def display_device_type(self, obj):
        return obj.device_type
    
    @action(description="Reboot Selected Devices")
    def reboot_devices(self, request, queryset):
        for device in queryset:
            DeviceCommand.objects.create(
                device=device,
                command_type='REBOOT'
            )
        self.message_user(request, f"Reboot command queued for {queryset.count()} devices")
    
    @action(description="Sync Time")
    def sync_time(self, request, queryset):
        for device in queryset:
            DeviceCommand.objects.create(
                device=device,
                command_type='UPDATE_TIME'
            )
        self.message_user(request, f"Time sync command queued for {queryset.count()} devices")
    
    @action(description="Get Users from Device")
    def get_users_from_device(self, request, queryset):
        for device in queryset:
            DeviceCommand.objects.create(
                device=device,
                command_type='GET_USERS'
            )
        self.message_user(request, f"Get users command queued for {queryset.count()} devices")
    
    @action(description="Get Attendance Logs from Device")
    def get_logs_from_device(self, request, queryset):
        for device in queryset:
            DeviceCommand.objects.create(
                device=device,
                command_type='GET_LOGS'
            )
        self.message_user(request, f"Get logs command queued for {queryset.count()} devices")
    
    @action(description="Mark as Offline")
    def mark_offline(self, request, queryset):
        queryset.update(is_online=False)
        self.message_user(request, f"{queryset.count()} devices marked as offline")
    
    @action(description="Clear Attendance Logs")
    def clear_attendance_logs(self, request, queryset):
        for device in queryset:
            DeviceCommand.objects.create(
                device=device,
                command_type='CLEAR_LOG'
            )
        self.message_user(request, f"Clear log command queued for {queryset.count()} devices")


# ==================== ATTENDANCE LOG ADMIN ====================

@admin.register(AttendanceLog)
class AttendanceLogAdmin(ModelAdmin):
    list_display = (
        'user_id', 'display_device', 'punch_time', 
        'display_punch_type', 'display_verify_type',
        'display_temperature', 'display_sync_status', 'created_at'
    )
    list_filter = (
        ('device', RelatedDropdownFilter),
        ('punch_type', ChoicesDropdownFilter),
        ('verify_type', ChoicesDropdownFilter),
        'is_synced',
        ('punch_time', RangeDateTimeFilter),
        ('created_at', RangeDateTimeFilter),
    )
    search_fields = ('user_id', 'device__serial_number', 'device__device_name')
    ordering = ('-punch_time',)
    readonly_fields = ('raw_data', 'created_at', 'synced_at')
    date_hierarchy = 'punch_time'
    list_per_page = 50
    
    fieldsets = (
        ('Attendance Information', {
            'fields': (
                ('user_id', 'device'),
                ('punch_time',),
            ),
            'classes': ['tab'],
        }),
        ('Details', {
            'fields': (
                ('punch_type', 'verify_type'),
                ('work_code',),
            ),
            'classes': ['tab'],
        }),
        ('Additional Info', {
            'fields': (
                ('temperature', 'mask_status'),
            ),
            'classes': ['tab'],
        }),
        ('Sync Status', {
            'fields': (
                ('is_synced', 'synced_at'),
            ),
            'classes': ['tab'],
        }),
        ('Raw Data', {
            'fields': (('raw_data',),),
            'classes': ['tab'],
        }),
    )
    
    actions = ['mark_as_synced', 'mark_as_unsynced', 'export_selected']
    
    @display(description='Device', ordering='device__device_name')
    def display_device(self, obj):
        return obj.device.device_name or obj.device.serial_number
    
    @display(description='Punch', label={
        0: 'success',
        1: 'warning',
        2: 'info',
        3: 'info',
        4: 'primary',
        5: 'primary',
        255: 'danger',
    })
    def display_punch_type(self, obj):
        return obj.punch_type
    
    @display(description='Verify', label='info')
    def display_verify_type(self, obj):
        return obj.get_verify_type_display()
    
    @display(description='Temp')
    def display_temperature(self, obj):
        if obj.temperature:
            color = 'green' if obj.temperature < 37.5 else 'red'
            return format_html('<span style="color: {}">{} C</span>', color, obj.temperature)
        return '-'
    
    @display(description='Synced', label={
        True: 'success',
        False: 'warning'
    })
    def display_sync_status(self, obj):
        return obj.is_synced
    
    @action(description="Mark as Synced")
    def mark_as_synced(self, request, queryset):
        queryset.update(is_synced=True, synced_at=timezone.now())
        self.message_user(request, f"{queryset.count()} records marked as synced")
    
    @action(description="Mark as Unsynced")
    def mark_as_unsynced(self, request, queryset):
        queryset.update(is_synced=False, synced_at=None)
        self.message_user(request, f"{queryset.count()} records marked as unsynced")
    
    @action(description="Export Selected")
    def export_selected(self, request, queryset):
        self.message_user(request, f"Export feature - {queryset.count()} records selected")


# ==================== DEVICE USER ADMIN ====================

@admin.register(DeviceUser)
class DeviceUserAdmin(ModelAdmin):
    list_display = (
        'user_id', 'name', 'display_device', 
        'display_employee_status', 'display_privilege', 
        'display_biometrics', 'card_number', 'is_active'
    )
    list_filter = (
        ('device', RelatedDropdownFilter),
        ('privilege', ChoicesDropdownFilter),
        'is_active',
        'has_fingerprint',
        'has_face',
    )
    search_fields = ('user_id', 'name', 'card_number', 'device__device_name')
    list_editable = ('is_active',)
    ordering = ('device', 'user_id')
    list_per_page = 50
    
    fieldsets = (
        ('User Information', {
            'fields': (
                ('device', 'user_id'),
                ('name', 'privilege'),
            ),
            'classes': ['tab'],
        }),
        ('Authentication', {
            'fields': (
                ('card_number', 'password'),
                ('group',),
            ),
            'classes': ['tab'],
        }),
        ('Biometric Status', {
            'fields': (
                ('has_fingerprint', 'fp_count'),
                ('has_face', 'has_palm'),
            ),
            'classes': ['tab'],
        }),
        ('Status', {
            'fields': (('is_active',),),
            'classes': ['tab'],
        }),
    )
    
    actions = ['sync_to_device', 'delete_from_device', 'activate_users', 'deactivate_users', 'create_employees']
    
    @display(description='Device', ordering='device__device_name')
    def display_device(self, obj):
        return obj.device.device_name or obj.device.serial_number
    
    @display(description='Employee', label={
        True: 'success',
        False: 'warning'
    })
    def display_employee_status(self, obj):
        """Show if device user has corresponding employee record"""
        return obj.get_employee() is not None
    
    @display(description='Role', label={
        0: 'info',
        2: 'warning',
        6: 'success',
        14: 'danger',
    })
    def display_privilege(self, obj):
        return obj.privilege
    
    @display(description='Biometrics')
    def display_biometrics(self, obj):
        icons = []
        if obj.has_fingerprint:
            icons.append(format_html('<span title="Fingerprint">FP</span>'))
        if obj.has_face:
            icons.append(format_html('<span title="Face">Face</span>'))
        if obj.has_palm:
            icons.append(format_html('<span title="Palm">Palm</span>'))
        return format_html(' | '.join(icons)) if icons else '-'
    
    @action(description="Sync to Device")
    def sync_to_device(self, request, queryset):
        for user in queryset:
            DeviceCommand.objects.create(
                device=user.device,
                command_type='SET_USER',
                command_content=f"PIN={user.user_id}\tName={user.name}\tPri={user.privilege}"
            )
        self.message_user(request, f"Sync command queued for {queryset.count()} users")
    
    @action(description="Delete from Device")
    def delete_from_device(self, request, queryset):
        for user in queryset:
            DeviceCommand.objects.create(
                device=user.device,
                command_type='DEL_USER',
                command_content=f"PIN={user.user_id}"
            )
        self.message_user(request, f"Delete command queued for {queryset.count()} users")
    
    @action(description="Activate Users")
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} users activated")
    
    @action(description="Deactivate Users")
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} users deactivated")
    
    @action(description="Create Employee Records")
    def create_employees(self, request, queryset):
        created_count = 0
        for user in queryset:
            if not user.get_employee():
                employee = user.create_employee_if_not_exists()
                if employee:
                    created_count += 1
        self.message_user(request, f"Created {created_count} employee records")


# ==================== DEVICE COMMAND ADMIN ====================

@admin.register(DeviceCommand)
class DeviceCommandAdmin(ModelAdmin):
    list_display = (
        'id', 'display_device', 'display_command_type', 
        'display_status', 'created_at', 'sent_at', 'executed_at'
    )
    list_filter = (
        ('device', RelatedDropdownFilter),
        ('command_type', ChoicesDropdownFilter),
        ('status', ChoicesDropdownFilter),
        ('created_at', RangeDateTimeFilter),
    )
    search_fields = ('device__serial_number', 'device__device_name', 'command_content', 'command_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'sent_at', 'executed_at')
    list_per_page = 50
    
    fieldsets = (
        ('Command Information', {
            'fields': (
                ('device', 'command_type'),
                ('status',),
            ),
            'classes': ['tab'],
        }),
        ('Command Details', {
            'fields': (
                ('command_content',),
                ('command_id',),
            ),
            'classes': ['tab'],
        }),
        ('Response', {
            'fields': (
                ('response',),
                ('return_value',),
            ),
            'classes': ['tab'],
        }),
        ('Timestamps', {
            'fields': (
                ('created_at', 'sent_at', 'executed_at'),
            ),
            'classes': ['tab'],
        }),
    )
    
    actions = ['mark_as_pending', 'mark_as_failed', 'retry_commands']
    
    @display(description='Device', ordering='device__device_name')
    def display_device(self, obj):
        return obj.device.device_name or obj.device.serial_number
    
    @display(description='Command', label='info')
    def display_command_type(self, obj):
        return obj.get_command_type_display()
    
    @display(description='Status', label={
        'pending': 'warning',
        'sent': 'info',
        'executed': 'success',
        'failed': 'danger',
        'timeout': 'danger',
    })
    def display_status(self, obj):
        return obj.status
    
    @action(description="Mark as Pending")
    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending', sent_at=None, executed_at=None)
        self.message_user(request, f"{queryset.count()} commands marked as pending")
    
    @action(description="Mark as Failed")
    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"{queryset.count()} commands marked as failed")
    
    @action(description="Retry Commands")
    def retry_commands(self, request, queryset):
        count = 0
        for cmd in queryset.filter(status__in=['failed', 'timeout']):
            DeviceCommand.objects.create(
                device=cmd.device,
                command_type=cmd.command_type,
                command_content=cmd.command_content
            )
            count += 1
        self.message_user(request, f"{count} commands queued for retry")


# ==================== OPERATION LOG ADMIN ====================

@admin.register(OperationLog)
class OperationLogAdmin(ModelAdmin):
    list_display = (
        'display_device', 'display_operation_type',
        'admin_id', 'user_id', 'operation_time', 'created_at'
    )
    list_filter = (
        ('device', RelatedDropdownFilter),
        ('operation_type', ChoicesDropdownFilter),
        ('operation_time', RangeDateTimeFilter),
    )
    search_fields = ('device__device_name', 'admin_id', 'user_id', 'details')
    ordering = ('-operation_time',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'operation_time'
    list_per_page = 50
    
    fieldsets = (
        ('Operation Information', {
            'fields': (
                ('device', 'operation_type'),
                ('admin_id', 'user_id'),
                ('operation_time',),
            ),
            'classes': ['tab'],
        }),
        ('Details', {
            'fields': (('details',),),
            'classes': ['tab'],
        }),
        ('Raw Data', {
            'fields': (('raw_data',),),
            'classes': ['tab'],
        }),
    )
    
    @display(description='Device', ordering='device__device_name')
    def display_device(self, obj):
        return obj.device.device_name or obj.device.serial_number
    
    @display(description='Operation', label={
        'ENROLL': 'success',
        'DELETE': 'danger',
        'UPDATE': 'warning',
        'ADMIN_LOGIN': 'info',
        'ADMIN_LOGOUT': 'info',
        'CLEAR': 'danger',
        'REBOOT': 'warning',
        'OTHER': 'secondary',
    })
    def display_operation_type(self, obj):
        return obj.operation_type


# ==================== DEVICE HEARTBEAT ADMIN ====================

@admin.register(DeviceHeartbeat)
class DeviceHeartbeatAdmin(ModelAdmin):
    list_display = (
        'display_device', 'heartbeat_time', 'ip_address',
        'user_count', 'fp_count', 'face_count', 'log_count'
    )
    list_filter = (
        ('device', RelatedDropdownFilter),
        ('heartbeat_time', RangeDateTimeFilter),
    )
    search_fields = ('device__device_name', 'device__serial_number', 'ip_address')
    ordering = ('-heartbeat_time',)
    date_hierarchy = 'heartbeat_time'
    list_per_page = 50
    
    @display(description='Device', ordering='device__device_name')
    def display_device(self, obj):
        return obj.device.device_name or obj.device.serial_number


# ==================== FINGERPRINT TEMPLATE ADMIN ====================

@admin.register(FingerprintTemplate)
class FingerprintTemplateAdmin(ModelAdmin):
    list_display = (
        'user_id', 'display_device', 'finger_index', 
        'template_size', 'template_flag', 'created_at'
    )
    list_filter = (
        ('device', RelatedDropdownFilter),
        'finger_index',
    )
    search_fields = ('user_id', 'device__device_name')
    ordering = ('device', 'user_id', 'finger_index')
    list_per_page = 50
    
    @display(description='Device', ordering='device__device_name')
    def display_device(self, obj):
        return obj.device.device_name or obj.device.serial_number


# ==================== FACE TEMPLATE ADMIN ====================

@admin.register(FaceTemplate)
class FaceTemplateAdmin(ModelAdmin):
    list_display = (
        'user_id', 'display_device', 'face_index', 
        'template_size', 'created_at'
    )
    list_filter = (
        ('device', RelatedDropdownFilter),
    )
    search_fields = ('user_id', 'device__device_name')
    ordering = ('device', 'user_id')
    list_per_page = 50
    
    @display(description='Device', ordering='device__device_name')
    def display_device(self, obj):
        return obj.device.device_name or obj.device.serial_number
