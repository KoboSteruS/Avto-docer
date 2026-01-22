"""
Management команда для запуска бота сбора новостей из Telegram канала

⚠️  DEPRECATED: Используйте run_unified_bot вместо этой команды
Эта команда оставлена для обратной совместимости и вызывает run_unified_bot
"""
import sys
from django.core.management.base import BaseCommand
from django.core.management import call_command
from loguru import logger


class Command(BaseCommand):
    """
    УСТАРЕВШАЯ команда для запуска бота сбора новостей
    
    ⚠️  Теперь используйте: python manage.py run_unified_bot --channel @your_channel
    
    Эта команда автоматически перенаправляет на новую универсальную команду
    """
    help = 'DEPRECATED: Use run_unified_bot --channel instead'
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            '--channel',
            type=str,
            help='ID или username канала (например, @avto_decor_news)',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Таймаут для long polling (по умолчанию 30 секунд)',
        )
        parser.add_argument(
            '--auto-publish',
            action='store_true',
            help='Автоматически публиковать новости',
        )
    
    def handle(self, *args, **options):
        """Перенаправляет на новую универсальную команду"""
        logger.warning('⚠️  ВНИМАНИЕ: Команда run_news_bot устарела!')
        logger.warning('⚠️  Используйте: python manage.py run_unified_bot --channel @your_channel')
        logger.info('')
        logger.info('Автоматическое перенаправление на run_unified_bot...')
        logger.info('')
        
        # Вызываем новую команду с теми же параметрами
        call_args = {
            'timeout': options['timeout']
        }
        
        if options.get('channel'):
            call_args['channel'] = options['channel']
        
        if options.get('auto_publish'):
            call_args['auto_publish'] = True
        
        call_command('run_unified_bot', **call_args)
