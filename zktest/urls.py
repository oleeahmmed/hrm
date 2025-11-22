# ==================== zktest/urls.py ====================
"""
URL configuration for ZKTest app
"""
from django.urls import path
from zktest.views import (
    AttendanceLogReportView, 
    DailyAttendanceReportView,
    MobileLoginView,
    MobileLogoutView,
    MobileDashboardView
)

app_name = 'zktest'

urlpatterns = [
    # Admin Reports
    path('reports/attendance-log/', AttendanceLogReportView.as_view(), name='attendance-log-report'),
    path('reports/daily-attendance/', DailyAttendanceReportView.as_view(), name='daily-attendance-report'),
    
    # Mobile Views
    path('', MobileLoginView.as_view(), name='mobile-login'),
    path('mobile/logout/', MobileLogoutView.as_view(), name='mobile-logout'),
    path('mobile/dashboard/', MobileDashboardView.as_view(), name='mobile-dashboard'),
]
