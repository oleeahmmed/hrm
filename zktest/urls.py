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
    MobileAttendanceView,
    MobileEmployeeListView,
    MobileReportsView,
)

app_name = 'zktest'

urlpatterns = [
    # Admin Reports
    path('reports/attendance-log/', AttendanceLogReportView.as_view(), name='attendance-log-report'),
    path('reports/daily-attendance/', DailyAttendanceReportView.as_view(), name='daily-attendance-report'),
    
    # Mobile Views (will be accessed via /mobile/ prefix in main urls.py)
    path('mobile/', MobileLoginView.as_view(), name='mobile-login'),
    path('mobile/logout/', MobileLogoutView.as_view(), name='mobile-logout'),
    path('mobile/dashboard/', MobileDashboardView.as_view(), name='mobile-dashboard'),
    path('mobile/attendance/', MobileAttendanceView.as_view(), name='mobile-attendance'),
    path('mobile/employees/', MobileEmployeeListView.as_view(), name='mobile-employees'),
    path('mobile/reports/', MobileReportsView.as_view(), name='mobile-reports'),
]
