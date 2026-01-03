"""
View для детальной страницы категории работ
"""
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from works.models import Category


class CategoryDetailView(DetailView):
    """
    Детальная страница категории с мозаикой фотографий
    """
    model = Category
    template_name = 'works/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """
        Возвращаем только активные категории
        """
        return Category.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        """
        Добавляем работы категории в контекст
        """
        context = super().get_context_data(**kwargs)
        context['works'] = self.object.works.filter(is_active=True).order_by('order', '-created_at')
        return context

