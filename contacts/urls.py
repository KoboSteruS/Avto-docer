"""
URL-конфигурация для contacts приложения
"""
from django.urls import path
from contacts.views import ContactsView, submit_contact_form_ajax

app_name = 'contacts'

urlpatterns = [
    path('', ContactsView.as_view(), name='contacts'),
    path('submit-form/', submit_contact_form_ajax, name='submit_form_ajax'),
]

