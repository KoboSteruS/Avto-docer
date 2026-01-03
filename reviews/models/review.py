"""
Модель отзыва
"""
from django.db import models
from core.models import BaseModel


class Review(BaseModel):
    """
    Модель отзыва клиента
    
    Attributes:
        name: Имя клиента
        car: Марка и модель автомобиля
        rating: Рейтинг от 1 до 5
        text: Текст отзыва
        is_published: Флаг публикации (для модерации)
    """
    class Rating(models.IntegerChoices):
        """Выбор рейтинга"""
        ONE = 1, '1 звезда'
        TWO = 2, '2 звезды'
        THREE = 3, '3 звезды'
        FOUR = 4, '4 звезды'
        FIVE = 5, '5 звезд'
    
    name = models.CharField(
        max_length=100,
        verbose_name='Имя клиента',
        help_text='Введите ваше имя'
    )
    car = models.CharField(
        max_length=100,
        verbose_name='Автомобиль',
        help_text='Марка и модель автомобиля'
    )
    rating = models.IntegerField(
        choices=Rating.choices,
        verbose_name='Рейтинг',
        help_text='Оценка от 1 до 5 звезд'
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Текст отзыва',
        help_text='Опишите ваши впечатления'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликован',
        help_text='Отзыв будет виден только после модерации'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_published', '-created_at']),
        ]

    def __str__(self) -> str:
        return f'{self.name} - {self.car} ({self.rating} звезд)'

