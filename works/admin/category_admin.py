"""
Админка для модели Category
"""
from django.contrib import admin
from django.utils.html import format_html
from works.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Админка для управления категориями работ
    """
    list_display = [
        'name',
        'slug',
        'order',
        'works_count',
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
        'name',
        'slug',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'image_preview',
        'works_count',
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'is_active', 'order')
        }),
        ('Изображение', {
            'fields': ('image', 'image_preview')
        }),
        ('Системная информация', {
            'fields': ('id', 'works_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']
    prepopulated_fields = {'slug': ('name',)}
    
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
    
    def works_count(self, obj):
        """
        Количество работ в категории
        """
        return obj.get_works_count()
    works_count.short_description = 'Количество работ'
    
    actions = ['activate_categories', 'deactivate_categories']
    
    def activate_categories(self, request, queryset):
        """
        Действие для массовой активации категорий
        """
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} категорий(и) активировано.'
        )
    activate_categories.short_description = 'Активировать выбранные категории'
    
    def deactivate_categories(self, request, queryset):
        """
        Действие для массовой деактивации категорий
        """
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} категорий(и) деактивировано.'
        )
    deactivate_categories.short_description = 'Деактивировать выбранные категории'

