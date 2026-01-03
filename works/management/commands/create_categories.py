"""
Команда для создания всех категорий работ
"""
from django.core.management.base import BaseCommand
from works.models import Category


class Command(BaseCommand):
    """
    Команда для создания всех категорий работ
    """
    help = 'Создает все категории работ для студии Avto-Декор'

    def handle(self, *args, **options):
        """
        Создание всех категорий
        """
        categories_data = [
            'Элементы салона',
            'Рули',
            'Aston Martin',
            'Audi',
            'BMW',
            'BMW 2',
            'BMW 3',
            'BMW 4',
            'BMW X1',
            'BMW Игрушка',
            'Chevrolet',
            'Dodge',
            'Ford',
            'Ford Escape',
            'Ford Focus',
            'Honda',
            'Honda Accord',
            'Infiniti',
            'Infiniti 2',
            'KIA',
            'Mazda',
            'Mercedes 221',
            'MERCEDES W140',
            'Mers',
            'MINI Cooper',
            'Mitsubishi',
            'Opel',
            'Passat CC',
            'Pontiac',
            'Porsche Carrera',
            'Toyota Land Cruiser Prado',
            'Volvo XC90',
            'БМВ X6',
            'Волга 21',
            'Волга21',
            'Декоративные швы',
            'Мазда',
            'Мазда клеточки',
            'Мерс',
            'Мерседес',
            'Мерседес 140',
            'Мерседес C 200',
            'Мицубиси Лансер X',
            'Москвич 401',
            'Пежо',
            'Перетяжка торпедо кожей',
            'Победа',
            'Ремонт',
            'Тойота',
            'Торпедо',
            'Шкода',
        ]

        created_count = 0
        updated_count = 0

        for index, category_name in enumerate(categories_data, start=1):
            # Создаем slug из названия
            from django.utils.text import slugify
            slug = slugify(category_name)
            
            # Если slug уже существует, добавляем суффикс
            base_slug = slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            category, created = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': category_name,
                    'order': index,
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создана категория: {category.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Обновлена категория: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nГотово! Создано: {created_count}, Обновлено: {updated_count}'
            )
        )

