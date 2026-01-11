"""
Команда для удаления пустых категорий (без работ)
"""
from django.core.management.base import BaseCommand
from works.models import Category


class Command(BaseCommand):
    """
    Удаляет категории, в которых нет ни одной работы
    """
    help = 'Удаляет категории без работ'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, какие категории будут удалены, без фактического удаления',
        )

    def handle(self, *args, **options):
        """
        Удаление пустых категорий
        """
        dry_run = options.get('dry_run', False)
        
        # Находим все категории
        all_categories = Category.objects.all()
        empty_categories = []
        
        for category in all_categories:
            works_count = category.works.count()
            if works_count == 0:
                empty_categories.append(category)
        
        if not empty_categories:
            self.stdout.write(self.style.SUCCESS('Пустых категорий не найдено'))
            return
        
        self.stdout.write(f'Найдено пустых категорий: {len(empty_categories)}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nКатегории, которые будут удалены (dry-run):'))
            for category in empty_categories:
                self.stdout.write(f'  - {category.name} (slug: {category.slug})')
            return
        
        # Удаляем пустые категории
        deleted_count = 0
        for category in empty_categories:
            category_name = category.name
            category.delete()
            deleted_count += 1
            self.stdout.write(f'Удалена категория: {category_name}')
        
        self.stdout.write(self.style.SUCCESS(f'\nУдалено категорий: {deleted_count}'))
