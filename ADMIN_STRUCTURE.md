# Admin Structure Documentation

## Overview
The admin interface has been reorganized into a modular structure with separate files for different functional areas.

## Directory Structure
```
zktest/
├── admin/
│   ├── __init__.py          # Imports all admin modules
│   ├── zkdeviceadmin.py     # ZK Device related admin classes
│   └── hradmin.py           # HR Management admin classes
```

## Files Description

### 1. zktest/admin/__init__.py
- Imports all admin modules to register them with Django admin
- Entry point for admin registration

### 2. zktest/admin/zkdeviceadmin.py
Contains admin classes for ZK Device Management:
- **ZKDeviceAdmin** - Device management with tabs
- **AttendanceLogAdmin** - Raw attendance logs from devices
- **DeviceUserAdmin** - Users registered on devices
- **DeviceCommandAdmin** - Commands sent to devices
- **OperationLogAdmin** - Device operation history
- **DeviceHeartbeatAdmin** - Device heartbeat monitoring
- **FingerprintTemplateAdmin** - Fingerprint data
- **FaceTemplateAdmin** - Face recognition data

### 3. zktest/admin/hradmin.py
Contains admin classes for HR Management:

#### Organization Structure
- **DepartmentAdmin** - Department management
- **DesignationAdmin** - Job positions/roles
- **ShiftAdmin** - Work shift definitions

#### Employee Management
- **EmployeeAdmin** - Main employee records with inline tabs
- **EmployeePersonalInfoAdmin** - Personal details
- **EmployeeEducationAdmin** - Educational qualifications
- **EmployeeSalaryAdmin** - Salary and payment info
- **EmployeeSkillAdmin** - Employee skills tracking

#### Attendance & Time
- **AttendanceAdmin** - Processed daily attendance
- **OvertimeAdmin** - Overtime records and approvals

#### Leave Management
- **LeaveTypeAdmin** - Leave type definitions
- **LeaveBalanceAdmin** - Employee leave balances
- **LeaveApplicationAdmin** - Leave requests
- **HolidayAdmin** - Company holidays

#### Roster Management
- **RosterAdmin** - Work schedule templates
- **RosterAssignmentAdmin** - Employee roster assignments
- **RosterDayAdmin** - Daily roster details

#### Location & Communication
- **LocationAdmin** - Geofencing locations
- **UserLocationAdmin** - Employee location assignments
- **NoticeAdmin** - Company announcements

## Key Features

### Tab-Based Fieldsets
All admin classes now use tab-based fieldsets with `'classes': ['tab']` for better organization:
```python
fieldsets = (
    ('Section Name', {
        'fields': (...),
        'classes': ['tab'],  # Creates a tab
    }),
)
```

### Inline Classes
Employee admin includes multiple inline tabs:
- EmployeePersonalInfoInline
- EmployeeSalaryInline
- EmployeeEducationInline
- EmployeeSkillInline
- LeaveBalanceInline

### Display Decorators
Using Unfold's `@display` decorator for enhanced list displays:
- Color-coded status badges
- Custom labels and icons
- Conditional formatting

### Actions
Custom admin actions for bulk operations:
- Device management (reboot, sync, etc.)
- User synchronization
- Status updates
- Approval workflows

## Unfold Sidebar Configuration

The sidebar in `config/settings.py` is organized into logical sections:

1. **Dashboard** - Main dashboard link
2. **Core Management** - User profiles, companies, projects, tasks
3. **HR Management** - Employees, departments, designations, shifts
4. **Attendance & Roster** - Attendance records, overtime, rosters
5. **Leave Management** - Leave applications, balances, types, holidays
6. **Employee Details** - Personal info, education, salary, skills
7. **Location & Notices** - Locations, user locations, notices
8. **ZK Device Management** - Devices, users, commands, heartbeats
9. **Attendance Logs** - Raw logs from devices
10. **Biometric Data** - Fingerprint and face templates
11. **Authentication** - Django users and groups

Each section is collapsible and includes permission checks.

## Benefits

1. **Modularity** - Separate concerns into logical files
2. **Maintainability** - Easier to find and update specific admin classes
3. **Scalability** - Easy to add new admin modules
4. **Organization** - Clear separation between device and HR management
5. **Tab Interface** - Better UX with tabbed fieldsets
6. **Comprehensive Sidebar** - All models accessible from sidebar

## Usage

No changes needed in code - Django automatically discovers admin classes through the `__init__.py` imports.

All admin classes are registered and available at `/admin/`.
