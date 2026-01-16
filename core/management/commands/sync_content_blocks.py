"""
Команда для синхронизации контент-блоков из шаблонов в базу данных
Автоматически находит все вызовы get_content в шаблонах и создает недостающие блоки
"""
import re
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from core.models import ContentBlock


class Command(BaseCommand):
    help = 'Синхронизирует контент-блоки из шаблонов в базу данных. Находит все вызовы get_content и создает недостающие блоки.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, какие блоки будут созданы, без фактического создания',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Обновить существующие блоки значениями по умолчанию из шаблонов',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        update = options['update']
        
        # Находим все шаблоны
        template_dirs = []
        template_dirs.append(Path(settings.BASE_DIR) / 'templates')
        
        # Также добавляем шаблоны из приложений
        for app in settings.INSTALLED_APPS:
            if not app.startswith('django.'):
                app_path = Path(settings.BASE_DIR) / app
                templates_path = app_path / 'templates'
                if templates_path.exists():
                    template_dirs.append(templates_path)
        
        # Паттерн для поиска вызовов get_content
        # {% get_content 'page' 'block_key' 'default_value' %}
        # Поддерживаем как одинарные, так и двойные кавычки
        # И многострочные значения
        pattern = r"{%\s*get_content\s+(['\"])([^'\"]+)\1\s+(['\"])([^'\"]+)\3\s+(['\"])(.*?)\5\s*%}"
        
        found_blocks = {}
        
        self.stdout.write('Поиск контент-блоков в шаблонах...\n')
        
        # Ищем все шаблоны
        for template_dir in template_dirs:
            if not template_dir.exists():
                continue
                
            for template_file in template_dir.rglob('*.html'):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Ищем все вызовы get_content
                    matches = re.finditer(pattern, content, re.DOTALL | re.MULTILINE)
                    
                    for match in matches:
                        page = match.group(2)
                        block_key = match.group(4)
                        default_content = match.group(6)
                        
                        # Очищаем default_content от HTML-тегов для определения is_html
                        has_html = bool(re.search(r'<[^>]+>', default_content))
                        
                        # Создаем ключ для уникальности
                        unique_key = f"{page}:{block_key}"
                        
                        if unique_key not in found_blocks:
                            found_blocks[unique_key] = {
                                'page': page,
                                'block_key': block_key,
                                'content': default_content,
                                'is_html': has_html,
                                'description': self._generate_description(page, block_key),
                                'template': str(template_file.relative_to(settings.BASE_DIR))
                            }
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Ошибка при чтении {template_file}: {e}')
                    )
        
        self.stdout.write(f'\nНайдено блоков в шаблонах: {len(found_blocks)}\n')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('РЕЖИМ ПРОВЕРКИ (dry-run). Блоки не будут созданы.\n'))
        
        created = 0
        updated = 0
        skipped = 0
        
        # Проверяем и создаем блоки
        for unique_key, block_data in sorted(found_blocks.items()):
            page = block_data['page']
            block_key = block_data['block_key']
            
            # Проверяем, существует ли блок
            try:
                existing_block = ContentBlock.objects.get(page=page, block_key=block_key)
                
                # Всегда обновляем описание, если его нет
                needs_update = False
                if not existing_block.description:
                    existing_block.description = block_data['description']
                    needs_update = True
                
                if update:
                    # Обновляем содержимое и HTML флаг
                    existing_block.content = block_data['content']
                    existing_block.is_html = block_data['is_html']
                    needs_update = True
                
                if needs_update:
                    existing_block.save()
                    updated += 1
                    self.stdout.write(
                        self.style.WARNING(f'[~] Обновлен: {page}:{block_key} ({block_data["template"]})')
                    )
                else:
                    skipped += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[=] Уже существует: {page}:{block_key}')
                    )
            except ContentBlock.DoesNotExist:
                # Создаем новый блок
                if not dry_run:
                    ContentBlock.objects.create(
                        page=page,
                        block_key=block_key,
                        content=block_data['content'],
                        is_html=block_data['is_html'],
                        description=block_data['description']
                    )
                    created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[+] Создан: {page}:{block_key} ({block_data["template"]})')
                    )
                else:
                    created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[DRY-RUN] Будет создан: {page}:{block_key} ({block_data["template"]})')
                    )
        
        # Итоговая статистика
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(self.style.WARNING(f'РЕЖИМ ПРОВЕРКИ'))
            self.stdout.write(f'Будет создано: {created}')
            self.stdout.write(f'Уже существует: {skipped}')
            self.stdout.write(self.style.WARNING('\nЗапустите без --dry-run для создания блоков'))
        else:
            self.stdout.write(self.style.SUCCESS(f'[+] Создано: {created}'))
            if update:
                self.stdout.write(self.style.WARNING(f'↻ Обновлено: {updated}'))
            self.stdout.write(f'Пропущено (уже существует): {skipped}')
            self.stdout.write(f'Всего обработано: {created + updated + skipped}')
        
        self.stdout.write('='*60)

    def _generate_description(self, page, block_key):
        """Генерирует описание блока на основе page и block_key"""
        # Маппинг страниц
        page_names = {
            'home': 'Главная',
            'about': 'О студии',
            'contacts': 'Контакты',
            'services': 'Услуги',
            'works': 'Наши работы',
            'reviews': 'Отзывы',
        }
        
        page_name = page_names.get(page, page)
        
        # Маппинг ключей на понятные названия
        key_names = {
            'hero_title': 'Заголовок hero-секции',
            'hero_subtitle': 'Подзаголовок hero-секции',
            'title': 'Заголовок страницы',
            'subtitle': 'Подзаголовок страницы',
            'about_text': 'Текст о компании',
            'about_text_1': 'Текст о компании (часть 1)',
            'about_text_2': 'Текст о компании (часть 2)',
            'about_subtitle': 'Подзаголовок о компании',
            'about_description': 'Описание о компании',
            'main_title': 'Основной заголовок',
            'main_subtitle': 'Основной подзаголовок',
            'info_title': 'Заголовок информации',
            'form_title': 'Заголовок формы',
            'find_title': 'Заголовок "Как нас найти"',
            'find_text': 'Текст "Как нас найти"',
            'cta_title': 'Заголовок призыва к действию',
            'cta_text': 'Текст призыва к действию',
            'coating_benefits_title': 'Заголовок преимуществ покрытий',
            'additional_services_title': 'Заголовок дополнительных услуг',
            'parts_order_title': 'Заголовок заказа запчастей',
            'parts_order_text': 'Текст заказа запчастей',
            'service_cta_title': 'Заголовок CTA услуги',
            'service_cta_text': 'Текст CTA услуги',
            'about_title': 'Заголовок "О услуге"',
            'details_title': 'Заголовок "Подробнее"',
            'features_title': 'Заголовок "Включает направления"',
            'advantages_title': 'Заголовок "Преимущества"',
        }
        
        key_name = key_names.get(block_key, block_key.replace('_', ' ').title())
        
        return f'{page_name} - {key_name}'
