"""
Модели articles приложения
"""
from .article import Article
from .article_image import ArticleImage
from .telegram_sync import TelegramSync

__all__ = ['Article', 'ArticleImage', 'TelegramSync']
