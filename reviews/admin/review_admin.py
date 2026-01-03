"""
Админка для модели Review
"""
from django.contrib import admin
from reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Админка для управления отзывами
    
    Позволяет:
    - Просматривать список отзывов
    - Редактировать отзывы
    - Публиковать/скрывать отзывы
    - Фильтровать по статусу публикации и рейтингу
    """
    list_display = [
        'name',
        'car',
        'rating',
        'is_published',
        'created_at',
    ]
    list_filter = [
        'is_published',
        'rating',
        'created_at',
    ]
    search_fields = [
        'name',
        'car',
        'text',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'car', 'rating', 'text')
        }),
        ('Статус', {
            'fields': ('is_published',)
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_editable = ['is_published']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    actions = ['publish_reviews', 'unpublish_reviews']
    
    def publish_reviews(self, request, queryset):
        """
        Действие для массовой публикации отзывов
        """
        updated = queryset.update(is_published=True)
        self.message_user(
            request,
            f'{updated} отзыв(ов) опубликовано.'
        )
    publish_reviews.short_description = 'Опубликовать выбранные отзывы'
    
    def unpublish_reviews(self, request, queryset):
        """
        Действие для массового снятия с публикации отзывов
        """
        updated = queryset.update(is_published=False)
        self.message_user(
            request,
            f'{updated} отзыв(ов) снято с публикации.'
        )
    unpublish_reviews.short_description = 'Снять с публикации выбранные отзывы'

