from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import Patient, Medicine, Purchase, Visit, Sale

# Configure default admin site
admin.site.site_header = 'ফার্মেসি ম্যানেজমেন্ট সিস্টেম'
admin.site.site_title = 'ফার্মেসি অ্যাডমিন'
admin.site.index_title = 'ড্যাশবোর্ড'

class PatientAdmin(ModelAdmin):
    list_display = ['name', 'phone', 'total_visits', 'last_visit', 'created_at']
    search_fields = ['name', 'phone']
    list_filter = ['created_at']
    
    def total_visits(self, obj):
        return obj.visit_set.count()
    total_visits.short_description = "মোট ভিজিট"
    
    def last_visit(self, obj):
        last = obj.visit_set.first()
        return last.visit_date.strftime('%d/%m/%Y') if last else "কোন ভিজিট নেই"
    last_visit.short_description = "শেষ ভিজিট"

class MedicineAdmin(ModelAdmin):
    list_display = ['name', 'company', 'unit_price', 'stock_quantity', 'stock_status']
    search_fields = ['name', 'company']
    list_filter = ['company', 'created_at']
    
    def stock_status(self, obj):
        if obj.stock_quantity <= 5:
            return format_html('<span style="color: red;">কম স্টক</span>')
        elif obj.stock_quantity <= 20:
            return format_html('<span style="color: orange;">মাঝারি</span>')
        else:
            return format_html('<span style="color: green;">পর্যাপ্ত</span>')
    stock_status.short_description = "স্টক অবস্থা"

class PurchaseAdmin(ModelAdmin):
    list_display = ['medicine', 'quantity', 'unit_cost', 'total_cost', 'supplier', 'purchase_date']
    list_filter = ['purchase_date', 'supplier']
    search_fields = ['medicine__name', 'supplier']
    date_hierarchy = 'purchase_date'

class SaleInline(admin.TabularInline):
    model = Sale
    extra = 1
    fields = ['medicine', 'quantity', 'unit_price', 'payment_type']
    autocomplete_fields = ['medicine']
    


class VisitAdmin(ModelAdmin):
    list_display = ['patient', 'visit_date', 'total_medicines', 'total_amount']
    list_filter = ['visit_date']
    search_fields = ['patient__name']
    date_hierarchy = 'visit_date'
    inlines = [SaleInline]
    autocomplete_fields = ['patient']
    
    def total_medicines(self, obj):
        return obj.sale_set.count()
    total_medicines.short_description = "ওষুধের সংখ্যা"
    
    def total_amount(self, obj):
        total = obj.sale_set.aggregate(Sum('total_price'))['total_price__sum'] or 0
        return f"৳{total}"
    total_amount.short_description = "মোট টাকা"

class SaleAdmin(ModelAdmin):
    list_display = ['visit', 'medicine', 'quantity', 'unit_price', 'total_price', 'payment_type', 'sale_date']
    list_filter = ['payment_type', 'sale_date', 'medicine']
    search_fields = ['visit__patient__name', 'medicine__name']
    date_hierarchy = 'sale_date'
# Register models with default admin
admin.site.register(Patient, PatientAdmin)
admin.site.register(Medicine, MedicineAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Sale, SaleAdmin)

# Custom URL configuration for admin
from .views import DashboardView, get_medicine_price, PurchaseReportView, SaleReportView, VisitReportView

original_get_urls = admin.site.get_urls

def custom_get_urls():
    from django.urls import path
    custom_urls = [
        path('pharmacy-dashboard/', admin.site.admin_view(DashboardView.as_view()), name='pharmacy-dashboard'),
        path('get-medicine-price/', admin.site.admin_view(get_medicine_price), name='get-medicine-price'),
        path('pharmacy-purchase-report/', admin.site.admin_view(PurchaseReportView.as_view()), name='pharmacy-purchase-report'),
        path('pharmacy-sale-report/', admin.site.admin_view(SaleReportView.as_view()), name='pharmacy-sale-report'),
        path('pharmacy-visit-report/', admin.site.admin_view(VisitReportView.as_view()), name='pharmacy-visit-report'),
    ]
    return custom_urls + original_get_urls()

admin.site.get_urls = custom_get_urls