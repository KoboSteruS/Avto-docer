"""
Management команда для импорта постов через пересылку
"""
import os
import sys
import time
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import InMemoryUploadedFile
from loguru import logger
import requests
from articles.models import Article, ArticleImage


class Command(BaseCommand):
    """
    Команда для импорта постов из канала через механизм пересылки.
    
    КАК РАБОТАЕТ:
    1. Запускаешь эту команду
    2. Бот показывает инструкцию и свой username
    3. Переходишь в канал и пересылаешь боту нужные посты
    4. Бот автоматически создаёт из них новости
    5. Ctrl+C для остановки
    
    ПРЕИМУЩЕСТВА:
    - Можешь выбрать какие именно посты импортировать
    - Работает со старыми постами
    - Не нужен доступ к Bot API истории
    
    Использование:
        python manage.py import_forwarded_posts
    """
    help = 'Импортирует посты из канала через пересылку боту'
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            '--timeout',
            type=int,
            default=300,
            help='Сколько секунд ждать пересылки постов (по умолчанию 300 = 5 минут)',
        )
        parser.add_argument(
            '--auto-publish',
            action='store_true',
            help='Автоматически публиковать новости (по умолчанию черновики)',
        )
    
    def handle(self, *args, **options):
        """Основной метод команды"""
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '8389210453:AAE0pUO2PflNa8UWqXWRN-SEnf8LvplsdrA')
        api_url = f'https://api.telegram.org/bot{token}'
        timeout = options['timeout']
        auto_publish = options['auto_publish']
        offset = 0
        
        logger.info('=' * 80)
        logger.info('📥 ИМПОРТ ПОСТОВ ЧЕРЕЗ ПЕРЕСЫЛКУ')
        logger.info('=' * 80)
        
        # Проверяем бота
        try:
            response = requests.get(f'{api_url}/getMe', timeout=10)
            response.raise_for_status()
            bot_info = response.json()
            
            if bot_info.get('ok'):
                bot_username = bot_info['result'].get('username', 'Unknown')
                bot_first_name = bot_info['result'].get('first_name', 'Bot')
                logger.info(f'✅ Бот подключен: @{bot_username}')
                logger.info(f'   Имя: {bot_first_name}')
            else:
                logger.error('❌ Ошибка при подключении к боту')
                sys.exit(1)
                
        except Exception as e:
            logger.error(f'❌ Ошибка при проверке бота: {e}')
            sys.exit(1)
        
        logger.info('=' * 80)
        logger.info('')
        logger.info('📌 ИНСТРУКЦИЯ ПО ИМПОРТУ:')
        logger.info('')
        logger.info(f'1. Найди бота в Telegram: @{bot_username}')
        logger.info('2. Открой свой канал с новостями')
        logger.info('3. Выбери посты, которые хочешь импортировать')
        logger.info('4. Нажми "Переслать" (Forward) и отправь их боту')
        logger.info('5. Бот автоматически создаст новости из постов')
        logger.info(f'6. Время ожидания: {timeout} секунд ({timeout//60} минут)')
        logger.info('7. Ctrl+C для завершения')
        logger.info('')
        logger.info(f'📝 Режим публикации: {"Сразу публиковать" if auto_publish else "Черновики (нужна модерация)"}')
        logger.info('')
        logger.info('=' * 80)
        logger.info('')
        logger.info('⏳ Жду пересылки постов...')
        logger.info('')
        
        start_time = time.time()
        created_count = 0
        processed_message_ids = set()  # Чтобы не дублировать
        
        try:
            while True:
                # Проверяем таймаут
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    logger.info('')
                    logger.info(f'⏱️  Время ожидания истекло ({timeout} секунд)')
                    break
                
                try:
                    # Получаем обновления
                    response = requests.get(
                        f'{api_url}/getUpdates',
                        params={
                            'offset': offset,
                            'timeout': 30,
                            'allowed_updates': ['message']
                        },
                        timeout=35
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if not data.get('ok'):
                        logger.error(f'Ошибка API: {data.get("description")}')
                        time.sleep(5)
                        continue
                    
                    updates = data.get('result', [])
                    
                    for update in updates:
                        offset = update['update_id'] + 1
                        
                        if 'message' not in update:
                            continue
                        
                        message = update['message']
                        
                        # Проверяем, что это пересланное сообщение
                        if 'forward_from_chat' not in message and 'forward_origin' not in message:
                            # Не пересланное - отвечаем инструкцией
                            chat_id = message['chat']['id']
                            text = message.get('text', '')
                            
                            if text.startswith('/start'):
                                self._send_message(
                                    api_url,
                                    chat_id,
                                    f'👋 Привет! Я бот для импорта новостей.\n\n'
                                    f'📥 Чтобы импортировать посты:\n\n'
                                    f'1. Открой свой канал\n'
                                    f'2. Выбери посты для импорта\n'
                                    f'3. Нажми "Переслать" и отправь их мне\n\n'
                                    f'Я создам из них новости на сайте!\n\n'
                                    f'⚠️ Запусти команду: python manage.py import_forwarded_posts'
                                )
                            continue
                        
                        # Это пересланное сообщение!
                        forward_from = message.get('forward_from_chat') or message.get('forward_origin', {})
                        
                        # ID оригинального сообщения (чтобы не дублировать)
                        original_message_id = None
                        if 'forward_from_chat' in message:
                            original_message_id = message.get('forward_from_message_id')
                        elif 'forward_origin' in message:
                            forward_origin = message['forward_origin']
                            if forward_origin.get('type') == 'channel':
                                original_message_id = forward_origin.get('message_id')
                        
                        if original_message_id and original_message_id in processed_message_ids:
                            logger.info(f'⏭️  Пост уже обработан, пропускаем')
                            continue
                        
                        if original_message_id:
                            processed_message_ids.add(original_message_id)
                        
                        # Получаем текст и фото
                        text = message.get('text') or message.get('caption', '')
                        photos = []
                        
                        if 'photo' in message:
                            photo = max(message['photo'], key=lambda x: x.get('file_size', 0))
                            photos.append(photo)
                        
                        if not text:
                            logger.warning('⚠️  Пост без текста, пропускаем')
                            continue
                        
                        logger.info('=' * 80)
                        logger.info('📥 ПОЛУЧЕН ПЕРЕСЛАННЫЙ ПОСТ')
                        logger.info('=' * 80)
                        
                        # Разбираем текст
                        lines = text.strip().split('\n', 1)
                        title = lines[0][:255]
                        content = lines[1] if len(lines) > 1 else text
                        
                        logger.info(f'📰 Заголовок: {title}')
                        logger.info(f'📝 Длина текста: {len(content)} символов')
                        logger.info(f'📷 Фото: {len(photos)} шт.')
                        
                        try:
                            # Создаём статью
                            article = Article.objects.create(
                                title=title,
                                content=content,
                                is_published=auto_publish
                            )
                            
                            logger.info(f'✅ Создана новость: {article.title}')
                            logger.info(f'   Slug: {article.slug}')
                            logger.info(f'   Опубликована: {"Да" if article.is_published else "Нет (черновик)"}')
                            
                            # Сохраняем фото
                            for idx, photo in enumerate(photos):
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
                                        logger.error(f'Ошибка при получении файла: {file_data.get("description")}')
                                        continue
                                    
                                    file_path = file_data['result']['file_path']
                                    file_url = f'https://api.telegram.org/file/bot{token}/{file_path}'
                                    
                                    image_response = requests.get(file_url, timeout=30)
                                    image_response.raise_for_status()
                                    
                                    image_content = BytesIO(image_response.content)
                                    image_name = f'{article.slug}_{idx}.jpg'
                                    
                                    if idx == 0:
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
                                        logger.info(f'   📷 Главное изображение сохранено')
                                    else:
                                        article_image = ArticleImage.objects.create(
                                            article=article,
                                            order=idx
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
                                        logger.info(f'   📷 Изображение {idx + 1} добавлено в галерею')
                                
                                except Exception as e:
                                    logger.error(f'Ошибка при сохранении фото {idx}: {e}')
                            
                            created_count += 1
                            
                            # Отправляем подтверждение пользователю
                            chat_id = message['chat']['id']
                            self._send_message(
                                api_url,
                                chat_id,
                                f'✅ Новость создана!\n\n'
                                f'📰 {article.title}\n'
                                f'🔗 {article.slug}\n'
                                f'📝 {len(content)} символов\n'
                                f'📷 {len(photos)} фото\n'
                                f'📊 Всего импортировано: {created_count}'
                            )
                            
                            logger.info(f'✨ Новость #{created_count} успешно создана!')
                            logger.info('=' * 80)
                            logger.info('')
                            
                        except Exception as e:
                            logger.error(f'❌ Ошибка при создании новости: {e}')
                            
                            # Уведомляем об ошибке
                            chat_id = message['chat']['id']
                            self._send_message(
                                api_url,
                                chat_id,
                                f'❌ Ошибка при создании новости:\n{str(e)}'
                            )
                    
                    if not updates:
                        time.sleep(1)
                        
                except requests.exceptions.Timeout:
                    continue
                except requests.exceptions.RequestException as e:
                    logger.error(f'Ошибка при получении обновлений: {e}')
                    time.sleep(5)
                except KeyboardInterrupt:
                    logger.info('')
                    logger.info('⚠️  Импорт прерван пользователем')
                    break
                except Exception as e:
                    logger.error(f'Неожиданная ошибка: {e}')
                    time.sleep(5)
                    
        except KeyboardInterrupt:
            logger.info('')
            logger.info('⚠️  Импорт остановлен')
        
        # Итоги
        logger.info('')
        logger.info('=' * 80)
        logger.info('✨ ИМПОРТ ЗАВЕРШЁН')
        logger.info('=' * 80)
        logger.info(f'✅ Создано новостей: {created_count}')
        logger.info(f'⏱️  Время работы: {int(time.time() - start_time)} секунд')
        logger.info('=' * 80)
    
    @staticmethod
    def _send_message(api_url: str, chat_id: int, text: str) -> bool:
        """Отправляет сообщение в Telegram"""
        try:
            response = requests.post(
                f'{api_url}/sendMessage',
                json={
                    'chat_id': chat_id,
                    'text': text
                },
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f'Ошибка при отправке сообщения: {e}')
            return False
