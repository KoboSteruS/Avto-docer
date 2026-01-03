"""
Модель работы
"""
from django.db import models
from core.models import BaseModel
from .category import Category


class Work(BaseModel):
    """
    Модель работы (фотографии)
    
    Attributes:
        category: Категория работы
        image: Изображение работы
        order: Порядок сортировки
        is_active: Флаг активности
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name='Категория',
        help_text='Категория, к которой относится работа'
    )
    image = models.ImageField(
        upload_to='works/',
        verbose_name='Изображение',
        help_text='Фотография выполненной работы'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок сортировки',
        help_text='Чем меньше число, тем выше работа в списке'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Показывать работу на сайте'
    )

    class Meta:
        verbose_name = 'Работа'
        verbose_name_plural = 'Работы'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active', 'order']),
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self) -> str:
        return f'{self.category.name} - {self.id}'

