"""
Команда для перемещения изображений работ из media/works/ в media/img/works/
"""
import os
import shutil
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from works.models import Work


class Command(BaseCommand):
    """
    Перемещает изображения работ из старого пути в новый
    """
    help = 'Перемещает изображения работ из media/works/ в media/img/works/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, какие файлы будут перемещены, без фактического перемещения',
        )

    def handle(self, *args, **options):
        """
        Перемещение изображений
        """
        dry_run = options.get('dry_run', False)
        
        media_root = Path(settings.MEDIA_ROOT)
        old_path = media_root / 'works'
        new_path = media_root / 'img' / 'works'
        
        if not old_path.exists():
            self.stdout.write(self.style.WARNING(f'Старая папка не найдена: {old_path}'))
            return
        
        # Создаем новую папку, если её нет
        if not dry_run:
            new_path.mkdir(parents=True, exist_ok=True)
        
        # Получаем все работы
        works = Work.objects.all()
        moved_count = 0
        error_count = 0
        
        self.stdout.write(f'Найдено работ: {works.count()}')
        
        for work in works:
            if not work.image:
                continue
            
            old_file_path = media_root / work.image.name
            
            if not old_file_path.exists():
                self.stdout.write(self.style.WARNING(f'Файл не найден: {old_file_path}'))
                continue
            
            # Новый путь файла
            filename = old_file_path.name
            new_file_path = new_path / filename
            
            # Если файл уже в новом месте, пропускаем
            if old_file_path.parent == new_path:
                continue
            
            if dry_run:
                self.stdout.write(f'Будет перемещен: {old_file_path} -> {new_file_path}')
                moved_count += 1
            else:
                try:
                    # Перемещаем файл
                    shutil.move(str(old_file_path), str(new_file_path))
                    
                    # Обновляем путь в модели
                    work.image.name = f'img/works/{filename}'
                    work.save()
                    
                    moved_count += 1
                    if moved_count % 10 == 0:
                        self.stdout.write(f'Перемещено файлов: {moved_count}')
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'Ошибка при перемещении {old_file_path}: {e}'))
        
        # Удаляем старую папку, если она пустая
        if not dry_run and old_path.exists():
            try:
                if not any(old_path.iterdir()):
                    old_path.rmdir()
                    self.stdout.write(f'Удалена пустая папка: {old_path}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Не удалось удалить папку {old_path}: {e}'))
        
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(self.style.WARNING(f'Будет перемещено файлов: {moved_count} (dry-run)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Перемещено файлов: {moved_count}'))
            if error_count > 0:
                self.stdout.write(self.style.ERROR(f'Ошибок: {error_count}'))
