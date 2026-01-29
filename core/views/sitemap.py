"""
View для генерации sitemap.xml
"""
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from services.models import Service
from works.models import Category
from articles.models import Article


def sitemap_view(request):
    """
    Генерирует sitemap.xml со всеми страницами сайта
    """
    base_url = 'https://www.avto-decor.com'
    
    # Статические страницы
    static_pages = [
        {'loc': '', 'changefreq': 'daily', 'priority': '1.0'},
        {'loc': '/o-studii/', 'changefreq': 'monthly', 'priority': '0.8'},
        {'loc': '/uslugi/', 'changefreq': 'weekly', 'priority': '0.9'},
        {'loc': '/nashi-raboty/', 'changefreq': 'weekly', 'priority': '0.9'},
        {'loc': '/otzyvy/', 'changefreq': 'weekly', 'priority': '0.8'},
        {'loc': '/kontakty/', 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': '/stati/', 'changefreq': 'daily', 'priority': '0.9'},
        {'loc': '/privacy/', 'changefreq': 'yearly', 'priority': '0.5'},
    ]
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Добавляем статические страницы
    for page in static_pages:
        lastmod = timezone.now().strftime('%Y-%m-%d')
        xml.append('  <url>')
        xml.append(f'    <loc>{base_url}{page["loc"]}</loc>')
        xml.append(f'    <lastmod>{lastmod}</lastmod>')
        xml.append(f'    <changefreq>{page["changefreq"]}</changefreq>')
        xml.append(f'    <priority>{page["priority"]}</priority>')
        xml.append('  </url>')
    
    # Добавляем услуги
    services = Service.objects.filter(is_active=True)
    for service in services:
        lastmod = service.updated_at.strftime('%Y-%m-%d')
        xml.append('  <url>')
        xml.append(f'    <loc>{base_url}/uslugi/{service.slug}/</loc>')
        xml.append(f'    <lastmod>{lastmod}</lastmod>')
        xml.append('    <changefreq>monthly</changefreq>')
        xml.append('    <priority>0.8</priority>')
        xml.append('  </url>')
    
    # Добавляем категории работ
    categories = Category.objects.filter(is_active=True)
    for category in categories:
        lastmod = category.updated_at.strftime('%Y-%m-%d')
        xml.append('  <url>')
        xml.append(f'    <loc>{base_url}/nashi-raboty/{category.slug}/</loc>')
        xml.append(f'    <lastmod>{lastmod}</lastmod>')
        xml.append('    <changefreq>monthly</changefreq>')
        xml.append('    <priority>0.7</priority>')
        xml.append('  </url>')
    
    # Добавляем статьи
    articles = Article.objects.filter(is_published=True)
    for article in articles:
        lastmod = article.updated_at.strftime('%Y-%m-%d')
        xml.append('  <url>')
        xml.append(f'    <loc>{base_url}/stati/{article.slug}/</loc>')
        xml.append(f'    <lastmod>{lastmod}</lastmod>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.8</priority>')
        xml.append('  </url>')
    
    xml.append('</urlset>')
    
    response = HttpResponse('\n'.join(xml), content_type='application/xml')
    return response

