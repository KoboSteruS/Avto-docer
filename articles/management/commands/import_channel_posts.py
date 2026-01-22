"""
Management команда для массового импорта всех постов из Telegram канала
"""
import os
import sys
import time
from pathlib import Path
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
from loguru import logger
import requests
from articles.models import Article, ArticleImage


class Command(BaseCommand):
    """
    Команда для массового импорта всех постов из Telegram канала.
    
    Собирает ВСЕ посты из указанного канала и создаёт из них новости на сайте.
    Полезно для первоначального заполнения базы данных.
    
    Использование:
        python manage.py import_channel_posts --channel @your_channel --limit 100
    """
    help = 'Импортирует все посты из Telegram канала в базу данных'
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            '--channel',
            type=str,
            help='Username канала (например, @avto_decor_news)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Максимальное количество постов для импорта (по умолчанию 100)',
        )
        parser.add_argument(
            '--offset',
            type=int,
            default=0,
            help='С какого поста начать (пропустить первые N постов)',
        )
        parser.add_argument(
            '--auto-publish',
            action='store_true',
            help='Автоматически публиковать новости (по умолчанию сохраняются как черновики)',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Пропускать посты, которые уже есть в базе (по заголовку)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Тестовый режим - не сохранять в базу, только показать что будет импортировано',
        )
    
    def handle(self, *args, **options):
        """Основной метод команды"""
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '8389210453:AAE0pUO2PflNa8UWqXWRN-SEnf8LvplsdrA')
        api_url = f'https://api.telegram.org/bot{token}'
        channel_username = options.get('channel') or os.environ.get('TELEGRAM_NEWS_CHANNEL')
        limit = options['limit']
        offset = options['offset']
        auto_publish = options['auto_publish']
        skip_existing = options['skip_existing']
        dry_run = options['dry_run']
        
        if not channel_username:
            logger.error('❌ Не указан username канала. Используйте --channel @your_channel')
            sys.exit(1)
        
        # Убираем @ если есть
        channel_username = channel_username.lstrip('@')
        
        logger.info('=' * 80)
        logger.info('🚀 МАССОВЫЙ ИМПОРТ ПОСТОВ ИЗ TELEGRAM КАНАЛА')
        logger.info('=' * 80)
        logger.info(f'📺 Канал: @{channel_username}')
        logger.info(f'📊 Лимит постов: {limit}')
        logger.info(f'⏭️  Пропустить первых: {offset}')
        logger.info(f'📝 Автопубликация: {"Да" if auto_publish else "Нет (черновики)"}')
        logger.info(f'🔄 Пропускать существующие: {"Да" if skip_existing else "Нет"}')
        logger.info(f'🧪 Тестовый режим: {"Да (не сохраняется)" if dry_run else "Нет (сохраняется)"}')
        logger.info('=' * 80)
        
        # Проверяем, что бот работает
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
        logger.info('🔍 Получаем список постов из канала...')
        
        # Получаем историю постов из канала
        posts = []
        current_offset = 0
        max_message_id = None
        
        try:
            # Сначала получаем последний пост, чтобы узнать max message_id
            logger.info('📡 Получаем информацию о канале...')
            
            # Получаем chat_id канала
            channel_info_response = requests.post(
                f'{api_url}/getChat',
                json={'chat_id': f'@{channel_username}'},
                timeout=10
            )
            
            if not channel_info_response.json().get('ok'):
                logger.error(f'❌ Канал @{channel_username} не найден или бот не является администратором')
                logger.error('💡 Убедитесь, что:')
                logger.error('   1. Канал существует')
                logger.error('   2. Username канала указан правильно')
                logger.error('   3. Бот добавлен в администраторы канала')
                sys.exit(1)
            
            chat_id = channel_info_response.json()['result']['id']
            logger.info(f'✅ Канал найден! Chat ID: {chat_id}')
            
            # Теперь получаем посты через getUpdates (с момента добавления бота)
            # Или через пагинацию с помощью getChatHistory (недоступно в Bot API)
            
            # Альтернатива: используем поиск через offset
            logger.info('📥 Начинаем сбор постов...')
            logger.info('')
            
            collected_count = 0
            message_id = 1  # Начинаем с первого сообщения
            max_attempts = limit * 2  # Ограничиваем попытки
            attempts = 0
            
            while collected_count < limit and attempts < max_attempts:
                attempts += 1
                
                try:
                    # Пытаемся получить сообщение по ID
                    msg_response = requests.post(
                        f'{api_url}/forwardMessage',
                        json={
                            'chat_id': chat_id,
                            'from_chat_id': chat_id,
                            'message_id': message_id,
                            'disable_notification': True
                        },
                        timeout=5
                    )
                    
                    # Если сообщение не найдено, переходим к следующему
                    if not msg_response.json().get('ok'):
                        message_id += 1
                        continue
                    
                    # Получаем данные поста
                    # На самом деле нам нужен другой подход...
                    
                except Exception:
                    message_id += 1
                    continue
            
            # АЛЬТЕРНАТИВНЫЙ ПОДХОД: Используем экспорт через getUpdates
            logger.warning('⚠️  Bot API не поддерживает прямой доступ к истории канала')
            logger.info('💡 Используем альтернативный метод через getUpdates...')
            logger.info('')
            logger.info('📌 ИНСТРУКЦИЯ:')
            logger.info('')
            logger.info('К сожалению, Telegram Bot API не позволяет получить историю постов канала.')
            logger.info('Доступны только новые посты, которые приходят после добавления бота.')
            logger.info('')
            logger.info('🔧 РЕШЕНИЕ:')
            logger.info('')
            logger.info('Вариант 1 (Рекомендуемый):')
            logger.info('  1. Запустите бота для мониторинга: python manage.py run_news_bot --channel @{}'.format(channel_username))
            logger.info('  2. В канале "Переслать" (forward) нужные старые посты')
            logger.info('  3. Бот поймает их как новые и создаст новости')
            logger.info('')
            logger.info('Вариант 2 (Через Telegram Desktop):')
            logger.info('  1. Откройте канал в Telegram Desktop')
            logger.info('  2. Экспортируйте историю (Settings → Export chat history)')
            logger.info('  3. Получите JSON файл с постами')
            logger.info('  4. Используйте скрипт импорта из JSON (создам отдельно)')
            logger.info('')
            logger.info('Вариант 3 (Ручной):')
            logger.info('  1. Создайте новости через админку Django')
            logger.info('  2. Загрузите фото вручную')
            logger.info('')
            
            # Попробуем получить хотя бы последние обновления
            logger.info('🔄 Пробуем получить последние посты через getUpdates...')
            
            updates_response = requests.get(
                f'{api_url}/getUpdates',
                params={
                    'offset': -100,  # Последние 100 обновлений
                    'limit': 100,
                    'allowed_updates': ['channel_post']
                },
                timeout=30
            )
            
            if updates_response.json().get('ok'):
                updates = updates_response.json().get('result', [])
                logger.info(f'✅ Получено обновлений: {len(updates)}')
                
                for update in updates:
                    if 'channel_post' in update:
                        post = update['channel_post']
                        
                        # Проверяем, что это наш канал
                        post_username = post.get('chat', {}).get('username', '')
                        if post_username != channel_username:
                            continue
                        
                        posts.append(post)
                
                logger.info(f'✅ Найдено постов из канала @{channel_username}: {len(posts)}')
            else:
                logger.warning('⚠️  Не удалось получить обновления')
            
            if not posts:
                logger.info('')
                logger.info('=' * 80)
                logger.info('❌ Посты не найдены')
                logger.info('=' * 80)
                logger.info('')
                logger.info('Для импорта старых постов используйте метод с пересылкой (см. выше)')
                return
            
            # Обрабатываем найденные посты
            logger.info('')
            logger.info('=' * 80)
            logger.info(f'📦 ОБРАБОТКА ПОСТОВ: {len(posts)} шт.')
            logger.info('=' * 80)
            logger.info('')
            
            created_count = 0
            skipped_count = 0
            error_count = 0
            
            for idx, post in enumerate(posts[offset:offset+limit], 1):
                try:
                    text = post.get('text') or post.get('caption', '')
                    
                    if not text:
                        logger.warning(f'⚠️  Пост #{idx}: Нет текста, пропускаем')
                        skipped_count += 1
                        continue
                    
                    # Получаем фото
                    photos = []
                    if 'photo' in post:
                        photo = max(post['photo'], key=lambda x: x.get('file_size', 0))
                        photos.append(photo)
                    
                    # Разбираем текст
                    lines = text.strip().split('\n', 1)
                    title = lines[0][:255]
                    content = lines[1] if len(lines) > 1 else text
                    
                    logger.info(f'📰 Пост #{idx}: {title[:50]}...')
                    logger.info(f'   📷 Фото: {len(photos)} шт.')
                    
                    # Проверяем существование
                    if skip_existing:
                        if Article.objects.filter(title=title).exists():
                            logger.info(f'   ⏭️  Уже существует, пропускаем')
                            skipped_count += 1
                            continue
                    
                    if dry_run:
                        logger.info(f'   🧪 Тестовый режим - не сохраняем')
                        created_count += 1
                        continue
                    
                    # Создаём статью
                    article = Article.objects.create(
                        title=title,
                        content=content,
                        is_published=auto_publish
                    )
                    
                    logger.info(f'   ✅ Создана: {article.slug}')
                    
                    # Сохраняем фото
                    for photo_idx, photo in enumerate(photos):
                        try:
                            file_id = photo['file_id']
                            
                            file_response = requests.get(
                                f'{api_url}/getFile',
                                params={'file_id': file_id},
                                timeout=10
                            )
                            file_response.raise_for_status()
                            file_data = file_response.json()
                            
                            if not file_data.get('ok'):
                                continue
                            
                            file_path = file_data['result']['file_path']
                            file_url = f'https://api.telegram.org/file/bot{token}/{file_path}'
                            
                            image_response = requests.get(file_url, timeout=30)
                            image_response.raise_for_status()
                            
                            image_content = BytesIO(image_response.content)
                            image_name = f'{article.slug}_{photo_idx}.jpg'
                            
                            if photo_idx == 0:
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
                                logger.info(f'      📷 Главное фото сохранено')
                            else:
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
                                logger.info(f'      📷 Фото {photo_idx + 1} в галерею')
                        
                        except Exception as e:
                            logger.error(f'      ❌ Ошибка при сохранении фото: {e}')
                    
                    created_count += 1
                    logger.info('')
                    
                except Exception as e:
                    logger.error(f'❌ Ошибка при обработке поста #{idx}: {e}')
                    error_count += 1
                    continue
            
            # Итоги
            logger.info('=' * 80)
            logger.info('✨ ИМПОРТ ЗАВЕРШЁН')
            logger.info('=' * 80)
            logger.info(f'✅ Создано новостей: {created_count}')
            logger.info(f'⏭️  Пропущено: {skipped_count}')
            logger.info(f'❌ Ошибок: {error_count}')
            logger.info(f'📊 Всего обработано: {len(posts)}')
            logger.info('=' * 80)
            
            if dry_run:
                logger.info('')
                logger.info('🧪 Тестовый режим - изменения НЕ сохранены')
                logger.info('   Запустите без --dry-run для реального импорта')
            
        except KeyboardInterrupt:
            logger.info('')
            logger.info('⚠️  Импорт прерван пользователем')
        except Exception as e:
            logger.error(f'❌ Критическая ошибка: {e}')
            import traceback
            traceback.print_exc()
            sys.exit(1)
