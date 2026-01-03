"""
Админка для модели Work
"""
from django.contrib import admin
from django.utils.html import format_html
from works.models import Work


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    """
    Админка для управления работами (фотографиями)
    """
    list_display = [
        'image_preview',
        'category',
        'order',
        'is_active',
        'created_at',
    ]
    list_filter = [
        'category',
        'is_active',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'category__name',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'image_preview',
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'image', 'image_preview', 'is_active', 'order')
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_editable = ['order', 'is_active']
    ordering = ['order', '-created_at']
    
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
    
    actions = ['activate_works', 'deactivate_works']
    
    def activate_works(self, request, queryset):
        """
        Действие для массовой активации работ
        """
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} работ(ы) активировано.'
        )
    activate_works.short_description = 'Активировать выбранные работы'
    
    def deactivate_works(self, request, queryset):
        """
        Действие для массовой деактивации работ
        """
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} работ(ы) деактивировано.'
        )
    deactivate_works.short_description = 'Деактивировать выбранные работы'

