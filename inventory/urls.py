from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('uploads/', views.upload_inventory, name='upload_inventory'),
    path('products/<path:product_name>/', views.product_detail, name='product_detail'),
    path('inbound/', views.inbound_schedule, name='inbound_schedule'),
    path('templates/basic/', views.download_basic_template, name='download_basic_template'),
    path('templates/product-master/', views.download_product_master_template, name='download_product_master_template'),
    path('templates/inbound-schedule/', views.download_inbound_schedule_template, name='download_inbound_schedule_template'),
    path('templates/total-sales/', views.download_total_sales_template, name='download_total_sales_template'),
    path('templates/recent-sales/', views.download_recent_sales_template, name='download_recent_sales_template'),
    path('templates/current-stock/', views.download_current_stock_template, name='download_current_stock_template'),
]
