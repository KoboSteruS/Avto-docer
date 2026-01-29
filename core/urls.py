"""
URL-конфигурация для core приложения
"""
from django.urls import path
from core.views import HomeView, AboutView, PrivacyPolicyView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('o-studii/', AboutView.as_view(), name='about'),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy'),
]

