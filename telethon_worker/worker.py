"""
Telethon worker для скачивания больших видео из Telegram каналов

Использование:
    python telethon_worker/worker.py
    
Или через Django management command:
    python manage.py download_pending_videos
"""
import os
import sys
import asyncio
from pathlib import Path

# Добавляем путь к проекту Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avto_decor.settings.development')
import django
django.setup()

from telethon import TelegramClient
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from loguru import logger
from django.conf import settings
from asgiref.sync import sync_to_async
from articles.models import Article


# Telegram API credentials (из my.telegram.org)
API_ID = 39517977
API_HASH = "5900eda1c27150d65511553695b4d58f"
SESSION_NAME = str(BASE_DIR / "telethon_worker" / "session")

# Директория для скачивания видео
DOWNLOAD_DIR = BASE_DIR / "media" / "articles" / "videos"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


class TelegramVideoDownloader:
    """
    Класс для скачивания видео из Telegram через Telethon
    """
    
    def __init__(self):
        # Создаём директорию для session если её нет
        session_dir = Path(SESSION_NAME).parent
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Используем loop=None чтобы Telethon использовал текущий event loop
        self.client = TelegramClient(
            SESSION_NAME,
            API_ID,
            API_HASH,
            loop=None  # Используем текущий event loop
        )
    
    async def start(self):
        """
        Запуск клиента Telethon
        При первом запуске запросит номер телефона и код
        """
        await self.client.start()
        logger.info("✅ Telethon клиент запущен")
    
    async def download_video(self, article_id: int) -> bool:
        """
        Скачивает видео для статьи
        
        Args:
            article_id: ID статьи
            
        Returns:
            True если успешно, False если ошибка
        """
        # Получаем статью через sync_to_async
        def get_article(article_id):
            return Article.objects.get(id=article_id)
        
        article = await sync_to_async(get_article)(article_id)
        
        # Получаем данные из статьи (синхронно, т.к. article уже получен)
        def get_article_data(article_obj):
            return article_obj.telegram_channel_username, article_obj.telegram_message_id
        
        channel_username, message_id = await sync_to_async(get_article_data)(article)
        
        if not channel_username or not message_id:
            logger.error(f"❌ Статья {article_id} не содержит данных Telegram")
            await sync_to_async(setattr)(article, 'video_status', 'error')
            await sync_to_async(article.save)()
            return False
        
        try:
            
            # Обновляем статус
            await sync_to_async(setattr)(article, 'video_status', 'downloading')
            await sync_to_async(article.save)()
            
            channel = channel_username.lstrip('@')
            
            logger.info(f"📥 Скачиваю видео для статьи {article_id}")
            logger.info(f"   Канал: @{channel}, Message ID: {message_id}")
            
            # Получаем сообщение через get_messages
            messages = await self.client.get_messages(
                channel,
                ids=message_id
            )
            
            # get_messages возвращает список или одно сообщение
            if isinstance(messages, list):
                if not messages:
                    raise Exception(f"Сообщение {message_id} не найдено в канале @{channel}")
                msg = messages[0]
            else:
                if not messages:
                    raise Exception(f"Сообщение {message_id} не найдено в канале @{channel}")
                msg = messages
            
            # Проверяем наличие видео
            if not hasattr(msg, 'media') or not msg.media:
                raise Exception("В сообщении нет медиа")
            
            # Скачиваем видео
            file_path = await self.client.download_media(
                msg.media,
                file=str(DOWNLOAD_DIR)
            )
            
            if not file_path:
                raise Exception("Не удалось скачать файл")
            
            logger.info(f"✅ Видео скачано: {file_path}")
            
            # Сохраняем файл в Django (синхронная операция)
            def save_video_file(article_obj, file_path_str):
                with open(file_path_str, 'rb') as f:
                    file_name = Path(file_path_str).name
                    article_obj.video_file.save(
                        file_name,
                        f,
                        save=True
                    )
                # Удаляем временный файл
                os.remove(file_path_str)
                # Обновляем статус
                article_obj.video_status = 'ready'
                article_obj.save()
            
            await sync_to_async(save_video_file)(article, str(file_path))
            
            logger.info(f"✅ Статья {article_id} обновлена, видео готово")
            return True
            
        except FloodWaitError as e:
            logger.warning(f"⏳ FloodWait: нужно подождать {e.seconds} секунд")
            await sync_to_async(setattr)(article, 'video_status', 'pending')  # Возвращаем в очередь
            await sync_to_async(article.save)()
            return False
            
        except SessionPasswordNeededError:
            logger.error("❌ Требуется пароль двухфакторной аутентификации")
            logger.error("   Настройте 2FA в настройках Telegram или отключите его")
            await sync_to_async(setattr)(article, 'video_status', 'error')
            await sync_to_async(article.save)()
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка при скачивании видео для статьи {article_id}: {e}")
            logger.exception(e)
            await sync_to_async(setattr)(article, 'video_status', 'error')
            await sync_to_async(article.save)()
            return False
    
    async def process_pending_videos(self, limit: int = 10):
        """
        Обрабатывает все статьи со статусом 'pending'
        
        Args:
            limit: Максимальное количество видео для обработки за раз
        """
        # Получаем список ID статей через sync_to_async
        def get_pending_article_ids():
            return list(Article.objects.filter(
                video_status='pending',
                telegram_channel_username__isnull=False,
                telegram_message_id__isnull=False
            ).values_list('id', flat=True)[:limit])
        
        pending_ids = await sync_to_async(get_pending_article_ids)()
        
        if not pending_ids:
            logger.info("ℹ️  Нет видео для скачивания")
            return
        
        logger.info(f"📋 Найдено {len(pending_ids)} видео для скачивания")
        
        for article_id in pending_ids:
            await self.download_video(article_id)
            # Небольшая задержка между запросами
            await asyncio.sleep(2)
    
    async def close(self):
        """Закрытие клиента"""
        await self.client.disconnect()
        logger.info("👋 Telethon клиент отключен")


async def main():
    """
    Основная функция для запуска воркера
    """
    downloader = TelegramVideoDownloader()
    
    try:
        await downloader.start()
        await downloader.process_pending_videos(limit=10)
    finally:
        await downloader.close()


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🎬 TELEGRAM VIDEO DOWNLOADER (Telethon)")
    logger.info("=" * 80)
    logger.info("")
    
    asyncio.run(main())

