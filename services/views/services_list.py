"""
View для списка услуг
"""
from django.views.generic import ListView
from services.models import Service


class ServicesListView(ListView):
    """
    Страница со списком всех услуг
    """
    model = Service
    template_name = 'services/services_list.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        """
        Возвращаем только активные услуги, отсортированные по порядку
        """
        return Service.objects.filter(is_active=True).order_by('order', 'title')

