"""
URL configuration for core app
"""
from django.urls import path
from .views import DashboardView, TaskReportView

app_name = 'core'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reports/tasks/', TaskReportView.as_view(), name='task-report'),
]
