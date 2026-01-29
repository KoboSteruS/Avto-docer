"""
View для страницы политики конфиденциальности
"""
from django.views.generic import TemplateView


class PrivacyPolicyView(TemplateView):
    """
    Страница политики конфиденциальности
    """
    template_name = 'core/privacy.html'

