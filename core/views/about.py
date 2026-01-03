"""
View для страницы "О студии"
"""
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """
    Страница "О студии"
    """
    template_name = 'core/about.html'

