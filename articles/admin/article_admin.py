"""
Админка для управления статьями
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from articles.models import Article, ArticleImage


class ArticleImageInline(admin.TabularInline):
    """
    Inline для управления изображениями статьи
    """
    model = ArticleImage
    extra = 1
    fields = ['image', 'image_preview', 'order', 'caption']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """Превью изображения"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 100px; border-radius: 4px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">Нет изображения</span>')
    image_preview.short_description = 'Превью'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Админка для управления статьями.
    Удобный интерфейс с превью изображений и видео.
    """
    inlines = [ArticleImageInline]
    list_display = ['title', 'slug', 'image_preview', 'video_preview', 'is_published', 'views', 'created_at']
    list_filter = ['is_published', 'created_at', 'updated_at']
    search_fields = ['title', 'slug', 'content']
    list_editable = ['is_published']
    readonly_fields = ['id', 'views', 'created_at', 'updated_at', 'image_preview', 'video_preview']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Убираем обязательные поля
        for field in form.base_fields.values():
            field.required = False
        return form
    
    class Media:
        """Дополнительные стили для админки"""
        css = {
            'all': ('admin/css/article_admin.css',)
        }
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'is_published')
        }),
        ('Содержимое', {
            'fields': ('content',),
            'description': mark_safe('''
                <div style="background: #1f2937; padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #dc2626;">
                    <p style="color: #ffffff; margin: 0 0 12px 0; font-size: 16px; line-height: 1.6;">
                        <strong style="color: #ffffff;">Как редактировать текст:</strong>
                    </p>
                    <p style="color: #ffffff; margin: 0 0 15px 0; font-size: 14px; line-height: 1.7;">
                        Просто введите текст статьи в поле ниже. Можно использовать обычный текст - он будет отображаться нормально.
                    </p>
                    <p style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px; line-height: 1.7;">
                        <strong style="color: #ffffff;">Для дополнительного форматирования используйте HTML:</strong>
                    </p>
                    <ul style="color: #ffffff; margin: 0 0 15px 0; padding-left: 20px; line-height: 2;">
                        <li style="color: #ffffff;">Жирный текст: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;strong&gt;текст&lt;/strong&gt;</code></li>
                        <li style="color: #ffffff;">Курсив: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;em&gt;текст&lt;/em&gt;</code></li>
                        <li style="color: #ffffff;">Заголовок: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;h2&gt;Заголовок&lt;/h2&gt;</code></li>
                        <li style="color: #ffffff;">Список: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;ul&gt;&lt;li&gt;Элемент&lt;/li&gt;&lt;/ul&gt;</code></li>
                        <li style="color: #ffffff;">Изображение: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;img src="URL" alt="Описание" /&gt;</code></li>
                        <li style="color: #ffffff;">Ссылка: <code style="background: #374151; padding: 3px 8px; border-radius: 4px; color: #fbbf24; font-size: 13px;">&lt;a href="URL"&gt;Текст&lt;/a&gt;</code></li>
                    </ul>
                    <p style="color: #d1d5db; margin: 0; font-size: 13px; font-style: italic; border-top: 1px solid #374151; padding-top: 12px;">
                        💡 Совет: HTML не обязателен - можно просто ввести текст, и он будет отображаться нормально.
                    </p>
                </div>
            ''')
        }),
        ('Медиа', {
            'fields': ('image', 'image_preview', 'video_file', 'video_url', 'video_preview'),
            'description': 'Добавьте главное изображение или видео. Можно загрузить видео файл или указать ссылку (YouTube, Vimeo). Если указано и изображение, и видео, будет показано видео. Приоритет у загруженного файла.'
        }),
        ('Статистика', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Превью изображения"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; border-radius: 8px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">Нет изображения</span>')
    image_preview.short_description = 'Превью изображения'
    
    def video_preview(self, obj):
        """Превью видео"""
        if obj.video_file:
            # Загруженный файл
            return format_html(
                '<div style="max-width: 400px;">'
                '<video controls width="100%" style="max-height: 225px;">'
                '<source src="{}" type="video/mp4">'
                'Ваш браузер не поддерживает видео.'
                '</video>'
                '<p style="margin-top: 8px; color: #666; font-size: 12px;">Загруженный файл: {}</p>'
                '</div>',
                obj.video_file.url,
                obj.video_file.name
            )
        elif obj.video_url:
            # URL видео
            if obj.is_youtube_url() or obj.is_vimeo_url():
                embed_url = obj.get_video_embed_url()
                return format_html(
                    '<div style="max-width: 400px;">'
                    '<iframe src="{}" width="100%" height="225" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>'
                    '<p style="margin-top: 8px; color: #666; font-size: 12px;">URL: {}</p>'
                    '</div>',
                    embed_url,
                    obj.video_url
                )
            else:
                return format_html(
                    '<div style="max-width: 400px;">'
                    '<video controls width="100%" style="max-height: 225px;">'
                    '<source src="{}" type="video/mp4">'
                    'Ваш браузер не поддерживает видео.'
                    '</video>'
                    '<p style="margin-top: 8px; color: #666; font-size: 12px;">URL: {}</p>'
                    '</div>',
                    obj.video_url,
                    obj.video_url
                )
        return format_html('<span style="color: #999;">Нет видео</span>')
    video_preview.short_description = 'Превью видео'
    
    actions = ['publish_articles', 'unpublish_articles']
    
    def publish_articles(self, request, queryset):
        """Массовая публикация статей"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} статей опубликовано.')
    publish_articles.short_description = 'Опубликовать выбранные статьи'
    
    def unpublish_articles(self, request, queryset):
        """Массовое снятие с публикации"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} статей снято с публикации.')
    unpublish_articles.short_description = 'Снять с публикации выбранные статьи'
