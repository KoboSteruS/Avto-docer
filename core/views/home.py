"""
View для главной страницы
"""
from django.views.generic import TemplateView
from services.models import Service
from works.models import Category


class HomeView(TemplateView):
    """
    Главная страница сайта
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        """
        Добавляет услуги и категории работ в контекст
        """
        context = super().get_context_data(**kwargs)
        # Получаем первые 6 активных услуг для отображения на главной
        context['services'] = Service.objects.filter(is_active=True).order_by('order', 'title')[:6]
        # Получаем категории работ в том же порядке, что и на странице "Наши работы"
        categories = Category.objects.filter(is_active=True).order_by('order', 'name')[:6]
        # Для каждой категории получаем первую работу (по порядку)
        for category in categories:
            first_work = category.works.filter(is_active=True).order_by('order', 'created_at').first()
            category.first_work = first_work
        context['work_categories'] = categories
        return context

