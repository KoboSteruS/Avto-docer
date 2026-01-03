"""
Конфигурация приложения reviews
"""
from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
    verbose_name = 'Отзывы'
    
    def ready(self):
        """
        Импортируем админку при готовности приложения
        """
        import reviews.admin.review_admin  # noqa

