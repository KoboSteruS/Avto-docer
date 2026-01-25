"""
URL-маршруты для статей
"""
from django.urls import path
from articles.views import ArticleListView, ArticleDetailView, stream_telegram_video

app_name = 'articles'

urlpatterns = [
    path('', ArticleListView.as_view(), name='list'),
    path('video/<uuid:article_id>/', stream_telegram_video, name='video_stream'),
    path('<slug:slug>/', ArticleDetailView.as_view(), name='detail'),
]
