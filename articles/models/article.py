"""
Модель статьи
"""
import re
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from core.models import BaseModel


class Article(BaseModel):
    """
    Модель статьи/поста в блоге.
    
    Attributes:
        title: Заголовок статьи
        slug: URL-слаг (автогенерируется из title)
        content: Содержимое статьи (HTML)
        image: Главное изображение статьи
        video_url: URL видео (YouTube, Vimeo или прямой файл)
        is_published: Флаг публикации
        views: Количество просмотров
    """
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок',
        help_text='Заголовок статьи'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='URL-слаг',
        help_text='Автоматически генерируется из заголовка'
    )
    content = models.TextField(
        verbose_name='Содержимое',
        help_text='Введите текст статьи. Можно использовать HTML для форматирования (см. инструкцию выше).'
    )
    image = models.ImageField(
        upload_to='articles/',
        blank=True,
        null=True,
        verbose_name='Главное изображение',
        help_text='Главное изображение статьи (будет показано вверху)'
    )
    video_file = models.FileField(
        upload_to='articles/videos/',
        blank=True,
        null=True,
        verbose_name='Видео файл',
        help_text='Загрузите видео файл (MP4, MOV, AVI и т.д.). Если указано, будет показано вместо изображения'
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL видео',
        help_text='Или укажите ссылку на видео (YouTube, Vimeo или прямой файл). Если указано и файл, и URL, приоритет у файла'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано',
        help_text='Статья будет видна только после публикации'
    )
    views = models.PositiveIntegerField(
        default=0,
        verbose_name='Просмотры',
        help_text='Количество просмотров статьи'
    )

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        """Автоматическая генерация slug из title"""
        # Генерируем slug если его нет
        if not self.slug or self.slug.strip() == '':
            self.slug = slugify(self.title)
            # Если slug все еще пустой (например, title содержит только спецсимволы)
            if not self.slug or self.slug.strip() == '':
                import time
                self.slug = f'article-{int(time.time())}'
        
        # Сохраняем первый раз
        super().save(*args, **kwargs)
        
        # После сохранения проверяем уникальность и обновляем если нужно
        if self.slug:
            # Если slug не уникален, добавляем ID
            if Article.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f'{self.slug}-{self.id}'
                super().save(update_fields=['slug'])
    
    def get_absolute_url(self):
        """URL для детальной страницы статьи"""
        return reverse('articles:detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Увеличить счетчик просмотров"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def is_youtube_url(self):
        """Проверка, является ли URL YouTube"""
        return self.video_url and ('youtube.com' in self.video_url or 'youtu.be' in self.video_url)
    
    def is_vimeo_url(self):
        """Проверка, является ли URL Vimeo"""
        return self.video_url and 'vimeo.com' in self.video_url
    
    def has_video(self):
        """Проверка, есть ли видео (файл или URL)"""
        return bool(self.video_file or self.video_url)
    
    def get_video_url(self):
        """Получить URL видео (приоритет у файла)"""
        if self.video_file:
            return self.video_file.url
        return self.video_url
    
    def get_video_embed_url(self):
        """Получить embed URL для видео (только для YouTube/Vimeo)"""
        if not self.video_url:
            return None
        
        if 'youtube.com' in self.video_url or 'youtu.be' in self.video_url:
            # YouTube
            if 'youtu.be' in self.video_url:
                video_id = self.video_url.split('/')[-1].split('?')[0]
            else:
                video_id = self.video_url.split('v=')[1].split('&')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        elif 'vimeo.com' in self.video_url:
            # Vimeo
            video_id = self.video_url.split('/')[-1]
            return f'https://player.vimeo.com/video/{video_id}'
        
        return None  # Для прямых ссылок на файлы используем video_file
    
    def get_plain_text(self, max_length=150):
        """Получить текст без HTML тегов для превью"""
        # Удаляем HTML теги
        text = re.sub(r'<[^>]+>', '', self.content)
        # Удаляем лишние пробелы
        text = ' '.join(text.split())
        # Обрезаем до нужной длины
        if len(text) > max_length:
            text = text[:max_length] + '...'
        return text
