"""
View для главной страницы
"""
from django.views.generic import TemplateView
from services.models import Service
from works.models import Work


class HomeView(TemplateView):
    """
    Главная страница сайта
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        """
        Добавляет услуги и работы в контекст
        """
        context = super().get_context_data(**kwargs)
        # Получаем первые 6 активных услуг для отображения на главной
        context['services'] = Service.objects.filter(is_active=True).order_by('order', 'title')[:6]
        # Получаем все активные работы для ротации (без ограничений по категории)
        all_works = Work.objects.filter(is_active=True).order_by('?')
        context['works'] = list(all_works)  # Все работы для переливания
        return context

