"""
Модель контент-блока для управления текстовым содержимым страниц
"""
from django.db import models
from django.utils.html import format_html
from django.core.cache import cache
from .base import BaseModel


class ContentBlock(BaseModel):
    """
    Модель контент-блока для управления текстовым содержимым страниц через админку.
    
    Attributes:
        page: Страница, на которой используется блок (например, 'home', 'about', 'contacts')
        block_key: Уникальный ключ блока на странице (например, 'hero_title', 'about_text')
        content: Текст содержимого блока
        is_html: Флаг, разрешающий HTML в содержимом
        description: Описание блока для удобства в админке
    """
    class Page(models.TextChoices):
        """Выбор страницы"""
        HOME = 'home', 'Главная'
        ABOUT = 'about', 'О студии'
        CONTACTS = 'contacts', 'Контакты'
        SERVICES = 'services', 'Услуги'
        WORKS = 'works', 'Наши работы'
        REVIEWS = 'reviews', 'Отзывы'
    
    page = models.CharField(
        max_length=50,
        choices=Page.choices,
        verbose_name='Страница',
        help_text='Выберите страницу, на которой используется этот блок'
    )
    block_key = models.CharField(
        max_length=100,
        verbose_name='Ключ блока',
        help_text='Уникальный ключ блока на странице (например: hero_title, about_text)'
    )
    content = models.TextField(
        verbose_name='Содержимое',
        help_text='Текст содержимого блока. Можно использовать HTML, если включена опция ниже'
    )
    is_html = models.BooleanField(
        default=False,
        verbose_name='Разрешить HTML',
        help_text='Если включено, содержимое будет интерпретироваться как HTML'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Описание',
        help_text='Краткое описание блока для удобства в админке (необязательно)'
    )

    class Meta:
        verbose_name = 'Контент-блок'
        verbose_name_plural = 'Контент-блоки'
        unique_together = [['page', 'block_key']]
        ordering = ['page', 'block_key']
        indexes = [
            models.Index(fields=['page', 'block_key']),
        ]

    def __str__(self) -> str:
        """Строковое представление"""
        desc = f' - {self.description}' if self.description else ''
        return f'{self.get_page_display()}: {self.block_key}{desc}'
    
    def get_preview(self) -> str:
        """Получить превью содержимого для админки"""
        preview = self.content[:100]
        if len(self.content) > 100:
            preview += '...'
        return format_html('<span style="color: #666;">{}</span>', preview)
    
    def save(self, *args, **kwargs):
        """Переопределяем save для очистки кэша при сохранении"""
        # Очищаем кэш для этого блока
        cache_key = f'content_block:{self.page}:{self.block_key}'
        cache.delete(cache_key)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Переопределяем delete для очистки кэша при удалении"""
        # Очищаем кэш для этого блока
        cache_key = f'content_block:{self.page}:{self.block_key}'
        cache.delete(cache_key)
        super().delete(*args, **kwargs)