"""
Модель для дополнительных изображений услуг
"""
from django.db import models
from core.models import BaseModel
from .service import Service


class ServiceImage(BaseModel):
    """
    Дополнительные изображения для услуг
    
    Attributes:
        service: Связь с услугой
        image: Изображение
        caption: Подпись к изображению (опционально)
        order: Порядок сортировки
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='additional_images',
        verbose_name='Услуга'
    )
    image = models.ImageField(
        upload_to='services/additional/',
        verbose_name='Изображение',
        help_text='Дополнительное изображение для услуги'
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Подпись',
        help_text='Подпись к изображению (опционально)'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок сортировки',
        help_text='Чем меньше число, тем выше изображение в списке'
    )
    
    class Meta:
        verbose_name = 'Изображение услуги'
        verbose_name_plural = 'Изображения услуг'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['service', 'order']),
        ]
    
    def __str__(self) -> str:
        return f"{self.service.title} - Изображение {self.order}"

