"""
Админка для модели ServiceImage
"""
from django.contrib import admin
from django.utils.html import format_html
from services.models import ServiceImage


class ServiceImageInline(admin.TabularInline):
    """
    Inline для добавления дополнительных изображений в админке услуги
    """
    model = ServiceImage
    extra = 1
    fields = ('image', 'image_preview', 'caption', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        """
        Превью изображения в inline
        """
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.image.url
            )
        return 'Загрузите изображение'
    image_preview.short_description = 'Превью'


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    """
    Админка для управления дополнительными изображениями услуг
    """
    list_display = [
        'service',
        'image_preview',
        'caption',
        'order',
        'created_at',
    ]
    list_filter = [
        'service',
        'created_at',
    ]
    search_fields = [
        'service__title',
        'caption',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'image_preview',
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': ('service', 'image', 'image_preview', 'caption', 'order')
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['service', 'order', 'created_at']
    
    def image_preview(self, obj):
        """
        Превью изображения в админке
        """
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.image.url
            )
        return 'Нет изображения'
    image_preview.short_description = 'Превью'

