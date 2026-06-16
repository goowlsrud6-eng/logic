from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('uploads/', views.upload_inventory, name='upload_inventory'),
    path('templates/basic/', views.download_basic_template, name='download_basic_template'),
]
