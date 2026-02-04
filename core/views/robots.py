"""
View для отдачи robots.txt
"""
from django.http import HttpResponse
from django.conf import settings
from pathlib import Path


def robots_view(request):
    """
    Отдаёт robots.txt файл
    """
    robots_path = Path(settings.BASE_DIR) / 'static' / 'robots.txt'
    
    try:
        with open(robots_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        # Если файл не найден, возвращаем базовый robots.txt
        content = """User-agent: *
Allow: /

# Sitemap
Sitemap: https://www.avto-decor.com/sitemap.xml

# Запрещаем индексацию админки
Disallow: /admin/
Disallow: /admin
"""
    
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    # Кешируем на 1 день
    response['Cache-Control'] = 'public, max-age=86400'
    return response
