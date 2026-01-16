"""
Модель контент-блока для управления текстовым содержимым страниц
"""
from django.db import models
from django.utils.html import format_html
from django.core.cache import cache
from django.utils.text import slugify
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
        help_text='Уникальный ключ блока на странице (генерируется автоматически из описания)',
        db_index=True
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
        help_text='Краткое описание блока для удобства в админке. Ключ блока сгенерируется автоматически из описания.'
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
        if self.description:
            return f'{self.get_page_display()}: {self.description}'
        return f'{self.get_page_display()}: {self.block_key}'
    
    def get_preview(self) -> str:
        """Получить превью содержимого для админки"""
        preview = self.content[:100]
        if len(self.content) > 100:
            preview += '...'
        return format_html('<span style="color: #666;">{}</span>', preview)
    
    def save(self, *args, **kwargs):
        """Переопределяем save для автогенерации ключа и очистки кэша"""
        # Автогенерация ключа из описания, если не указан
        if not self.block_key and self.description:
            self.block_key = slugify(self.description)
            # Ограничиваем длину
            if len(self.block_key) > 100:
                self.block_key = self.block_key[:100]
        
        # Очищаем кэш для этого блока
        if self.block_key:
            cache_key = f'content_block:{self.page}:{self.block_key}'
            cache.delete(cache_key)
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Переопределяем delete для очистки кэша при удалении"""
        # Очищаем кэш для этого блока
        cache_key = f'content_block:{self.page}:{self.block_key}'
        cache.delete(cache_key)
        super().delete(*args, **kwargs)