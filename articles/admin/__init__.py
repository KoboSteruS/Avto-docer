"""
Админка articles приложения
"""
from .article_admin import ArticleAdmin
from .telegram_sync_admin import TelegramSyncAdmin

__all__ = ['ArticleAdmin', 'TelegramSyncAdmin']
