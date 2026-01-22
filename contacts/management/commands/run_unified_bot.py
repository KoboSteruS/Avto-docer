"""
Универсальный Telegram-бот: заявки + новости из канала

Объединяет функциональность:
1. Обработка команд пользователей (/start, /help и т.д.)
2. Автоматический сбор новостей из Telegram-канала
"""
import os
import sys
import time
from datetime import datetime
from io import BytesIO
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
from django.utils import timezone
from loguru import logger
import requests
import html

from contacts.utils import SubscribersManager
from articles.models import Article, ArticleImage, TelegramSync


class Command(BaseCommand):
    """
    Универсальный Telegram-бот для обработки заявок и сбора новостей
    
    Функции:
    - Обрабатывает команды пользователей (/start, /stop, /help)
    - Автоматически собирает новости из указанного канала
    - Поддерживает медиа-группы (несколько фото в одном посте)
    - Сохраняет прогресс синхронизации
    
    Использование:
        # Только заявки (как раньше)
        python manage.py run_unified_bot
        
        # Заявки + новости из канала
        python manage.py run_unified_bot --channel @your_channel
        
        # С автопубликацией новостей
        python manage.py run_unified_bot --channel @your_channel --auto-publish
    """
    help = 'Unified Telegram bot: leads + news from channel'
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Таймаут для long polling (по умолчанию 30 секунд)',
        )
        parser.add_argument(
            '--channel',
            type=str,
            help='ID или username канала для новостей (например, @avto_decor_news)',
        )
        parser.add_argument(
            '--auto-publish',
            action='store_true',
            help='Автоматически публиковать новости (по умолчанию черновики)',
        )
    
    def __init__(self):
        super().__init__()
        self.subscribers_manager = SubscribersManager()
        self.media_groups = defaultdict(list)  # Группировка медиа по media_group_id
        self.processed_media_groups = set()  # Обработанные группы
    
    def handle(self, *args, **options):
        """Основной метод команды"""
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '8389210453:AAE0pUO2PflNa8UWqXWRN-SEnf8LvplsdrA')
        api_url = f'https://api.telegram.org/bot{token}'
        timeout = options['timeout']
        channel_id = options.get('channel') or os.environ.get('TELEGRAM_NEWS_CHANNEL')
        auto_publish = options['auto_publish']
        offset = 0
        
        # Режим работы
        news_mode = bool(channel_id)
        
        logger.info('=' * 80)
        logger.info('🤖 УНИВЕРСАЛЬНЫЙ TELEGRAM-БОТ')
        logger.info('=' * 80)
        logger.info(f'Токен: {token[:10]}...')
        logger.info('')
        
        # Проверяем подключение к боту
        try:
            response = requests.get(f'{api_url}/getMe', timeout=10)
            response.raise_for_status()
            bot_info = response.json()
            
            if bot_info.get('ok'):
                bot_username = bot_info['result'].get('username', 'Unknown')
                logger.info(f'✅ Бот подключен: @{bot_username}')
            else:
                logger.error('❌ Ошибка при подключении к боту')
                sys.exit(1)
        except Exception as e:
            logger.error(f'❌ Ошибка при проверке бота: {e}')
            sys.exit(1)
        
        logger.info('')
        logger.info('📋 АКТИВНЫЕ ФУНКЦИИ:')
        logger.info('   ✅ Обработка команд пользователей (/start, /help, и т.д.)')
        logger.info(f'   {"✅" if news_mode else "❌"} Сбор новостей из канала')
        
        if news_mode:
            logger.info('')
            logger.info(f'📢 Канал для новостей: {channel_id}')
            logger.info(f'📝 Режим публикации: {"автоматическая" if auto_publish else "черновики"}')
            
            # Получаем синхронизацию для канала
            sync = TelegramSync.get_or_create_sync(channel_id)
            logger.info('')
            logger.info('📊 Статистика канала:')
            logger.info(f'   Обработано постов: {sync.posts_processed}')
            if sync.last_post_date:
                logger.info(f'   Последний пост: {sync.last_post_date.strftime("%d.%m.%Y %H:%M:%S")}')
                logger.info(f'   ID последнего сообщения: {sync.last_message_id}')
            else:
                logger.info('   Это первый запуск для этого канала')
            
            if sync.last_update_id:
                offset = sync.last_update_id + 1
                logger.info(f'   ♻️  Продолжаем с update_id: {offset}')
        else:
            sync = None
        
        # Подписчики на заявки
        logger.info('')
        logger.info('👥 ПОДПИСЧИКИ НА ЗАЯВКИ:')
        logger.info(f'   Файл: {self.subscribers_manager.subscribers_file}')
        logger.info(f'   Количество: {self.subscribers_manager.get_count()}')
        
        current_subscribers = self.subscribers_manager.get_subscribers()
        if current_subscribers:
            logger.info(f'   Список: {list(current_subscribers)}')
        else:
            logger.info('   ⚠️  Подписчиков нет. Отправьте боту /start для подписки')
        
        logger.info('')
        logger.info('=' * 80)
        logger.info('🚀 БОТ ЗАПУЩЕН')
        logger.info('=' * 80)
        logger.info('Ожидаю обновления...')
        logger.info('Для остановки: Ctrl+C')
        logger.info('')
        
        # Основной цикл polling
        try:
            while True:
                try:
                    # Получаем обновления (и сообщения, и посты из канала)
                    allowed_updates = ['message']
                    if news_mode:
                        allowed_updates.append('channel_post')
                    
                    response = requests.get(
                        f'{api_url}/getUpdates',
                        params={
                            'offset': offset,
                            'timeout': timeout,
                            'allowed_updates': allowed_updates
                        },
                        timeout=timeout + 10
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if not data.get('ok'):
                        logger.error(f'Ошибка API: {data.get("description", "Unknown error")}')
                        time.sleep(5)
                        continue
                    
                    updates = data.get('result', [])
                    
                    for update in updates:
                        offset = update['update_id'] + 1
                        
                        # ОБРАБОТКА СООБЩЕНИЙ ОТ ПОЛЬЗОВАТЕЛЕЙ
                        if 'message' in update:
                            self._handle_user_message(api_url, update['message'])
                        
                        # ОБРАБОТКА ПОСТОВ ИЗ КАНАЛА
                        if news_mode and 'channel_post' in update:
                            self._handle_channel_post(
                                api_url,
                                update['channel_post'],
                                channel_id,
                                auto_publish,
                                sync,
                                update['update_id']
                            )
                    
                    # Задержка если нет обновлений
                    if not updates:
                        time.sleep(1)
                    
                except requests.exceptions.Timeout:
                    # Таймаут - это нормально для long polling
                    continue
                except requests.exceptions.RequestException as e:
                    logger.error(f'Ошибка при получении обновлений: {e}')
                    time.sleep(5)
                except KeyboardInterrupt:
                    logger.info('Получен сигнал остановки. Завершение работы...')
                    break
                except Exception as e:
                    logger.error(f'Неожиданная ошибка: {e}')
                    logger.exception(e)
                    time.sleep(5)
        
        except KeyboardInterrupt:
            logger.info('Бот остановлен')
        except Exception as e:
            logger.error(f'Критическая ошибка: {e}')
            sys.exit(1)
    
    def _handle_user_message(self, api_url: str, message: dict):
        """
        Обрабатывает сообщения от пользователей (команды /start, /help и т.д.)
        
        Args:
            api_url: URL API бота
            message: Объект сообщения от Telegram
        """
        chat_id = message['chat']['id']
        chat_id_str = str(chat_id)
        text = message.get('text', '')
        
        # Игнорируем пересланные сообщения (это для batch_import_posts)
        if 'forward_from_chat' in message or 'forward_origin' in message:
            return
        
        # Обрабатываем команды
        if text.startswith('/start'):
            logger.info(f'📨 /start от chat_id: {chat_id_str}')
            
            is_new = self.subscribers_manager.add_subscriber(chat_id_str)
            current_count = self.subscribers_manager.get_count()
            
            if is_new:
                self._send_message(
                    api_url,
                    chat_id,
                    '✅ Вы успешно подписаны на уведомления о заявках!\n\n'
                    'Теперь все заявки с сайта Avto-Декор будут приходить в этот чат.\n\n'
                    f'Ваш chat_id: <code>{chat_id}</code>\n'
                    f'Всего подписчиков: {current_count}',
                    parse_mode='HTML'
                )
                logger.info(f'   ✅ Новый подписчик: {chat_id_str}. Всего: {current_count}')
            else:
                self._send_message(
                    api_url,
                    chat_id,
                    'Вы уже подписаны на уведомления о заявках.\n\n'
                    f'Ваш chat_id: <code>{chat_id}</code>\n'
                    f'Всего подписчиков: {current_count}',
                    parse_mode='HTML'
                )
        
        elif text.startswith('/stop'):
            removed = self.subscribers_manager.remove_subscriber(chat_id_str)
            
            if removed:
                self._send_message(
                    api_url,
                    chat_id,
                    '❌ Вы отписаны от уведомлений о заявках.\n\n'
                    'Чтобы снова получать уведомления, отправьте /start'
                )
                logger.info(f'📨 Подписчик удален: {chat_id_str}')
            else:
                self._send_message(api_url, chat_id, 'Вы не были подписаны на уведомления.')
        
        elif text.startswith('/help'):
            is_subscribed = self.subscribers_manager.is_subscribed(chat_id_str)
            status = '✅ подписаны' if is_subscribed else '❌ не подписаны'
            
            self._send_message(
                api_url,
                chat_id,
                '🤖 Универсальный бот Avto-Декор\n\n'
                f'Ваш статус: {status}\n\n'
                '📋 Команды:\n'
                '/start - Подписаться на уведомления о заявках\n'
                '/stop - Отписаться от уведомлений\n'
                '/help - Показать эту справку\n'
                '/chat_id - Показать ваш chat_id\n'
                '/status - Показать статус подписки'
            )
        
        elif text.startswith('/chat_id'):
            self._send_message(
                api_url,
                chat_id,
                f'Ваш chat_id: <code>{chat_id}</code>\n\n'
                'Этот ID используется для отправки вам уведомлений.',
                parse_mode='HTML'
            )
        
        elif text.startswith('/status'):
            is_subscribed = self.subscribers_manager.is_subscribed(chat_id_str)
            total_subscribers = self.subscribers_manager.get_count()
            
            if is_subscribed:
                status_text = '✅ Вы подписаны на уведомления о заявках'
            else:
                status_text = '❌ Вы не подписаны\n\nОтправьте /start для подписки'
            
            self._send_message(
                api_url,
                chat_id,
                f'{status_text}\n\n'
                f'Всего подписчиков: {total_subscribers}\n'
                f'Ваш chat_id: <code>{chat_id}</code>',
                parse_mode='HTML'
            )
        
        else:
            # Обычное сообщение - просто подтверждаем
            is_subscribed = self.subscribers_manager.is_subscribed(chat_id_str)
            
            if is_subscribed:
                self._send_message(
                    api_url,
                    chat_id,
                    'Сообщение получено. Вы подписаны на уведомления о заявках.\n\n'
                    'Используйте /help для списка команд.'
                )
            else:
                self._send_message(
                    api_url,
                    chat_id,
                    'Сообщение получено.\n\n'
                    'Чтобы получать уведомления о заявках, отправьте /start'
                )
    
    def _handle_channel_post(
        self,
        api_url: str,
        post: dict,
        channel_id: str,
        auto_publish: bool,
        sync: TelegramSync,
        update_id: int
    ):
        """
        Обрабатывает посты из канала и создаёт новости
        
        Args:
            api_url: URL API бота
            post: Объект поста из канала
            channel_id: ID канала для фильтрации
            auto_publish: Автоматически публиковать новости
            sync: Объект синхронизации
            update_id: ID обновления
        """
        post_channel_id = post.get('chat', {}).get('id')
        message_id = post.get('message_id')
        media_group_id = post.get('media_group_id')
        
        # Получаем дату поста
        post_timestamp = post.get('date')
        post_date = None
        if post_timestamp:
            post_date = timezone.make_aware(datetime.fromtimestamp(post_timestamp))
        
        # Проверяем, что пост из нужного канала
        if channel_id.startswith('@'):
            channel_username = post.get('chat', {}).get('username', '')
            if f'@{channel_username}' != channel_id:
                return
        else:
            if str(post_channel_id) != str(channel_id).replace('@', ''):
                return
        
        # Проверяем, обрабатывали ли уже этот пост
        if not sync.should_process_message(message_id, post_date):
            return
        
        # МЕДИА-ГРУППА: собираем все фото из группы
        if media_group_id:
            # Добавляем в группу
            self.media_groups[media_group_id].append(post)
            
            # Даём время собрать все фото из группы (ждём 2 секунды)
            # Если группа уже обработана - пропускаем
            if media_group_id in self.processed_media_groups:
                return
            
            # Помечаем как обработанную
            self.processed_media_groups.add(media_group_id)
            
            # Ждём немного, чтобы собрать все сообщения из группы
            time.sleep(2)
            
            # Объединяем все сообщения из группы
            group_messages = self.media_groups[media_group_id]
            
            # Берём первое сообщение как основу
            base_post = group_messages[0]
            text = base_post.get('text') or base_post.get('caption', '')
            
            # Собираем все фото
            all_photos = []
            for msg in group_messages:
                if 'photo' in msg:
                    photo = max(msg['photo'], key=lambda x: x.get('file_size', 0))
                    all_photos.append(photo)
                # Берём текст из первого сообщения с текстом
                if not text:
                    text = msg.get('text') or msg.get('caption', '')
            
            photos = all_photos
            logger.info(f'📷 Медиа-группа: {len(photos)} фото')
        
        else:
            # Обычный пост (одно фото или без фото)
            text = post.get('text') or post.get('caption', '')
            photos = []
            
            if 'photo' in post:
                photo = max(post['photo'], key=lambda x: x.get('file_size', 0))
                photos.append(photo)
        
        # Если нет текста И нет фото - пропускаем
        if not text and not photos:
            logger.warning(f'⏭️  Пост #{message_id}: нет текста и фото, пропускаем')
            sync.update_last_message(message_id, post_date, update_id)
            return
        
        # Парсим текст или создаём заголовок из даты
        if text:
            # Декодируем HTML-сущности
            text = html.unescape(text)
            lines = text.strip().split('\n', 1)
            title = lines[0][:255]
            content = lines[1] if len(lines) > 1 else text
        else:
            # Если текста нет, но есть фото - создаём заголовок из даты
            date_obj = post_date or timezone.now()
            title = f"Фото от {date_obj.strftime('%d.%m.%Y')}"
            content = f"Фотография, добавленная {date_obj.strftime('%d.%m.%Y в %H:%M')}"
        
        # Проверяем дубликат
        if Article.objects.filter(title=title).exists():
            logger.info(f'⏭️  Пост #{message_id}: "{title[:40]}..." уже существует')
            sync.update_last_message(message_id, post_date, update_id)
            return
        
        logger.info('')
        logger.info('=' * 80)
        logger.info('📰 НОВЫЙ ПОСТ ИЗ КАНАЛА')
        logger.info('=' * 80)
        logger.info(f'   Message ID: {message_id}')
        logger.info(f'   Заголовок: {title[:50]}...')
        logger.info(f'   Текст: {"Да" if text else "Нет"}')
        logger.info(f'   Фото: {len(photos)} шт.')
        logger.info('')
        
        try:
            # Создаём статью
            article = Article.objects.create(
                title=title,
                content=content,
                is_published=auto_publish
            )
            
            logger.info(f'✅ Статья создана: {article.slug}')
            
            # Сохраняем фото
            if photos:
                saved_photos = 0
                for photo_idx, photo in enumerate(photos):
                    try:
                        file_id = photo['file_id']
                        
                        # Получаем файл
                        file_response = requests.get(
                            f'{api_url}/getFile',
                            params={'file_id': file_id},
                            timeout=10
                        )
                        file_response.raise_for_status()
                        file_data = file_response.json()
                        
                        if not file_data.get('ok'):
                            logger.warning(f'   ⚠️  Фото {photo_idx + 1}: API ошибка')
                            continue
                        
                        file_path = file_data['result']['file_path']
                        file_url = f'https://api.telegram.org/file/bot{api_url.split("bot")[1].split("/")[0]}/{file_path}'
                        
                        # Скачиваем изображение
                        image_response = requests.get(file_url, timeout=30)
                        image_response.raise_for_status()
                        
                        image_content = BytesIO(image_response.content)
                        image_name = f'{article.slug}_{photo_idx}.jpg'
                        
                        if photo_idx == 0:
                            # Главное фото
                            article.image.save(
                                image_name,
                                InMemoryUploadedFile(
                                    image_content,
                                    None,
                                    image_name,
                                    'image/jpeg',
                                    len(image_response.content),
                                    None
                                )
                            )
                            logger.info(f'   📷 Главное фото сохранено')
                        else:
                            # Фото в галерею
                            article_image = ArticleImage.objects.create(
                                article=article,
                                order=photo_idx
                            )
                            article_image.image.save(
                                image_name,
                                InMemoryUploadedFile(
                                    image_content,
                                    None,
                                    image_name,
                                    'image/jpeg',
                                    len(image_response.content),
                                    None
                                )
                            )
                            logger.info(f'   📷 Фото {photo_idx + 1} → галерея')
                        
                        saved_photos += 1
                    
                    except Exception as e:
                        logger.error(f'   ❌ Ошибка фото {photo_idx + 1}: {e}')
                
                if saved_photos > 0:
                    logger.info(f'   ✅ Сохранено фото: {saved_photos}/{len(photos)}')
            
            # Обновляем синхронизацию
            sync.update_last_message(message_id, post_date, update_id)
            sync.posts_processed += 1
            sync.save()
            
            logger.info('')
            logger.info(f'✅ НОВОСТЬ ОПУБЛИКОВАНА: {article.slug}')
            logger.info(f'   Статус: {"Опубликована" if auto_publish else "Черновик"}')
            logger.info(f'   Всего обработано: {sync.posts_processed}')
            logger.info('=' * 80)
            logger.info('')
        
        except Exception as e:
            logger.error(f'❌ Ошибка при создании новости: {e}')
            logger.exception(e)
    
    @staticmethod
    def _send_message(api_url: str, chat_id: int, text: str, parse_mode: str = None) -> bool:
        """
        Отправляет сообщение в Telegram
        
        Args:
            api_url: URL API бота
            chat_id: ID чата
            text: Текст сообщения
            parse_mode: Режим парсинга (HTML, Markdown)
        
        Returns:
            True если сообщение отправлено успешно
        """
        try:
            payload = {
                'chat_id': chat_id,
                'text': text
            }
            
            if parse_mode:
                payload['parse_mode'] = parse_mode
            
            response = requests.post(
                f'{api_url}/sendMessage',
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        
        except Exception as e:
            logger.error(f'Ошибка при отправке сообщения: {e}')
            return False
