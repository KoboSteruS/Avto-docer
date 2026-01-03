"""
Команда для исправления пустых slug у категорий
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from works.models import Category


class Command(BaseCommand):
    """
    Команда для исправления пустых slug у категорий
    """
    help = 'Исправляет пустые slug у категорий работ'

    def handle(self, *args, **options):
        """
        Исправление пустых slug
        """
        categories = Category.objects.filter(slug='')
        fixed_count = 0

        for category in categories:
            base_slug = slugify(category.name)
            if not base_slug:
                # Если slug все еще пустой, используем id
                base_slug = f'category-{str(category.id)[:8]}'
            
            # Проверяем уникальность
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(id=category.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            category.slug = slug
            category.save()
            fixed_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Исправлена категория: {category.name} -> {slug}')
            )

        if fixed_count == 0:
            self.stdout.write(
                self.style.SUCCESS('Все категории имеют slug. Исправлений не требуется.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nГотово! Исправлено категорий: {fixed_count}')
            )

