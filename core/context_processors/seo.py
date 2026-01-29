"""
Контекстный процессор для SEO мета-тегов
"""
import re
from django.conf import settings
from django.urls import resolve


def seo_meta(request):
    """
    Добавляет базовые SEO мета-теги в контекст всех шаблонов
    Определяет описание для каждой страницы автоматически
    """
    site_url = f"https://www.avto-decor.com"
    site_name = "Avto-Декор"
    default_description = "Профессиональный тюнинг и детейлинг автомобилей в Петрозаводске. Аэрография, аквапринт, перетяжка салона, золочение и другие услуги."
    default_keywords = "тюнинг автомобилей, детейлинг, аэрография, аквапринт, перетяжка салона, золочение, Петрозаводск, автомобильный тюнинг"
    
    # Получаем текущий путь для генерации canonical URL
    canonical_url = f"{site_url}{request.path}"
    
    # Определяем описание в зависимости от страницы
    page_description = get_page_description(request, default_description)
    page_keywords = get_page_keywords(request, default_keywords)
    
    return {
        'site_url': site_url,
        'site_name': site_name,
        'default_description': page_description,
        'default_keywords': page_keywords,
        'canonical_url': canonical_url,
    }


def get_page_description(request, default_description):
    """
    Определяет описание для текущей страницы
    """
    try:
        resolver_match = request.resolver_match
        if not resolver_match:
            return default_description
        
        url_name = resolver_match.url_name
        app_name = resolver_match.app_name
        
        # Главная страница
        if url_name == 'home' and app_name == 'core':
            return "Avto-Декор - Профессиональный тюнинг и детейлинг автомобилей в Петрозаводске. Аэрография, аквапринт, перетяжка салона, золочение, шумоизоляция, нанокерамика и другие услуги."
        
        # О студии
        if url_name == 'about' and app_name == 'core':
            return "О студии Avto-Декор - Профессиональный тюнинг и детейлинг автомобилей в Петрозаводске. Опыт работы, команда специалистов, современное оборудование."
        
        # Политика конфиденциальности
        if url_name == 'privacy' and app_name == 'core':
            return "Политика конфиденциальности Avto-Декор - Информация об обработке персональных данных пользователей сайта."
        
        # Список услуг
        if url_name == 'list' and app_name == 'services':
            return "Услуги тюнинга и детейлинга автомобилей в Петрозаводске - Аэрография, аквапринт, перетяжка салона, золочение, шумоизоляция, нанокерамика и другие услуги."
        
        # Детальная страница услуги
        if url_name == 'detail' and app_name == 'services':
            # Получаем услугу из URL
            try:
                from services.models import Service
                slug = resolver_match.kwargs.get('slug')
                if slug:
                    service = Service.objects.filter(slug=slug, is_active=True).only('title', 'short_description', 'description').first()
                else:
                    service = None
            except:
                service = None
            
            if service:
                # Используем short_description или description
                if service.short_description:
                    desc = service.short_description[:160]
                elif service.description:
                    # Убираем HTML теги и обрезаем
                    desc = re.sub(r'<[^>]+>', '', service.description)[:160]
                else:
                    desc = f"{service.title} - Профессиональная услуга тюнинга и детейлинга автомобилей в Петрозаводске."
                
                return f"{desc} | Avto-Декор"
            return default_description
        
        # Список работ
        if url_name == 'list' and app_name == 'works':
            return "Наши работы - Портфолио выполненных проектов по тюнингу и детейлингу автомобилей в Петрозаводске. Аэрография, аквапринт, перетяжка салона и другие услуги."
        
        # Категория работ
        if url_name == 'category' and app_name == 'works':
            # Получаем категорию из URL
            try:
                from works.models import Category
                slug = resolver_match.kwargs.get('slug')
                if slug:
                    category = Category.objects.filter(slug=slug, is_active=True).only('name', 'description').first()
                else:
                    category = None
            except:
                category = None
            
            if category:
                return f"{category.name} - Примеры выполненных работ по тюнингу и детейлингу автомобилей в Петрозаводске. | Avto-Декор"
            return default_description
        
        # Отзывы
        if url_name == 'list' and app_name == 'reviews':
            return "Отзывы клиентов Avto-Декор - Реальные отзывы о работе студии тюнинга и детейлинга автомобилей в Петрозаводске."
        
        # Контакты
        if url_name == 'contacts' and app_name == 'contacts':
            return "Контакты Avto-Декор - Свяжитесь с нами для заказа услуг тюнинга и детейлинга автомобилей в Петрозаводске. Телефон, адрес, режим работы."
        
        # Список статей
        if url_name == 'list' and app_name == 'articles':
            return "Статьи и новости Avto-Декор - Полезная информация о тюнинге и детейлинге автомобилей, новости студии, советы и рекомендации."
        
        # Детальная страница статьи
        if url_name == 'detail' and app_name == 'articles':
            # Получаем статью из URL
            try:
                from articles.models import Article
                slug = resolver_match.kwargs.get('slug')
                if slug:
                    article = Article.objects.filter(slug=slug, is_published=True).only('title', 'content').first()
                else:
                    article = None
            except:
                article = None
            
            if article:
                # Используем get_plain_text для получения текста без HTML
                desc = article.get_plain_text(max_length=160)
                return f"{desc} | Avto-Декор"
            return default_description
        
    except Exception:
        pass
    
    return default_description


def get_page_keywords(request, default_keywords):
    """
    Определяет ключевые слова для текущей страницы
    """
    try:
        resolver_match = request.resolver_match
        if not resolver_match:
            return default_keywords
        
        url_name = resolver_match.url_name
        app_name = resolver_match.app_name
        
        # Для детальных страниц добавляем специфичные ключевые слова
        if url_name == 'detail' and app_name == 'services':
            try:
                from services.models import Service
                slug = resolver_match.kwargs.get('slug')
                if slug:
                    service = Service.objects.filter(slug=slug, is_active=True).only('title').first()
                else:
                    service = None
            except:
                service = None
            
            if service:
                # Добавляем название услуги в ключевые слова
                service_keywords = f"{service.title.lower()}, {default_keywords}"
                return service_keywords
        
        if url_name == 'detail' and app_name == 'articles':
            try:
                from articles.models import Article
                slug = resolver_match.kwargs.get('slug')
                if slug:
                    article = Article.objects.filter(slug=slug, is_published=True).only('title').first()
                else:
                    article = None
            except:
                article = None
            
            if article:
                # Извлекаем ключевые слова из заголовка
                title_words = article.title.lower().split()[:5]
                article_keywords = ", ".join(title_words) + f", {default_keywords}"
                return article_keywords
        
    except Exception:
        pass
    
    return default_keywords

