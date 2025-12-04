# ==================== zktest/urls.py ====================
"""
URL configuration for ZKTest app
"""
from django.urls import path
from zktest.report_views import (
    AttendanceLogReportView, 
    DailyAttendanceReportView,
)
from zktest.mobile_views import (
    MobileLoginView,
    MobileLogoutView,
    MobileDashboardView,
    MyAttendanceView,
    AttendanceSummaryView,
    AbsentReportView,
    EmployeeListView,
    MobileAttendanceLogReportView,
)

app_name = 'zktest'

urlpatterns = [
    # Admin Reports
    path('reports/attendance-log/', AttendanceLogReportView.as_view(), name='attendance-log-report'),
    path('reports/daily-attendance/', DailyAttendanceReportView.as_view(), name='daily-attendance-report'),
    
    # Mobile Views - Complete HRM System
    path('', MobileLoginView.as_view(), name='mobile-login'),
    path('mobile/logout/', MobileLogoutView.as_view(), name='mobile-logout'),
    path('mobile/dashboard/', MobileDashboardView.as_view(), name='mobile-dashboard'),
    path('mobile/my-attendance/', MyAttendanceView.as_view(), name='mobile-my-attendance'),
    path('mobile/attendance-summary/', AttendanceSummaryView.as_view(), name='mobile-attendance-summary'),
    path('mobile/absent-report/', AbsentReportView.as_view(), name='mobile-absent-report'),
    path('mobile/employees/', EmployeeListView.as_view(), name='mobile-employees'),
    path('mobile/attendance-log-report/', MobileAttendanceLogReportView.as_view(), name='mobile-attendance-log-report'),
]
