"""
Админка для управления синхронизацией с Telegram
"""
from django.contrib import admin
from django.utils.html import format_html
from articles.models import TelegramSync


@admin.register(TelegramSync)
class TelegramSyncAdmin(admin.ModelAdmin):
    """
    Админка для управления синхронизацией с Telegram каналами.
    Позволяет отслеживать и управлять синхронизацией новостей.
    """
    list_display = [
        'channel_id', 
        'posts_processed', 
        'last_post_date_formatted',
        'last_message_id', 
        'is_active_badge',
        'updated_at'
    ]
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['channel_id']
    readonly_fields = [
        'id', 
        'created_at', 
        'updated_at', 
        'posts_processed',
        'last_message_id',
        'last_post_date',
        'last_update_id'
    ]
    
    fieldsets = (
        ('Информация о канале', {
            'fields': ('channel_id', 'is_active')
        }),
        ('Статистика синхронизации', {
            'fields': (
                'posts_processed',
                'last_message_id',
                'last_post_date',
                'last_update_id'
            )
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['reset_sync', 'activate_sync', 'deactivate_sync']
    
    def last_post_date_formatted(self, obj):
        """Форматированная дата последнего поста"""
        if obj.last_post_date:
            return obj.last_post_date.strftime('%d.%m.%Y %H:%M:%S')
        return format_html('<span style="color: #999;">Нет данных</span>')
    last_post_date_formatted.short_description = 'Последний пост'
    
    def is_active_badge(self, obj):
        """Бейдж активности"""
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Активна</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">✗ Неактивна</span>'
        )
    is_active_badge.short_description = 'Статус'
    
    def reset_sync(self, request, queryset):
        """Сбросить синхронизацию (начать заново)"""
        for sync in queryset:
            sync.reset_sync()
        self.message_user(
            request, 
            f'Синхронизация сброшена для {queryset.count()} каналов. '
            f'Бот начнёт обрабатывать посты заново.'
        )
    reset_sync.short_description = 'Сбросить синхронизацию (начать заново)'
    
    def activate_sync(self, request, queryset):
        """Активировать синхронизацию"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} каналов.')
    activate_sync.short_description = 'Активировать синхронизацию'
    
    def deactivate_sync(self, request, queryset):
        """Деактивировать синхронизацию"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'Деактивировано {updated} каналов. Бот не будет обрабатывать посты из этих каналов.'
        )
    deactivate_sync.short_description = 'Деактивировать синхронизацию'
