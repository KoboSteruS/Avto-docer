"""
Сервис для отправки заявок в Telegram
"""
import os
from typing import List, Optional
from loguru import logger
import requests
from contacts.utils import SubscribersManager


class TelegramService:
    """
    Сервис для работы с Telegram Bot API
    
    Отправляет заявки с контактной формы в Telegram через Bot API
    Поддерживает отправку нескольким подписчикам
    """
    
    def __init__(self):
        """
        Инициализация сервиса с токеном бота
        """
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN', '8389210453:AAE0pUO2PflNa8UWqXWRN-SEnf8LvplsdrA')
        self.api_url = f'https://api.telegram.org/bot{self.token}'
        self.subscribers_manager = SubscribersManager()
    
    def get_subscribers(self) -> List[str]:
        """
        Получает список всех подписчиков
        
        Returns:
            Список chat_id подписчиков
        """
        subscribers = self.subscribers_manager.get_subscribers()
        
        # Если подписчиков нет, проверяем старую переменную окружения для обратной совместимости
        if not subscribers:
            old_chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
            if old_chat_id:
                logger.info(f'Используется старый TELEGRAM_CHAT_ID: {old_chat_id}')
                return [old_chat_id]
        
        return list(subscribers)
    
    def send_message(self, text: str, chat_id: Optional[str] = None) -> bool:
        """
        Отправляет сообщение в Telegram одному получателю
        
        Args:
            text: Текст сообщения
            chat_id: ID чата (если не указан, отправляет всем подписчикам)
        
        Returns:
            True если сообщение отправлено успешно, False в противном случае
        """
        if chat_id:
            return self._send_to_chat(text, chat_id)
        else:
            # Отправляем всем подписчикам
            return self.send_to_all_subscribers(text)
    
    def send_to_all_subscribers(self, text: str) -> int:
        """
        Отправляет сообщение всем подписчикам
        
        Args:
            text: Текст сообщения
        
        Returns:
            Количество успешно отправленных сообщений
        """
        subscribers = self.get_subscribers()
        
        logger.info(f'Попытка отправить сообщение подписчикам. Найдено подписчиков: {len(subscribers)}')
        logger.debug(f'Список подписчиков: {list(subscribers)}')
        logger.debug(f'Путь к файлу подписчиков: {self.subscribers_manager.subscribers_file}')
        
        if not subscribers:
            logger.warning('Нет подписчиков. Запустите бота командой: python manage.py run_telegram_bot и отправьте ему /start')
            logger.warning(f'Файл подписчиков: {self.subscribers_manager.subscribers_file}')
            logger.warning(f'Файл существует: {self.subscribers_manager.subscribers_file.exists()}')
            return 0
        
        success_count = 0
        failed_chat_ids = []
        
        for chat_id in subscribers:
            if self._send_to_chat(text, chat_id):
                success_count += 1
            else:
                failed_chat_ids.append(chat_id)
        
        # Удаляем неактивных подписчиков (если чат не найден или заблокирован)
        for chat_id in failed_chat_ids:
            logger.warning(f'Удаление неактивного подписчика: {chat_id}')
            self.subscribers_manager.remove_subscriber(chat_id)
        
        logger.info(f'Сообщение отправлено {success_count} из {len(subscribers)} подписчиков')
        return success_count
    
    def _send_to_chat(self, text: str, chat_id: str) -> bool:
        """
        Отправляет сообщение в конкретный чат
        
        Args:
            text: Текст сообщения
            chat_id: ID чата
        
        Returns:
            True если сообщение отправлено успешно
        """
        try:
            url = f'{self.api_url}/sendMessage'
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.debug(f'Сообщение успешно отправлено в Telegram (chat_id: {chat_id})')
            return True
            
        except requests.exceptions.HTTPError as e:
            # Если чат не найден или заблокирован
            if e.response and e.response.status_code == 400:
                error_data = e.response.json()
                error_description = error_data.get('description', '')
                if 'chat not found' in error_description.lower() or 'blocked' in error_description.lower():
                    logger.warning(f'Чат {chat_id} не найден или заблокирован')
                    return False
            logger.error(f'Ошибка HTTP при отправке сообщения в Telegram (chat_id: {chat_id}): {e}')
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f'Ошибка при отправке сообщения в Telegram (chat_id: {chat_id}): {e}')
            return False
        except Exception as e:
            logger.error(f'Неожиданная ошибка при отправке сообщения в Telegram (chat_id: {chat_id}): {e}')
            return False
    
    def send_contact_request(
        self,
        name: str,
        phone: str,
        email: str = '',
        message: str = ''
    ) -> bool:
        """
        Отправляет заявку с контактной формы в Telegram всем подписчикам
        
        Args:
            name: Имя клиента
            phone: Телефон
            email: Email (опционально)
            message: Сообщение/заявка
        
        Returns:
            True если заявка отправлена хотя бы одному подписчику, False в противном случае
        """
        # Форматируем сообщение
        text = f'<b>📋 Новая заявка с сайта Avto-Декор</b>\n\n'
        text += f'<b>Имя:</b> {self._escape_html(name)}\n'
        text += f'<b>Телефон:</b> {self._escape_html(phone)}\n'
        
        if email:
            text += f'<b>Email:</b> {self._escape_html(email)}\n'
        
        text += f'\n<b>Сообщение:</b>\n{self._escape_html(message)}'
        
        # Отправляем всем подписчикам
        success_count = self.send_to_all_subscribers(text)
        return success_count > 0
    
    @staticmethod
    def _escape_html(text: str) -> str:
        """
        Экранирует HTML-символы для безопасной отправки в Telegram
        
        Args:
            text: Текст для экранирования
        
        Returns:
            Экранированный текст
        """
        if not text:
            return ''
        
        return (
            text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
        )
