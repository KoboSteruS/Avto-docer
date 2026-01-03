"""
URL-конфигурация для services приложения
"""
from django.urls import path
from services.views import ServicesListView, ServiceDetailView

app_name = 'services'

urlpatterns = [
    path('', ServicesListView.as_view(), name='list'),
    path('<slug:slug>/', ServiceDetailView.as_view(), name='detail'),
]

