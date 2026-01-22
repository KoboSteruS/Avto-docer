"""
Модель изображений для статьи
"""
from django.db import models
from core.models import BaseModel


class ArticleImage(BaseModel):
    """
    Модель для хранения множественных изображений для статьи.
    
    Attributes:
        article: Связь со статьей
        image: Изображение
        order: Порядок отображения
        caption: Подпись к изображению
    """
    article = models.ForeignKey(
        'Article',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Статья',
        help_text='Статья, к которой относится изображение'
    )
    image = models.ImageField(
        upload_to='articles/gallery/',
        verbose_name='Изображение',
        help_text='Изображение для галереи статьи'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок',
        help_text='Порядок отображения (меньше - выше)'
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Подпись',
        help_text='Подпись к изображению (необязательно)'
    )

    class Meta:
        verbose_name = 'Изображение статьи'
        verbose_name_plural = 'Изображения статьи'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['article', 'order']),
        ]

    def __str__(self) -> str:
        return f'{self.article.title} - Изображение {self.order}'
