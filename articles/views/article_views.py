"""
Views для статей
"""
from django.views.generic import ListView, DetailView
from django.db.models import Q
from articles.models import Article


class ArticleListView(ListView):
    """
    Список всех опубликованных статей
    """
    model = Article
    template_name = 'articles/articles_list.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        """Получить только опубликованные статьи"""
        return Article.objects.filter(is_published=True).order_by('-created_at')


class ArticleDetailView(DetailView):
    """
    Детальная страница статьи
    """
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Получить только опубликованные статьи"""
        return Article.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        """Добавить связанные статьи в контекст"""
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Увеличиваем счетчик просмотров
        article.increment_views()
        
        # Получаем последние статьи (кроме текущей)
        context['related_articles'] = Article.objects.filter(
            is_published=True
        ).exclude(
            id=article.id
        ).order_by('-created_at')[:6]
        
        return context
