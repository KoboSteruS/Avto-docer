"""
Модель для отслеживания синхронизации с Telegram
"""
from django.db import models
from core.models import BaseModel


class TelegramSync(BaseModel):
    """
    Модель для отслеживания последнего синхронизированного поста из Telegram канала.
    
    Хранит информацию о последнем обработанном посте для каждого канала,
    чтобы избежать дубликатов при перезапуске бота.
    
    Attributes:
        channel_id: ID или username канала (например, @avto_decor_news или -1001234567890)
        last_message_id: ID последнего обработанного сообщения
        last_post_date: Дата последнего обработанного поста
        last_update_id: ID последнего update от Telegram API (для offset)
        posts_processed: Количество обработанных постов
        is_active: Активна ли синхронизация для этого канала
    """
    channel_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='ID канала',
        help_text='ID или username канала (например, @avto_decor_news)'
    )
    last_message_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='ID последнего сообщения',
        help_text='ID последнего обработанного сообщения в канале'
    )
    last_post_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата последнего поста',
        help_text='Дата и время последнего обработанного поста'
    )
    last_update_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='ID последнего update',
        help_text='ID последнего update от Telegram API (для offset)'
    )
    posts_processed = models.PositiveIntegerField(
        default=0,
        verbose_name='Обработано постов',
        help_text='Общее количество обработанных постов из этого канала'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Активна ли синхронизация для этого канала'
    )
    
    class Meta:
        verbose_name = 'Синхронизация с Telegram'
        verbose_name_plural = 'Синхронизации с Telegram'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['channel_id', 'is_active']),
            models.Index(fields=['last_post_date']),
        ]
    
    def __str__(self) -> str:
        return f'{self.channel_id} - {self.posts_processed} постов'
    
    @classmethod
    def get_or_create_sync(cls, channel_id: str):
        """
        Получить или создать запись синхронизации для канала
        
        Args:
            channel_id: ID или username канала
        
        Returns:
            TelegramSync: Объект синхронизации
        """
        sync, created = cls.objects.get_or_create(
            channel_id=channel_id,
            defaults={'is_active': True}
        )
        return sync
    
    def should_process_message(self, message_id: int, post_date=None) -> bool:
        """
        Проверить, нужно ли обрабатывать сообщение
        
        Args:
            message_id: ID сообщения
            post_date: Дата поста (datetime)
        
        Returns:
            bool: True если нужно обработать, False если уже обработано
        """
        # Если нет последнего ID - обрабатываем
        if not self.last_message_id:
            return True
        
        # Проверяем по ID сообщения
        if message_id <= self.last_message_id:
            return False
        
        # Дополнительно проверяем по дате (если указана)
        if post_date and self.last_post_date:
            if post_date <= self.last_post_date:
                return False
        
        return True
    
    def update_last_message(self, message_id: int, post_date=None, update_id=None):
        """
        Обновить информацию о последнем обработанном сообщении
        
        Args:
            message_id: ID сообщения
            post_date: Дата поста (datetime)
            update_id: ID update от Telegram API
        """
        # Обновляем только если новое сообщение позже предыдущего
        if not self.last_message_id or message_id > self.last_message_id:
            self.last_message_id = message_id
        
        if post_date:
            if not self.last_post_date or post_date > self.last_post_date:
                self.last_post_date = post_date
        
        if update_id:
            if not self.last_update_id or update_id > self.last_update_id:
                self.last_update_id = update_id
        
        self.posts_processed += 1
        self.save(update_fields=['last_message_id', 'last_post_date', 'last_update_id', 'posts_processed', 'updated_at'])
    
    def reset_sync(self):
        """Сбросить синхронизацию (начать заново)"""
        self.last_message_id = None
        self.last_post_date = None
        self.last_update_id = None
        self.posts_processed = 0
        self.save()
