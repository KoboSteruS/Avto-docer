"""
Management команда для проверки подписчиков Telegram бота
"""
from django.core.management.base import BaseCommand
from loguru import logger
from contacts.utils import SubscribersManager
from pathlib import Path


class Command(BaseCommand):
    """
    Команда для проверки списка подписчиков
    """
    help = 'Проверяет список подписчиков Telegram бота'
    
    def handle(self, *args, **options):
        """
        Основной метод команды
        """
        subscribers_manager = SubscribersManager()
        
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('Проверка подписчиков Telegram бота'))
        self.stdout.write('=' * 60)
        
        # Информация о файле
        subscribers_file = subscribers_manager.subscribers_file
        self.stdout.write(f'\nФайл подписчиков: {subscribers_file}')
        self.stdout.write(f'Файл существует: {subscribers_file.exists()}')
        
        if subscribers_file.exists():
            try:
                file_size = subscribers_file.stat().st_size
                self.stdout.write(f'Размер файла: {file_size} байт')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при получении размера файла: {e}'))
        
        # Список подписчиков
        subscribers = subscribers_manager.get_subscribers()
        count = len(subscribers)
        
        self.stdout.write(f'\nВсего подписчиков: {count}')
        
        if subscribers:
            self.stdout.write('\nСписок подписчиков:')
            for i, chat_id in enumerate(sorted(subscribers), 1):
                self.stdout.write(f'  {i}. {chat_id}')
        else:
            self.stdout.write(self.style.WARNING('\nПодписчиков нет!'))
            self.stdout.write('\nДля добавления подписчиков:')
            self.stdout.write('  1. Запустите бота: python manage.py run_telegram_bot')
            self.stdout.write('  2. Найдите бота в Telegram')
            self.stdout.write('  3. Отправьте боту команду /start')
        
        self.stdout.write('\n' + '=' * 60)
