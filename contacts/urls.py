"""
URL-конфигурация для contacts приложения
"""
from django.urls import path
from contacts.views import ContactsView

app_name = 'contacts'

urlpatterns = [
    path('', ContactsView.as_view(), name='contacts'),
]

