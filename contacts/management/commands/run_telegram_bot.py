"""
Management команда для запуска Telegram бота с polling
"""
import os
import sys
from django.core.management.base import BaseCommand
from loguru import logger
import requests
import time
from contacts.utils import SubscribersManager


class Command(BaseCommand):
    """
    Команда для запуска Telegram бота с polling
    
    Бот слушает обновления и отправляет заявки с сайта в Telegram
    """
    help = 'Запускает Telegram бота с polling для получения заявок'
    
    def add_arguments(self, parser):
        """
        Добавляет аргументы команды
        """
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Таймаут для long polling (по умолчанию 30 секунд)',
        )
    
    def handle(self, *args, **options):
        """
        Основной метод команды
        """
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '8389210453:AAE0pUO2PflNa8UWqXWRN-SEnf8LvplsdrA')
        api_url = f'https://api.telegram.org/bot{token}'
        timeout = options['timeout']
        offset = 0
        subscribers_manager = SubscribersManager()
        
        logger.info('Запуск Telegram бота с polling...')
        logger.info(f'Токен: {token[:10]}...')
        logger.info(f'Файл подписчиков: {subscribers_manager.subscribers_file}')
        logger.info(f'Файл существует: {subscribers_manager.subscribers_file.exists()}')
        logger.info(f'Текущее количество подписчиков: {subscribers_manager.get_count()}')
        
        # Показываем текущих подписчиков
        current_subscribers = subscribers_manager.get_subscribers()
        if current_subscribers:
            logger.info(f'Текущие подписчики: {list(current_subscribers)}')
        else:
            logger.warning('Подписчиков нет. Отправьте боту /start для подписки на уведомления')
        
        # Проверяем, что бот работает
        try:
            response = requests.get(f'{api_url}/getMe', timeout=10)
            response.raise_for_status()
            bot_info = response.json()
            
            if bot_info.get('ok'):
                bot_username = bot_info['result'].get('username', 'Unknown')
                logger.info(f'Бот успешно подключен: @{bot_username}')
            else:
                logger.error('Ошибка при подключении к боту')
                sys.exit(1)
                
        except Exception as e:
            logger.error(f'Ошибка при проверке бота: {e}')
            sys.exit(1)
        
        logger.info('Бот запущен и ожидает обновления...')
        logger.info('Для остановки нажмите Ctrl+C')
        
        # Основной цикл polling
        try:
            while True:
                try:
                    # Получаем обновления
                    response = requests.get(
                        f'{api_url}/getUpdates',
                        params={
                            'offset': offset,
                            'timeout': timeout,
                            'allowed_updates': ['message']
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
                        
                        # Обрабатываем только сообщения
                        if 'message' in update:
                            message = update['message']
                            chat_id = message['chat']['id']
                            chat_id_str = str(chat_id)
                            text = message.get('text', '')
                            
                            # Отвечаем на команды
                            if text.startswith('/start'):
                                logger.info(f'Получена команда /start от chat_id: {chat_id_str}')
                                
                                # Добавляем подписчика
                                is_new = subscribers_manager.add_subscriber(chat_id_str)
                                
                                # Проверяем, что подписчик действительно добавлен
                                current_count = subscribers_manager.get_count()
                                is_in_list = subscribers_manager.is_subscribed(chat_id_str)
                                
                                logger.info(f'Результат добавления: is_new={is_new}, count={current_count}, is_in_list={is_in_list}')
                                
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
                                    logger.info(f'✅ Новый подписчик добавлен: {chat_id_str}. Всего: {current_count}')
                                else:
                                    self._send_message(
                                        api_url,
                                        chat_id,
                                        'Вы уже подписаны на уведомления о заявках.\n\n'
                                        f'Ваш chat_id: <code>{chat_id}</code>\n'
                                        f'Всего подписчиков: {current_count}',
                                        parse_mode='HTML'
                                    )
                                    logger.info(f'ℹ️ Подписчик уже был в списке: {chat_id_str}')
                                
                                # Дополнительная проверка
                                final_subscribers = subscribers_manager.get_subscribers()
                                logger.info(f'Финальный список подписчиков ({len(final_subscribers)}): {list(final_subscribers)}')
                                
                            elif text.startswith('/stop'):
                                # Удаляем подписчика
                                removed = subscribers_manager.remove_subscriber(chat_id_str)
                                
                                if removed:
                                    self._send_message(
                                        api_url,
                                        chat_id,
                                        '❌ Вы отписаны от уведомлений о заявках.\n\n'
                                        'Чтобы снова получать уведомления, отправьте /start'
                                    )
                                    logger.info(f'Подписчик удален: {chat_id_str}')
                                else:
                                    self._send_message(
                                        api_url,
                                        chat_id,
                                        'Вы не были подписаны на уведомления.'
                                    )
                                
                                logger.info(f'Всего подписчиков: {subscribers_manager.get_count()}')
                                
                            elif text.startswith('/help'):
                                is_subscribed = subscribers_manager.is_subscribed(chat_id_str)
                                status = '✅ подписаны' if is_subscribed else '❌ не подписаны'
                                
                                self._send_message(
                                    api_url,
                                    chat_id,
                                    '🤖 Бот для получения заявок с сайта Avto-Декор\n\n'
                                    f'Ваш статус: {status}\n\n'
                                    'Команды:\n'
                                    '/start - Подписаться на уведомления\n'
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
                                is_subscribed = subscribers_manager.is_subscribed(chat_id_str)
                                total_subscribers = subscribers_manager.get_count()
                                
                                if is_subscribed:
                                    status_text = '✅ Вы подписаны на уведомления'
                                else:
                                    status_text = '❌ Вы не подписаны на уведомления\n\nОтправьте /start для подписки'
                                
                                self._send_message(
                                    api_url,
                                    chat_id,
                                    f'{status_text}\n\n'
                                    f'Всего подписчиков: {total_subscribers}\n'
                                    f'Ваш chat_id: <code>{chat_id}</code>',
                                    parse_mode='HTML'
                                )
                                
                            else:
                                # Просто подтверждаем получение сообщения
                                is_subscribed = subscribers_manager.is_subscribed(chat_id_str)
                                
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
                    
                    # Небольшая задержка перед следующим запросом
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
                    time.sleep(5)
                    
        except KeyboardInterrupt:
            logger.info('Бот остановлен')
        except Exception as e:
            logger.error(f'Критическая ошибка: {e}')
            sys.exit(1)
    
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
