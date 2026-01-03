"""
View для детальной страницы услуги
"""
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from services.models import Service


class ServiceDetailView(DetailView):
    """
    Детальная страница услуги
    
    Отображает полную информацию об услуге с блоками контента
    """
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """
        Возвращаем только активные услуги
        """
        return Service.objects.filter(is_active=True)
    
    def get_object(self, queryset=None):
        """
        Получаем услугу по slug из URL
        """
        slug = self.kwargs.get(self.slug_url_kwarg)
        if slug is None:
            # Если slug не передан в kwargs, получаем из URL
            path_parts = self.request.path.strip('/').split('/')
            slug = path_parts[-1] if path_parts else None
        
        if queryset is None:
            queryset = self.get_queryset()
        
        return get_object_or_404(queryset, slug=slug)

