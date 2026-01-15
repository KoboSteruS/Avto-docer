"""
Template tags для работы с контент-блоками
"""
from django import template
from django.utils.safestring import mark_safe
from django.core.cache import cache
from core.models import ContentBlock

register = template.Library()


def get_cache_key(page, block_key):
    """Генерация ключа кэша для контент-блока"""
    return f'content_block:{page}:{block_key}'


@register.simple_tag
def get_content(page, block_key, default=''):
    """
    Получить содержимое контент-блока.
    
    Args:
        page: Страница (например, 'home', 'about')
        block_key: Ключ блока (например, 'hero_title', 'about_text')
        default: Значение по умолчанию, если блок не найден
    
    Returns:
        str: Содержимое блока или значение по умолчанию
    """
    cache_key = get_cache_key(page, block_key)
    
    # Пытаемся получить из кэша
    cached_content = cache.get(cache_key)
    if cached_content is not None:
        if isinstance(cached_content, dict) and cached_content.get('is_html'):
            return mark_safe(cached_content['content'])
        return cached_content
    
    # Если нет в кэше, получаем из БД
    try:
        block = ContentBlock.objects.get(page=page, block_key=block_key)
        content = block.content
        
        # Кэшируем результат (на 1 час)
        if block.is_html:
            cache.set(cache_key, {'content': content, 'is_html': True}, 3600)
            return mark_safe(content)
        else:
            cache.set(cache_key, content, 3600)
            return content
    except ContentBlock.DoesNotExist:
        # Кэшируем значение по умолчанию на короткое время (5 минут)
        cache.set(cache_key, default, 300)
        return default


@register.simple_tag
def get_content_safe(page, block_key, default=''):
    """
    Получить содержимое контент-блока с автоматическим экранированием HTML.
    
    Args:
        page: Страница (например, 'home', 'about')
        block_key: Ключ блока (например, 'hero_title', 'about_text')
        default: Значение по умолчанию, если блок не найден
    
    Returns:
        str: Содержимое блока (безопасное, HTML экранирован)
    """
    try:
        block = ContentBlock.objects.get(page=page, block_key=block_key)
        # Всегда возвращаем как безопасный текст (HTML экранируется)
        return block.content
    except ContentBlock.DoesNotExist:
        return default
