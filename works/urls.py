"""
URL-конфигурация для works приложения
"""
from django.urls import path
from works.views import WorksListView, CategoryDetailView

app_name = 'works'

urlpatterns = [
    path('nashi-raboty/', WorksListView.as_view(), name='list'),
    path('nashi-raboty/<slug:slug>/', CategoryDetailView.as_view(), name='category'),
]

