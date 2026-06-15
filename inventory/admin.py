from django.contrib import admin
from .models import ProductOptionMetric, UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'week_label', 'status', 'created_at')
    search_fields = ('original_name', 'week_label', 'file_hash')
    list_filter = ('status', 'created_at')


@admin.register(ProductOptionMetric)
class ProductOptionMetricAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'option_name', 'week_label', 'available_stock', 'recent_week_sales', 'inbound_recent_weeks', 'status')
    search_fields = ('product_name', 'option_name', 'product_code')
    list_filter = ('week_label', 'status')
