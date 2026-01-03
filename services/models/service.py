"""
Модель услуги
"""
from django.db import models
from django.utils.text import slugify
from core.models import BaseModel


class Service(BaseModel):
    """
    Модель услуги студии
    
    Attributes:
        title: Название услуги
        slug: URL-путь услуги (уникальный)
        short_description: Краткое описание для карточек
        description: Полное описание услуги
        image: Изображение услуги
        content: Дополнительный контент (HTML поддерживается)
        features: Список включенных услуг (каждая с новой строки)
        order: Порядок сортировки
        is_active: Флаг активности услуги
    """
    title = models.CharField(
        max_length=200,
        verbose_name='Название услуги',
        help_text='Полное название услуги'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='URL-путь',
        help_text='Уникальный URL-путь для услуги (например: avtotyuning)'
    )
    short_description = models.TextField(
        max_length=500,
        verbose_name='Краткое описание',
        help_text='Краткое описание для карточек на главной странице'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Полное описание услуги'
    )
    image = models.ImageField(
        upload_to='services/',
        verbose_name='Изображение',
        help_text='Основное изображение услуги',
        blank=True,
        null=True
    )
    content = models.TextField(
        blank=True,
        null=True,
        verbose_name='Дополнительный контент',
        help_text='Дополнительный контент (HTML поддерживается)'
    )
    features = models.TextField(
        blank=True,
        null=True,
        verbose_name='Включает (список услуг)',
        help_text='Список включенных услуг, каждая услуга с новой строки'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок сортировки',
        help_text='Чем меньше число, тем выше услуга в списке'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Показывать услугу на сайте'
    )

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        """
        Автоматическое создание slug из названия, если не указан
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_features_list(self):
        """
        Возвращает список включенных услуг как список строк
        """
        if not self.features:
            return []
        return [line.strip() for line in self.features.split('\n') if line.strip()]
