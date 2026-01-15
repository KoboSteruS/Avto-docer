"""
Админка для управления контент-блоками
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from core.models import ContentBlock


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    """
    Админка для управления контент-блоками.
    Удобный интерфейс с группировкой по страницам и поиском.
    """
    list_display = ['page', 'block_key', 'description', 'get_preview', 'is_html', 'updated_at']
    list_filter = ['page', 'is_html', 'created_at', 'updated_at']
    search_fields = ['block_key', 'description', 'content']
    list_editable = ['is_html']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('page', 'block_key', 'description')
        }),
        ('Содержимое', {
            'fields': ('content', 'is_html'),
            'description': 'Введите текст содержимого. Если включен HTML, можно использовать HTML-теги.'
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_preview(self, obj):
        """Превью содержимого в списке"""
        if not obj.content:
            return format_html('<span style="color: #999;">(пусто)</span>')
        
        preview = obj.content[:80].replace('\n', ' ')
        if len(obj.content) > 80:
            preview += '...'
        
        # Показываем HTML-теги, если они есть
        if obj.is_html:
            preview = format_html(
                '<span style="color: #28a745;">[HTML]</span> {}',
                preview
            )
        
        return mark_safe(preview)
    get_preview.short_description = 'Превью'
    get_preview.allow_tags = True
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related()
    
    def get_list_display(self, request):
        """Динамическое изменение списка в зависимости от прав"""
        return self.list_display
    
    class Media:
        """Дополнительные стили и скрипты для админки"""
        css = {
            'all': ('admin/css/content_block_admin.css',)
        }
