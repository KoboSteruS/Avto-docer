"""
Улучшенная команда для массового импорта постов из Telegram с поддержкой очереди
"""
import os
import sys
import time
from datetime import datetime
from io import BytesIO
from collections import deque
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
from django.utils import timezone
from loguru import logger
import requests
from articles.models import Article, ArticleImage


class Command(BaseCommand):
    """
    Улучшенная команда для импорта постов с поддержкой батч-обработки и очереди.
    
    Особенности:
    - Собирает все пересланные посты в очередь
    - Обрабатывает их батчами
    - Не спамит ответами
    - Показывает прогресс
    - Защита от дубликатов
    
    Использование:
        python manage.py batch_import_posts --timeout 300
    """
    help = 'Батч-импорт постов из Telegram с очередью'
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            '--timeout',
            type=int,
            default=300,
            help='Время ожидания постов в секундах (по умолчанию 300 = 5 минут)',
        )
        parser.add_argument(
            '--auto-publish',
            action='store_true',
            help='Автоматически публиковать новости',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=20,
            help='Размер батча для обработки (по умолчанию 20)',
        )
    
    def handle(self, *args, **options):
        """Основной метод команды"""
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '8389210453:AAE0pUO2PflNa8UWqXWRN-SEnf8LvplsdrA')
        api_url = f'https://api.telegram.org/bot{token}'
        timeout = options['timeout']
        auto_publish = options['auto_publish']
        batch_size = options['batch_size']
        
        logger.info('=' * 80)
        logger.info('📦 БАТЧ-ИМПОРТ ПОСТОВ ИЗ TELEGRAM')
        logger.info('=' * 80)
        logger.info(f'⏱️  Таймаут: {timeout} сек ({timeout//60} мин)')
        logger.info(f'📊 Размер батча: {batch_size} постов')
        logger.info(f'📝 Публикация: {"Сразу" if auto_publish else "Черновики"}')
        logger.info('=' * 80)
        
        # Проверяем бота
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
            logger.error(f'❌ Ошибка: {e}')
            sys.exit(1)
        
        logger.info('')
        logger.info('📌 ИНСТРУКЦИЯ:')
        logger.info('')
        logger.info(f'1. Открой бота @{bot_username} в Telegram')
        logger.info('2. Открой канал с новостями')
        logger.info('3. Выбери посты (можно выбрать сразу много)')
        logger.info('4. Нажми "Переслать" и отправь боту')
        logger.info(f'5. Жди {timeout//60} минут - бот соберёт все посты')
        logger.info('6. Затем обработает их батчами')
        logger.info('')
        logger.info('💡 Можно пересылать частями, бот подождёт все')
        logger.info('')
        logger.info('=' * 80)
        logger.info('')
        logger.info('⏳ Сбор постов... (пересылай сейчас)')
        logger.info('')
        
        # Очередь для постов и группировка медиа
        posts_queue = deque()
        processed_ids = set()
        media_groups = {}  # Группировка медиа по media_group_id
        offset = 0
        start_time = time.time()
        last_post_time = time.time()
        
        # Этап 1: Сбор постов
        logger.info('📥 ЭТАП 1: СБОР ПОСТОВ')
        logger.info(f'   Жду {timeout} секунд...')
        logger.info('')
        
        collection_phase = True
        
        try:
            while collection_phase:
                elapsed = time.time() - start_time
                time_since_last = time.time() - last_post_time
                
                # Завершаем сбор если:
                # 1. Прошёл общий таймаут
                # 2. Или прошло 30 сек с последнего поста и уже есть посты
                if elapsed > timeout or (time_since_last > 30 and len(posts_queue) > 0):
                    collection_phase = False
                    break
                
                try:
                    response = requests.get(
                        f'{api_url}/getUpdates',
                        params={
                            'offset': offset,
                            'timeout': 10,
                            'allowed_updates': ['message']
                        },
                        timeout=15
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if not data.get('ok'):
                        time.sleep(2)
                        continue
                    
                    updates = data.get('result', [])
                    
                    for update in updates:
                        offset = update['update_id'] + 1
                        
                        if 'message' not in update:
                            continue
                        
                        message = update['message']
                        
                        # Игнорируем не пересланные сообщения (без спама ответами)
                        if 'forward_from_chat' not in message and 'forward_origin' not in message:
                            continue
                        
                        # Получаем ID для дедупликации
                        message_id = message.get('message_id')
                        forward_date = message.get('forward_date', 0)
                        unique_id = f"{message_id}_{forward_date}"
                        
                        if unique_id in processed_ids:
                            continue
                        
                        processed_ids.add(unique_id)
                        
                        # Проверяем, это часть медиа-группы?
                        media_group_id = message.get('media_group_id')
                        
                        if media_group_id:
                            # Это часть группы фото - добавляем в группу
                            if media_group_id not in media_groups:
                                media_groups[media_group_id] = []
                            media_groups[media_group_id].append(message)
                            logger.info(f'   ✅ Добавлено фото в группу #{len(media_groups[media_group_id])}')
                        else:
                            # Обычный пост - сразу в очередь
                            posts_queue.append(message)
                            last_post_time = time.time()
                            logger.info(f'   ✅ Добавлен пост #{len(posts_queue)}')
                    
                    # Показываем прогресс каждые 10 секунд
                    if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                        remaining = timeout - int(elapsed)
                        logger.info(f'   ⏱️  Собрано: {len(posts_queue)} постов, {len(media_groups)} групп | Осталось: {remaining} сек')
                    
                except requests.exceptions.RequestException:
                    time.sleep(2)
                    continue
            
            logger.info('')
            logger.info('=' * 80)
            logger.info(f'✅ СБОР ЗАВЕРШЁН')
            logger.info('=' * 80)
            logger.info(f'📊 Постов: {len(posts_queue)}')
            logger.info(f'📷 Медиа-групп: {len(media_groups)}')
            logger.info('')
            
            # Объединяем медиа-группы в посты
            if media_groups:
                logger.info('🔗 Объединяю медиа-группы...')
                for group_id, messages in media_groups.items():
                    # Берём первое сообщение как основу (там может быть текст)
                    base_message = messages[0]
                    
                    # Собираем все фото и видео из группы
                    all_photos = []
                    all_videos = []
                    group_text = base_message.get('text') or base_message.get('caption', '')
                    
                    for msg in messages:
                        if 'photo' in msg:
                            photo = max(msg['photo'], key=lambda x: x.get('file_size', 0))
                            all_photos.append(photo)
                        if 'video' in msg:
                            all_videos.append({
                                'video': msg['video'],
                                'message_id': msg.get('message_id'),
                                'caption': msg.get('caption', '')
                            })
                        # Проверяем video_note (кружки/stories)
                        if 'video_note' in msg:
                            all_videos.append({
                                'video': msg['video_note'],
                                'message_id': msg.get('message_id'),
                                'caption': msg.get('caption', ''),
                                'is_video_note': True
                            })
                        # Берём текст из первого сообщения с текстом
                        if not group_text:
                            group_text = msg.get('text') or msg.get('caption', '')
                    
                    # Создаём объединённое сообщение
                    combined_message = base_message.copy()
                    combined_message['_all_photos'] = all_photos  # Сохраняем все фото
                    combined_message['_all_videos'] = all_videos  # Сохраняем все видео
                    if group_text:
                        combined_message['text'] = group_text
                    
                    posts_queue.append(combined_message)
                    media_info = []
                    if all_photos:
                        media_info.append(f'{len(all_photos)} фото')
                    if all_videos:
                        media_info.append(f'{len(all_videos)} видео')
                    logger.info(f'   ✅ Группа: {", ".join(media_info) if media_info else "пустая"} → 1 пост')
                
                logger.info('')
            
            total_posts = len(posts_queue)
            logger.info(f'📦 Всего к обработке: {total_posts} постов')
            logger.info('')
            
            if total_posts == 0:
                logger.warning('⚠️  Не получено ни одного поста')
                logger.info('💡 Убедись, что пересылаешь боту пересланные (forwarded) сообщения из канала')
                return
            
            # Этап 2: Обработка батчами
            logger.info('🔄 ЭТАП 2: ОБРАБОТКА ПОСТОВ')
            logger.info(f'   Всего постов: {len(posts_queue)}')
            logger.info(f'   Размер батча: {batch_size}')
            logger.info('')
            
            created_count = 0
            skipped_count = 0
            error_count = 0
            batch_num = 0
            
            while posts_queue:
                batch_num += 1
                batch = []
                
                # Берём батч постов
                for _ in range(min(batch_size, len(posts_queue))):
                    if posts_queue:
                        batch.append(posts_queue.popleft())
                
                logger.info(f'📦 Батч #{batch_num}: Обработка {len(batch)} постов...')
                logger.info('')
                
                for idx, message in enumerate(batch, 1):
                    try:
                        # Извлекаем данные
                        text = message.get('text') or message.get('caption', '')
                        
                        # Получаем фото (может быть одно фото или группа)
                        photos = []
                        videos = []  # Список видео (может быть несколько в медиа-группе)
                        
                        # Проверяем, это объединённая медиа-группа?
                        if '_all_photos' in message:
                            # Используем все фото из группы
                            photos = message['_all_photos']
                        elif 'photo' in message:
                            # Одно фото
                            photo = max(message['photo'], key=lambda x: x.get('file_size', 0))
                            photos.append(photo)
                        
                        # Проверяем медиа-группу с видео
                        if '_all_videos' in message:
                            # Используем все видео из группы
                            videos = message['_all_videos']
                        else:
                            # Обычное видео (одно)
                            if 'video' in message:
                                videos = [{
                                    'video': message['video'],
                                    'message_id': message.get('forward_from_message_id') or message.get('message_id'),
                                    'caption': message.get('caption', '')
                                }]
                            
                            # Проверяем video_note (кружки/stories)
                            if 'video_note' in message:
                                videos = [{
                                    'video': message['video_note'],
                                    'message_id': message.get('forward_from_message_id') or message.get('message_id'),
                                    'caption': message.get('caption', ''),
                                    'is_video_note': True
                                }]
                        
                        # Если нет текста И нет фото И нет видео - пропускаем
                        if not text and not photos and not videos:
                            logger.warning(f'   ⚠️  Пост #{idx}: Нет текста, фото и видео, пропускаем')
                            skipped_count += 1
                            continue
                        
                        # Парсим текст или создаём заголовок из даты
                        if text:
                            lines = text.strip().split('\n', 1)
                            title = lines[0][:255]
                            content = lines[1] if len(lines) > 1 else text
                        else:
                            # Если текста нет, но есть медиа - создаём заголовок из даты + времени
                            post_date = message.get('forward_date') or message.get('date', int(time.time()))
                            date_obj = datetime.fromtimestamp(post_date)
                            message_id = message.get('forward_from_message_id') or message.get('message_id', '')
                            msg_id_suffix = f" (#{message_id})" if message_id else ""
                            # Проверяем, есть ли video_note (кружки/stories)
                            is_video_note = videos and any(v.get('is_video_note') for v in videos)
                            # Добавляем время с секундами и message_id чтобы избежать дубликатов
                            if videos:
                                if is_video_note:
                                    title = f"Кружок от {date_obj.strftime('%d.%m.%Y %H:%M:%S')}{msg_id_suffix}"
                                    content = f"Видео-кружок (story), добавленный {date_obj.strftime('%d.%m.%Y в %H:%M:%S')}"
                                else:
                                    title = f"Видео от {date_obj.strftime('%d.%m.%Y %H:%M:%S')}{msg_id_suffix}"
                                    content = f"Видео, добавленное {date_obj.strftime('%d.%m.%Y в %H:%M:%S')}"
                            elif photos:
                                photo_count = len(photos)
                                if photo_count > 1:
                                    title = f"Фото {photo_count} шт. от {date_obj.strftime('%d.%m.%Y %H:%M:%S')}{msg_id_suffix}"
                                    content = f"Галерея из {photo_count} фотографий, добавленная {date_obj.strftime('%d.%m.%Y в %H:%M:%S')}"
                                else:
                                    title = f"Фото от {date_obj.strftime('%d.%m.%Y %H:%M:%S')}{msg_id_suffix}"
                                    content = f"Фотография, добавленная {date_obj.strftime('%d.%m.%Y в %H:%M:%S')}"
                            else:
                                # На всякий случай (не должно сюда попасть)
                                title = f"Пост от {date_obj.strftime('%d.%m.%Y %H:%M:%S')}{msg_id_suffix}"
                                content = f"Пост, добавленный {date_obj.strftime('%d.%m.%Y в %H:%M:%S')}"
                        
                        # Проверяем дубликат
                        if Article.objects.filter(title=title).exists():
                            logger.info(f'   ⏭️  Пост #{idx}: "{title[:40]}..." уже существует')
                            skipped_count += 1
                            continue
                        
                        # Логируем с информацией о содержимом
                        media_info = []
                        if text:
                            media_info.append('📝 текст')
                        if photos:
                            media_info.append(f'📷 {len(photos)} фото')
                        if videos:
                            video_note_count = sum(1 for v in videos if v.get('is_video_note'))
                            if video_note_count > 0:
                                if len(videos) > 1:
                                    media_info.append(f'🎥 {len(videos)} видео (из них {video_note_count} кружков)')
                                else:
                                    media_info.append('🎥 кружок/story')
                            else:
                                if len(videos) > 1:
                                    media_info.append(f'🎬 {len(videos)} видео')
                                else:
                                    media_info.append('🎬 видео')
                        
                        logger.info(f'   📰 Пост #{idx}: {title[:50]}... ({", ".join(media_info) if media_info else "нет контента"})')
                        
                        # Сохраняем видео (обрабатываем все видео из группы)
                        article = None
                        if videos:
                            saved_videos = 0
                            forward_from_chat = message.get('forward_from_chat', {})
                            channel_username = forward_from_chat.get('username', '')
                            
                            for video_idx, video_data in enumerate(videos):
                                try:
                                    video_obj = video_data['video']
                                    video_message_id = video_data['message_id']
                                    video_caption = video_data.get('caption', '')
                                    is_video_note = video_data.get('is_video_note', False)
                                    
                                    file_id = video_obj['file_id']
                                    file_size = video_obj.get('file_size', 0)
                                    size_mb = file_size / (1024 * 1024) if file_size else 0
                                    
                                    # Если видео несколько - создаём отдельную статью для каждого
                                    if len(videos) > 1 and video_idx > 0:
                                        # Создаём отдельную статью для дополнительного видео
                                        video_title = f"{title} (видео {video_idx + 1})"
                                        if video_caption:
                                            video_content = video_caption
                                        else:
                                            video_content = f"Видео {video_idx + 1} из серии"
                                        
                                        # Проверяем дубликат
                                        if Article.objects.filter(title=video_title).exists():
                                            logger.info(f'      ⏭️  Видео {video_idx + 1}: уже существует')
                                            continue
                                        
                                        video_article = Article.objects.create(
                                            title=video_title,
                                            content=video_content,
                                            is_published=auto_publish,
                                            video_status='ready'
                                        )
                                        
                                        # Сохраняем видео для дополнительной статьи
                                        if file_size > 20 * 1024 * 1024:
                                            video_article.telegram_channel_username = channel_username
                                            video_article.telegram_message_id = video_message_id
                                            video_article.video_status = 'pending'
                                            video_article.video_url = None
                                            video_article.save()
                                            logger.info(f'      ✅ Видео {video_idx + 1} сохранено (большое, ~{size_mb:.1f}MB, pending)')
                                        else:
                                            video_article.video_url = file_id
                                            video_article.save()
                                            logger.info(f'      ✅ Видео {video_idx + 1} сохранено (file_id, ~{size_mb:.1f}MB)')
                                        
                                        saved_videos += 1
                                        created_count += 1
                                        continue
                                    
                                    # Первое видео - создаём основную статью
                                    article = Article.objects.create(
                                        title=title,
                                        content=content,
                                        is_published=auto_publish,
                                        video_status='ready'
                                    )
                                    
                                    # Сохраняем видео для основной статьи
                                    if file_size > 20 * 1024 * 1024:
                                        article.telegram_channel_username = channel_username
                                        article.telegram_message_id = video_message_id
                                        article.video_status = 'pending'
                                        article.video_url = None
                                        article.save()
                                        logger.info(f'      ✅ Видео сохранено (большое, ~{size_mb:.1f}MB, pending)')
                                    else:
                                        article.video_url = file_id
                                        article.save()
                                        logger.info(f'      ✅ Видео сохранено (file_id, ~{size_mb:.1f}MB)')
                                    
                                    saved_videos += 1
                                    
                                except Exception as e:
                                    logger.error(f'      ❌ Ошибка сохранения видео {video_idx + 1}: {e}')
                            
                            if saved_videos > 0:
                                logger.info(f'      ✅ Сохранено видео: {saved_videos}/{len(videos)}')
                            
                            # Если были только видео - пропускаем сохранение фото
                            if not photos:
                                created_count += 1
                                logger.info(f'      ✅ Создана: {article.slug}')
                                continue
                        else:
                            # Нет видео - создаём статью для фото/текста
                            article = Article.objects.create(
                                title=title,
                                content=content,
                                is_published=auto_publish
                            )
                        
                        # Сохраняем фото
                        saved_photos = 0
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
                                    logger.warning(f'      ⚠️  Фото {photo_idx + 1}: API ошибка')
                                    continue
                                
                                file_path = file_data['result']['file_path']
                                file_url = f'https://api.telegram.org/file/bot{token}/{file_path}'
                                
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
                                    logger.info(f'      📷 Главное фото сохранено')
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
                                    logger.info(f'      📷 Фото {photo_idx + 1} → галерея')
                                
                                saved_photos += 1
                                
                            except Exception as e:
                                logger.error(f'      ❌ Ошибка фото {photo_idx + 1}: {e}')
                        
                        if saved_photos > 0:
                            logger.info(f'      ✅ Сохранено фото: {saved_photos}/{len(photos)}')
                        
                        # Увеличиваем счётчик созданных статей (если статья ещё не создана выше)
                        if article and (not videos or len(videos) == 1):
                            created_count += 1
                            logger.info(f'      ✅ Создана: {article.slug}')
                        
                    except Exception as e:
                        logger.error(f'   ❌ Ошибка поста #{idx}: {e}')
                        error_count += 1
                
                logger.info('')
                logger.info(f'   Батч #{batch_num} завершён')
                logger.info(f'   Создано: {created_count} | Пропущено: {skipped_count} | Ошибок: {error_count}')
                logger.info('')
                
                # Небольшая пауза между батчами
                if posts_queue:
                    logger.info('   ⏸️  Пауза 2 сек перед следующим батчем...')
                    logger.info('')
                    time.sleep(2)
            
            # Итоги
            logger.info('=' * 80)
            logger.info('✨ ИМПОРТ ЗАВЕРШЁН')
            logger.info('=' * 80)
            logger.info(f'✅ Создано: {created_count}')
            logger.info(f'⏭️  Пропущено: {skipped_count}')
            logger.info(f'❌ Ошибок: {error_count}')
            logger.info(f'📊 Всего обработано: {created_count + skipped_count + error_count}')
            logger.info('=' * 80)
            
        except KeyboardInterrupt:
            logger.info('')
            logger.info('⚠️  Прервано пользователем')
            logger.info(f'📊 Обработано до прерывания: {created_count}')
        except Exception as e:
            logger.error(f'❌ Критическая ошибка: {e}')
            import traceback
            traceback.print_exc()
            sys.exit(1)
