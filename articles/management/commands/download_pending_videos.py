"""
Django management command для скачивания pending видео через Telethon

Использование:
    python manage.py download_pending_videos
    
    # С лимитом
    python manage.py download_pending_videos --limit 5
    
    # В цикле (для systemd/cron)
    python manage.py download_pending_videos --loop --interval 60
"""
import asyncio
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from loguru import logger
import sys
from pathlib import Path

# Импортируем Telethon worker
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / 'telethon_worker'))

from telethon_worker.worker import TelegramVideoDownloader


class Command(BaseCommand):
    """
    Команда для скачивания pending видео через Telethon
    """
    help = 'Скачивает видео со статусом pending из Telegram через Telethon'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Максимальное количество видео для обработки (по умолчанию 10)'
        )
        parser.add_argument(
            '--loop',
            action='store_true',
            help='Запускать в бесконечном цикле'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Интервал между проверками в секундах (по умолчанию 60)'
        )
    
    def handle(self, *args, **options):
        """Основной метод команды"""
        limit = options['limit']
        loop = options['loop']
        interval = options['interval']
        
        # Создаём один event loop для всего процесса
        try:
            # Пытаемся получить существующий loop
            event_loop = asyncio.get_event_loop()
            if event_loop.is_closed():
                event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(event_loop)
        except RuntimeError:
            # Если нет loop, создаём новый
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)
        
        downloader = TelegramVideoDownloader()
        
        async def run_once():
            """Одна итерация обработки"""
            try:
                await downloader.start()
                await downloader.process_pending_videos(limit=limit)
            finally:
                await downloader.close()
        
        if loop:
            # Бесконечный цикл с одним event loop
            logger.info(f"🔄 Запуск в режиме цикла (интервал: {interval} сек)")
            try:
                while True:
                    try:
                        event_loop.run_until_complete(run_once())
                        logger.info(f"⏳ Ожидание {interval} секунд до следующей проверки...")
                        time.sleep(interval)
                    except KeyboardInterrupt:
                        logger.info("🛑 Остановка по запросу пользователя")
                        break
                    except Exception as e:
                        logger.error(f"❌ Ошибка в цикле: {e}")
                        logger.exception(e)
                        time.sleep(interval)
            finally:
                # Закрываем клиент перед выходом
                try:
                    event_loop.run_until_complete(downloader.close())
                except:
                    pass
                event_loop.close()
        else:
            # Одноразовый запуск
            try:
                event_loop.run_until_complete(run_once())
            finally:
                event_loop.close()

