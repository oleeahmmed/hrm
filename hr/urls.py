# ==================== hr/urls.py ====================
"""
URL configuration for HR app
"""
from django.urls import path
from hr.views import AttendanceReportView, AttendanceSummaryReportView, PayrollSummaryReportView

app_name = 'hr'

urlpatterns = [
    path('reports/attendance/', AttendanceReportView.as_view(), name='attendance-report'),
    path('reports/attendance-summary/', AttendanceSummaryReportView.as_view(), name='attendance-summary-report'),
    path('reports/payroll-summary/', PayrollSummaryReportView.as_view(), name='payroll-summary-report'),
]
