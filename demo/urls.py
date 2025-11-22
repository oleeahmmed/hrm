"""
URL configuration for pharmacy app
"""
from django.urls import path
from .views import DashboardView, PurchaseReportView, SaleReportView, VisitReportView

app_name = 'pharmacy'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reports/purchase/', PurchaseReportView.as_view(), name='purchase_report'),
    path('reports/sale/', SaleReportView.as_view(), name='sale_report'),
    path('reports/visit/', VisitReportView.as_view(), name='visit_report'),
]