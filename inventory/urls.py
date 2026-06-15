from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('uploads/', views.upload_inventory, name='upload_inventory'),
]
