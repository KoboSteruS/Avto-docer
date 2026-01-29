"""
Контекстный процессор для SEO мета-тегов
"""
from django.conf import settings


def seo_meta(request):
    """
    Добавляет базовые SEO мета-теги в контекст всех шаблонов
    """
    site_url = f"https://www.avto-decor.com"
    site_name = "Avto-Декор"
    default_description = "Профессиональный тюнинг и детейлинг автомобилей в Петрозаводске. Аэрография, аквапринт, перетяжка салона, золочение и другие услуги."
    default_keywords = "тюнинг автомобилей, детейлинг, аэрография, аквапринт, перетяжка салона, золочение, Петрозаводск, автомобильный тюнинг"
    
    # Получаем текущий путь для генерации canonical URL
    canonical_url = f"{site_url}{request.path}"
    
    return {
        'site_url': site_url,
        'site_name': site_name,
        'default_description': default_description,
        'default_keywords': default_keywords,
        'canonical_url': canonical_url,
    }

