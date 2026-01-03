"""
View для списка работ (категорий)
"""
from django.views.generic import ListView
from works.models import Category


class WorksListView(ListView):
    """
    Страница со списком категорий работ
    """
    model = Category
    template_name = 'works/works_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        """
        Возвращаем только активные категории, отсортированные по порядку
        """
        return Category.objects.filter(is_active=True).order_by('order', 'name')
    
    def get_context_data(self, **kwargs):
        """
        Добавляем случайные фото для каждой категории
        """
        context = super().get_context_data(**kwargs)
        # Для каждой категории получаем случайное фото
        for category in context['categories']:
            category.random_work = category.get_random_work_image()
        return context

