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
        # Получаем больше работ для ротации (минимум 9, чтобы было достаточно для смены)
        all_works = Work.objects.filter(is_active=True).order_by('?')
        context['works'] = list(all_works[:9])  # Берем 9 работ для ротации
        return context

