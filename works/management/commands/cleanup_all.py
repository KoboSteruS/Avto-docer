"""
Команда для полной очистки: удаление пустых и дублирующихся категорий
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Выполняет все операции очистки
    """
    help = 'Удаляет пустые и дублирующиеся категории'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, что будет сделано, без фактического выполнения',
        )

    def handle(self, *args, **options):
        """
        Выполнение всех операций очистки
        """
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS('Начинаем очистку...\n'))
        
        # 1. Удаление пустых категорий
        self.stdout.write(self.style.SUCCESS('1. Удаление пустых категорий'))
        self.stdout.write('-' * 50)
        call_command('cleanup_empty_categories', dry_run=dry_run)
        self.stdout.write('')
        
        # 2. Удаление дублирующихся категорий
        self.stdout.write(self.style.SUCCESS('2. Удаление дублирующихся категорий'))
        self.stdout.write('-' * 50)
        call_command('cleanup_duplicate_categories', dry_run=dry_run)
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('Очистка завершена!'))
