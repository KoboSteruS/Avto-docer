"""
Конфигурация приложения works
"""
from django.apps import AppConfig


class WorksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'works'
    verbose_name = 'Работы'
    
    def ready(self):
        """
        Импортируем админку при готовности приложения
        """
        import works.admin.category_admin  # noqa
        import works.admin.work_admin  # noqa

