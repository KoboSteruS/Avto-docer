"""
Админка для модели Service
"""
from django.contrib import admin
from django.utils.html import format_html
from services.models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Админка для управления услугами
    
    Позволяет:
    - Просматривать список услуг
    - Редактировать услуги
    - Управлять порядком сортировки
    - Активировать/деактивировать услуги
    """
    list_display = [
        'title',
        'slug',
        'order',
        'is_active',
        'image_preview',
        'created_at',
    ]
    list_filter = [
        'is_active',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'title',
        'slug',
        'description',
        'short_description',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'image_preview',
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'is_active', 'order')
        }),
        ('Описания', {
            'fields': ('short_description', 'description', 'features', 'content')
        }),
        ('Изображение', {
            'fields': ('image', 'image_preview')
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_editable = ['order', 'is_active']
    ordering = ['order', 'title']
    prepopulated_fields = {'slug': ('title',)}
    
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
    
    actions = ['activate_services', 'deactivate_services']
    
    def activate_services(self, request, queryset):
        """
        Действие для массовой активации услуг
        """
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} услуг(и) активировано.'
        )
    activate_services.short_description = 'Активировать выбранные услуги'
    
    def deactivate_services(self, request, queryset):
        """
        Действие для массовой деактивации услуг
        """
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} услуг(и) деактивировано.'
        )
    deactivate_services.short_description = 'Деактивировать выбранные услуги'

