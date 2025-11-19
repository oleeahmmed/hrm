# ==================== hr/admin/__init__.py ====================
"""
HR Admin Package
Import all admin classes to register them
"""

from .hr_admin import (
    DepartmentAdmin,
    DesignationAdmin,
    ShiftAdmin,
    EmployeeAdmin,
    AttendanceLogAdmin,
    AttendanceAdmin,
    OvertimeAdmin,
    LeaveTypeAdmin,
    LeaveBalanceAdmin,
    LeaveApplicationAdmin,
    HolidayAdmin,
    RosterAdmin,
    RosterAssignmentAdmin,
    RosterDayAdmin,
    NoticeAdmin,
)

from .device_admin import ZkDeviceAdmin
from .attendance_config_admin import AttendanceProcessorConfigurationAdmin

__all__ = [
    'DepartmentAdmin',
    'DesignationAdmin',
    'ShiftAdmin',
    'EmployeeAdmin',
    'ZkDeviceAdmin',
    'AttendanceLogAdmin',
    'AttendanceAdmin',
    'OvertimeAdmin',
    'LeaveTypeAdmin',
    'LeaveBalanceAdmin',
    'LeaveApplicationAdmin',
    'HolidayAdmin',
    'RosterAdmin',
    'RosterAssignmentAdmin',
    'RosterDayAdmin',
    'NoticeAdmin',
    'AttendanceProcessorConfigurationAdmin',
]
