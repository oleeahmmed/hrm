# ==================== zktest/urls.py ====================
"""
URL configuration for ZKTest app
"""
from django.urls import path
from zktest.views import AttendanceLogReportView, DailyAttendanceReportView

app_name = 'zktest'

urlpatterns = [
    path('reports/attendance-log/', AttendanceLogReportView.as_view(), name='attendance-log-report'),
    path('reports/daily-attendance/', DailyAttendanceReportView.as_view(), name='daily-attendance-report'),
]
