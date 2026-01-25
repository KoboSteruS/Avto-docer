"""
View для проксирования видео из Telegram
Позволяет стримить видео любого размера без скачивания на сервер
"""
import os
import requests
from django.http import StreamingHttpResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from loguru import logger
import logging

from articles.models import Article

# Используем стандартный Django logger вместо loguru для production
django_logger = logging.getLogger(__name__)


@require_http_methods(["GET", "HEAD"])
@cache_page(60 * 60)  # Кешируем на 1 час
def stream_telegram_video(request, article_id):
    """
    Проксирует видео из Telegram для отображения на сайте
    
    Args:
        request: HTTP запрос
        article_id: UUID статьи
        
    Returns:
        StreamingHttpResponse с видео контентом
    """
    try:
        # Получаем статью
        article = Article.objects.get(id=article_id, is_published=True)
        
        # Проверяем наличие video_url (там храним file_id)
        if not article.video_url:
            django_logger.warning(f"Статья {article_id} не содержит video_url (file_id)")
            raise Http404("Видео не найдено")
        
        file_id = article.video_url
        # Пытаемся получить токен из разных источников
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not bot_token:
            django_logger.error("TELEGRAM_BOT_TOKEN не найден в окружении")
            django_logger.error(f"Доступные переменные: {list(os.environ.keys())[:10]}")
            return HttpResponse("Ошибка конфигурации сервера", status=500)
        
        # Получаем информацию о файле через Bot API
        file_info_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
        file_info_response = requests.get(file_info_url, timeout=10)
        
        if file_info_response.status_code != 200:
            django_logger.error(f"Не удалось получить info для file_id={file_id}: {file_info_response.text}")
            raise Http404("Видео недоступно")
        
        file_data = file_info_response.json()
        
        if not file_data.get('ok'):
            django_logger.error(f"Telegram API вернул ошибку: {file_data}")
            raise Http404("Видео недоступно")
        
        file_path = file_data['result']['file_path']
        
        # Формируем URL для скачивания
        video_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        
        django_logger.info(f"Проксируем видео для статьи {article_id}, file_id={file_id}")
        
        # Стримим видео
        response = requests.get(video_url, stream=True, timeout=30)
        
        if response.status_code != 200:
            django_logger.error(f"Не удалось скачать видео: {response.status_code}")
            raise Http404("Видео недоступно")
        
        # Определяем MIME тип
        content_type = response.headers.get('Content-Type', 'video/mp4')
        content_length = response.headers.get('Content-Length')
        
        # Создаём streaming response
        def file_iterator(response_obj, chunk_size=8192):
            """Генератор для потоковой передачи данных"""
            for chunk in response_obj.iter_content(chunk_size=chunk_size):
                if chunk:
                    yield chunk
        
        streaming_response = StreamingHttpResponse(
            file_iterator(response),
            content_type=content_type
        )
        
        if content_length:
            streaming_response['Content-Length'] = content_length
        
        # Заголовки для корректного воспроизведения
        streaming_response['Accept-Ranges'] = 'bytes'
        streaming_response['Cache-Control'] = 'public, max-age=3600'
        
        return streaming_response
        
    except Article.DoesNotExist:
        django_logger.warning(f"Статья {article_id} не найдена")
        raise Http404("Статья не найдена")
    except requests.RequestException as e:
        django_logger.error(f"Ошибка при запросе к Telegram API: {e}")
        return HttpResponse("Ошибка при получении видео", status=502)
    except Exception as e:
        django_logger.error(f"Неожиданная ошибка при проксировании видео: {e}")
        django_logger.exception(e)  # Полный traceback
        return HttpResponse("Внутренняя ошибка сервера", status=500)
