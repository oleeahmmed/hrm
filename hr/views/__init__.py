# ==================== hr/views/__init__.py ====================
"""
HR Views Package
"""

from .device_admin_views import (
    device_test_connection,
    device_import_users,
    device_import_attendance,
    device_sync_all,
    device_clear_logs,
    device_test_connection_json,
    device_import_users_json,
    device_import_today_json,
    device_import_7days_json,
    device_import_30days_json,
    device_import_all_json,
    device_sync_all_json,
)

from .attendance_processor_views import (
    generate_attendance_for_config,
    generate_attendance_today_json,
    generate_attendance_7days_json,
    generate_attendance_15days_json,
    generate_attendance_30days_json,
    generate_attendance_all_json,
    generate_overtime_for_config,
    generate_overtime_today_json,
    generate_overtime_7days_json,
    generate_overtime_15days_json,
    generate_overtime_30days_json,
    generate_overtime_all_json,
)

from .attendance_report_views import AttendanceReportView, AttendanceSummaryReportView, PayrollSummaryReportView

__all__ = [
    'device_test_connection',
    'device_import_users',
    'device_import_attendance',
    'device_sync_all',
    'device_clear_logs',
    'device_test_connection_json',
    'device_import_users_json',
    'device_import_today_json',
    'device_import_7days_json',
    'device_import_30days_json',
    'device_import_all_json',
    'device_sync_all_json',
    'generate_attendance_for_config',
    'generate_attendance_today_json',
    'generate_attendance_7days_json',
    'generate_attendance_15days_json',
    'generate_attendance_30days_json',
    'generate_attendance_all_json',
    'generate_overtime_for_config',
    'generate_overtime_today_json',
    'generate_overtime_7days_json',
    'generate_overtime_15days_json',
    'generate_overtime_30days_json',
    'generate_overtime_all_json',
    'AttendanceReportView',
    'AttendanceSummaryReportView',
    'PayrollSummaryReportView',
]
