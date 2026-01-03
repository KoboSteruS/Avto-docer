"""
View для страницы контактов
"""
from django.views.generic import TemplateView


class ContactsView(TemplateView):
    """
    Страница контактов
    """
    template_name = 'contacts/contacts.html'

