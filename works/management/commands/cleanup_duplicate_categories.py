"""
Команда для удаления дублирующихся категорий
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from works.models import Category, Work


class Command(BaseCommand):
    """
    Находит и удаляет дублирующиеся категории, оставляя ту, у которой больше работ
    """
    help = 'Удаляет дублирующиеся категории, оставляя ту, у которой больше работ'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, какие категории будут удалены, без фактического удаления',
        )

    def handle(self, *args, **options):
        """
        Удаление дублирующихся категорий
        """
        dry_run = options.get('dry_run', False)
        
        # Находим категории с одинаковыми названиями (без учета регистра)
        from django.db.models import Count
        from django.db.models.functions import Lower
        
        # Группируем по названию (lowercase)
        categories_by_name = {}
        
        for category in Category.objects.all():
            name_lower = category.name.lower().strip()
            if name_lower not in categories_by_name:
                categories_by_name[name_lower] = []
            categories_by_name[name_lower].append(category)
        
        # Находим дубликаты
        duplicates = {}
        for name_lower, categories in categories_by_name.items():
            if len(categories) > 1:
                duplicates[name_lower] = categories
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS('Дублирующихся категорий не найдено'))
            return
        
        self.stdout.write(f'Найдено групп дубликатов: {len(duplicates)}')
        
        categories_to_delete = []
        categories_to_keep = []
        
        for name_lower, categories in duplicates.items():
            # Сортируем по количеству работ (убывание), затем по дате создания
            categories_sorted = sorted(
                categories,
                key=lambda c: (c.works.count(), c.created_at),
                reverse=True
            )
            
            # Оставляем первую (с наибольшим количеством работ)
            keep = categories_sorted[0]
            delete = categories_sorted[1:]
            
            categories_to_keep.append(keep)
            categories_to_delete.extend(delete)
            
            self.stdout.write(f'\nКатегория: "{categories[0].name}"')
            self.stdout.write(f'  Оставляем: {keep.name} (slug: {keep.slug}, работ: {keep.works.count()})')
            for cat in delete:
                self.stdout.write(f'  Удаляем: {cat.name} (slug: {cat.slug}, работ: {cat.works.count()})')
        
        if not categories_to_delete:
            self.stdout.write(self.style.SUCCESS('Нет категорий для удаления'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'\nБудет удалено категорий: {len(categories_to_delete)} (dry-run)'))
            return
        
        # Перемещаем работы из удаляемых категорий в оставляемые
        moved_count = 0
        deleted_count = 0
        
        for delete_cat in categories_to_delete:
            # Находим соответствующую категорию для сохранения
            name_lower = delete_cat.name.lower().strip()
            keep_cat = None
            for name, cats in duplicates.items():
                if name == name_lower:
                    keep_cat = sorted(
                        cats,
                        key=lambda c: (c.works.count(), c.created_at),
                        reverse=True
                    )[0]
                    break
            
            if keep_cat and keep_cat.id != delete_cat.id:
                # Перемещаем работы
                works = delete_cat.works.all()
                for work in works:
                    work.category = keep_cat
                    work.save()
                    moved_count += 1
                
                # Удаляем категорию
                delete_cat.delete()
                deleted_count += 1
                self.stdout.write(f'Удалена категория: {delete_cat.name} (работ перемещено: {works.count()})')
        
        self.stdout.write(self.style.SUCCESS(f'\nУдалено категорий: {deleted_count}'))
        self.stdout.write(self.style.SUCCESS(f'Перемещено работ: {moved_count}'))
