from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register our viewsets with it
router = DefaultRouter()

# Basic models
router.register(r'departments', api_views.DepartmentViewSet)
router.register(r'designations', api_views.DesignationViewSet)
router.register(r'shifts', api_views.ShiftViewSet)

# Employee models
router.register(r'employees', api_views.EmployeeViewSet)
router.register(r'employee-personal-info', api_views.EmployeePersonalInfoViewSet)
router.register(r'employee-education', api_views.EmployeeEducationViewSet)
router.register(r'employee-salary', api_views.EmployeeSalaryViewSet)
router.register(r'employee-skills', api_views.EmployeeSkillViewSet)

# Attendance models
router.register(r'attendance-logs', api_views.AttendanceLogViewSet)
router.register(r'attendance', api_views.AttendanceViewSet)

# Leave management
router.register(r'leave-types', api_views.LeaveTypeViewSet)
router.register(r'leave-balances', api_views.LeaveBalanceViewSet)
router.register(r'leave-applications', api_views.LeaveApplicationViewSet)

# Other models
router.register(r'holidays', api_views.HolidayViewSet)
router.register(r'overtime', api_views.OvertimeViewSet)
router.register(r'notices', api_views.NoticeViewSet)
router.register(r'locations', api_views.LocationViewSet)
router.register(r'user-locations', api_views.UserLocationViewSet)
router.register(r'rosters', api_views.RosterViewSet)
router.register(r'roster-assignments', api_views.RosterAssignmentViewSet)
router.register(r'roster-days', api_views.RosterDayViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    # Router URLs
    
    # ZKTeco device push endpoints (same as your previous API)
    path('zk-push/', api_views.ZKTecoAttendancePushView.as_view(), name='zk-push'),
    path('zk-cdata/', api_views.ZKTecoAttendancePushView.as_view(), name='zk-cdata'),
    
    # ZKTeco device endpoints (iclock protocol)
    path('iclock/getrequest', api_views.ZKTecoAttendancePushView.as_view(), name='zk_getrequest'),
    path('iclock/cdata', api_views.ZKTecoAttendancePushView.as_view(), name='zk_cdata'),
    
    # Custom API endpoints
    path('employee/<str:user_id>/attendance-summary/', 
         api_views.employee_attendance_summary, 
         name='employee-attendance-summary'),
    
    path('device/<str:device_sn>/logs/', 
         api_views.attendance_logs_by_device, 
         name='device-attendance-logs'),
    
    path('process-attendance-logs/', 
         api_views.process_attendance_logs, 
         name='process-attendance-logs'),
    
    path('dashboard-stats/', 
         api_views.dashboard_stats, 
         name='dashboard-stats'),
]

