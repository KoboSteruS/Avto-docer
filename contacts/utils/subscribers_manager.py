"""
Менеджер подписчиков Telegram бота
"""
import os
import json
from pathlib import Path
from typing import List, Set
from loguru import logger
from django.conf import settings


class SubscribersManager:
    """
    Управление списком подписчиков (chat_id) для Telegram бота
    
    Хранит список подписчиков в JSON файле
    """
    
    def __init__(self):
        """
        Инициализация менеджера подписчиков
        """
        # Путь к файлу с подписчиками
        subscribers_file = os.environ.get(
            'TELEGRAM_SUBSCRIBERS_FILE',
            str(Path(settings.BASE_DIR) / 'data' / 'telegram_subscribers.json')
        )
        self.subscribers_file = Path(subscribers_file)
        self.subscribers_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_subscribers(self) -> Set[str]:
        """
        Получает список всех подписчиков
        
        Returns:
            Множество chat_id подписчиков
        """
        if not self.subscribers_file.exists():
            logger.debug(f'Файл подписчиков не существует: {self.subscribers_file}')
            return set()
        
        try:
            with open(self.subscribers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                subscribers = data.get('subscribers', [])
                subscribers_set = set(str(chat_id) for chat_id in subscribers)
                logger.debug(f'Загружено {len(subscribers_set)} подписчиков из файла {self.subscribers_file}')
                return subscribers_set
        except json.JSONDecodeError as e:
            logger.error(f'Ошибка парсинга JSON файла подписчиков {self.subscribers_file}: {e}')
            return set()
        except Exception as e:
            logger.error(f'Ошибка при чтении файла подписчиков {self.subscribers_file}: {e}')
            return set()
    
    def add_subscriber(self, chat_id: str) -> bool:
        """
        Добавляет подписчика в список
        
        Args:
            chat_id: ID чата для добавления
        
        Returns:
            True если подписчик добавлен, False если уже существует
        """
        subscribers = self.get_subscribers()
        chat_id_str = str(chat_id)
        
        logger.info(f'Попытка добавить подписчика: {chat_id_str}. Текущее количество: {len(subscribers)}')
        logger.info(f'Путь к файлу: {self.subscribers_file}')
        
        if chat_id_str in subscribers:
            logger.info(f'Подписчик {chat_id_str} уже существует в списке')
            return False
        
        subscribers.add(chat_id_str)
        success = self._save_subscribers(subscribers)
        
        if success:
            logger.info(f'Подписчик {chat_id_str} успешно добавлен. Всего подписчиков: {len(subscribers)}')
        else:
            logger.error(f'Не удалось сохранить подписчика {chat_id_str}')
        
        return success
    
    def remove_subscriber(self, chat_id: str) -> bool:
        """
        Удаляет подписчика из списка
        
        Args:
            chat_id: ID чата для удаления
        
        Returns:
            True если подписчик удален, False если не найден
        """
        subscribers = self.get_subscribers()
        chat_id_str = str(chat_id)
        
        if chat_id_str not in subscribers:
            logger.info(f'Подписчик {chat_id_str} не найден')
            return False
        
        subscribers.remove(chat_id_str)
        return self._save_subscribers(subscribers)
    
    def is_subscribed(self, chat_id: str) -> bool:
        """
        Проверяет, подписан ли пользователь
        
        Args:
            chat_id: ID чата для проверки
        
        Returns:
            True если подписан, False в противном случае
        """
        subscribers = self.get_subscribers()
        return str(chat_id) in subscribers
    
    def _save_subscribers(self, subscribers: Set[str]) -> bool:
        """
        Сохраняет список подписчиков в файл
        
        Args:
            subscribers: Множество chat_id подписчиков
        
        Returns:
            True если сохранение успешно
        """
        try:
            # Убеждаемся, что директория существует
            self.subscribers_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'subscribers': sorted(list(subscribers), key=lambda x: int(x) if x.lstrip('-').isdigit() else 0)
            }
            
            # Создаем временный файл для безопасной записи
            temp_file = self.subscribers_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Атомарно заменяем старый файл новым
            temp_file.replace(self.subscribers_file)
            
            logger.info(f'Список подписчиков сохранен в {self.subscribers_file}. Всего: {len(subscribers)}')
            logger.debug(f'Подписчики: {list(subscribers)}')
            return True
            
        except Exception as e:
            logger.error(f'Ошибка при сохранении файла подписчиков {self.subscribers_file}: {e}', exc_info=True)
            return False
    
    def get_count(self) -> int:
        """
        Возвращает количество подписчиков
        
        Returns:
            Количество подписчиков
        """
        return len(self.get_subscribers())
