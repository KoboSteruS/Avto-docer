"""
Views для articles приложения
"""
from .article_views import ArticleListView, ArticleDetailView
from .video_proxy import stream_telegram_video

__all__ = ['ArticleListView', 'ArticleDetailView', 'stream_telegram_video']
