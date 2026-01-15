"""
Команда для очистки кэша контент-блоков
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from core.models import ContentBlock


class Command(BaseCommand):
    """
    Команда для очистки кэша всех контент-блоков
    """
    help = 'Очищает кэш всех контент-блоков'

    def add_arguments(self, parser):
        parser.add_argument(
            '--page',
            type=str,
            help='Очистить кэш только для указанной страницы (home, about, contacts и т.д.)',
        )
        parser.add_argument(
            '--block-key',
            type=str,
            help='Очистить кэш только для указанного ключа блока',
        )

    def handle(self, *args, **options):
        """
        Очистка кэша контент-блоков
        """
        page = options.get('page')
        block_key = options.get('block_key')
        
        if page and block_key:
            # Очищаем кэш для конкретного блока
            cache_key = f'content_block:{page}:{block_key}'
            cache.delete(cache_key)
            self.stdout.write(
                self.style.SUCCESS(f'Кэш очищен для блока: {page}:{block_key}')
            )
        elif page:
            # Очищаем кэш для всех блоков страницы
            blocks = ContentBlock.objects.filter(page=page)
            cleared = 0
            for block in blocks:
                cache_key = f'content_block:{block.page}:{block.block_key}'
                if cache.delete(cache_key):
                    cleared += 1
            self.stdout.write(
                self.style.SUCCESS(f'Кэш очищен для {cleared} блоков страницы: {page}')
            )
        else:
            # Очищаем кэш для всех блоков
            blocks = ContentBlock.objects.all()
            cleared = 0
            for block in blocks:
                cache_key = f'content_block:{block.page}:{block.block_key}'
                if cache.delete(cache_key):
                    cleared += 1
            self.stdout.write(
                self.style.SUCCESS(f'Кэш очищен для {cleared} контент-блоков')
            )
