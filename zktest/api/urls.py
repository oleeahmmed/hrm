from django.urls import path
from . import api_views

app_name = 'zktest'

urlpatterns = [
    # ==========================================================================
    # ADMS Protocol Endpoints (Device Communication)
    # ==========================================================================
    
    # Main ADMS endpoints
    path('iclock/cdata', api_views.ADMSHandlerView.as_view(), name='adms_cdata'),
    path('iclock/getrequest', api_views.ADMSHandlerView.as_view(), name='adms_getrequest'),
    path('iclock/devicecmd', api_views.DeviceCommandAckView.as_view(), name='adms_devicecmd'),
    
    # Alternative paths (some devices use these)
    path('cdata', api_views.ADMSHandlerView.as_view(), name='adms_cdata_alt'),
    path('getrequest', api_views.ADMSHandlerView.as_view(), name='adms_getrequest_alt'),
    path('devicecmd', api_views.DeviceCommandAckView.as_view(), name='adms_devicecmd_alt'),
    
    # Legacy ZKTeco paths
    path('iclockpush/cdata', api_views.ADMSHandlerView.as_view(), name='adms_push_cdata'),
    path('iclockpush/getrequest', api_views.ADMSHandlerView.as_view(), name='adms_push_getrequest'),
    
    # ==========================================================================
    # REST API Endpoints
    # ==========================================================================
    
    # Health & Dashboard
    path('api/health/', api_views.health_check, name='health_check'),
    path('api/dashboard/', api_views.dashboard_stats, name='dashboard_stats'),
    
    # Devices
    path('api/devices/', api_views.DeviceListView.as_view(), name='device_list'),
    path('api/devices/<int:pk>/', api_views.DeviceDetailView.as_view(), name='device_detail'),
    path('api/devices/<int:device_id>/commands/', api_views.DeviceCommandView.as_view(), name='device_commands'),
    path('api/devices/<int:device_id>/users/', api_views.DeviceUsersView.as_view(), name='device_users'),
    path('api/devices/<int:device_id>/sync-tcp/', api_views.DeviceTCPSyncView.as_view(), name='device_tcp_sync'),
    # Bulk Operations
    path('api/commands/bulk/', api_views.BulkCommandView.as_view(), name='bulk_commands'),
    
    # Attendance
    path('api/attendance/', api_views.AttendanceListView.as_view(), name='attendance_list'),
    path('api/attendance/report/', api_views.AttendanceReportView.as_view(), name='attendance_report'),
    
    # Operation Logs
    path('api/operations/', api_views.OperationLogView.as_view(), name='operation_logs'),
]
