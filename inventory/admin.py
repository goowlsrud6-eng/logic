from django.contrib import admin
from .models import DailyShipment, InboundSchedule, ProductCloseStatus, ProductMaster, ProductOptionMetric, UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'file_type', 'week_label', 'reference_date', 'status', 'created_at')
    search_fields = ('original_name', 'week_label', 'file_hash')
    list_filter = ('file_type', 'status', 'created_at')


@admin.register(ProductOptionMetric)
class ProductOptionMetricAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'option_name', 'supplier_option_name', 'week_label', 'available_stock', 'recent_week_sales', 'inbound_recent_weeks', 'sales_trend')
    search_fields = ('product_name', 'option_name', 'product_code', 'supplier_option_name')
    list_filter = ('week_label', 'status', 'sales_trend')


@admin.register(DailyShipment)
class DailyShipmentAdmin(admin.ModelAdmin):
    list_display = ('delivery_date', 'product_name', 'option_name', 'quantity', 'uploaded_file')
    search_fields = ('product_name', 'option_name', 'product_code', 'supplier_option_name')
    list_filter = ('delivery_date',)


@admin.register(InboundSchedule)
class InboundScheduleAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'inbound_date', 'product_name', 'option_name', 'supplier_option_name', 'quantity', 'status', 'uploaded_file')
    search_fields = ('product_name', 'option_name', 'product_code', 'supplier_option_name', 'order_number')
    list_filter = ('order_number', 'inbound_date', 'status')


@admin.register(ProductMaster)
class ProductMasterAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'option_name', 'product_code', 'supplier_option_name', 'open_date')
    search_fields = ('product_name', 'option_name', 'product_code', 'supplier_option_name')
    list_filter = ('open_date',)


@admin.register(ProductCloseStatus)
class ProductCloseStatusAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'is_closed', 'updated_at')
    search_fields = ('product_name',)
    list_filter = ('is_closed',)
