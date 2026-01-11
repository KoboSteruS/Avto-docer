"""
Команда для парсинга фотографий работ со старого сайта
"""
import os
import re
import time
from urllib.parse import urljoin, urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from loguru import logger

from works.models import Category, Work


class Command(BaseCommand):
    """
    Парсит фотографии работ со старого сайта avto-decor.com
    """
    help = 'Парсит фотографии работ со старого сайта и загружает их в БД'

    BASE_URL = 'https://avto-decor.com'
    CATEGORIES_URL = 'https://avto-decor.com/nashi-raboty'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.downloaded_count = 0
        self.errors_count = 0

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Пропускать категории, которые уже существуют в БД',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Задержка между запросами в секундах (по умолчанию 1.0)',
        )

    def handle(self, *args, **options):
        """
        Основной метод парсинга
        """
        skip_existing = options.get('skip_existing', False)
        delay = options.get('delay', 1.0)
        
        self.stdout.write(self.style.SUCCESS('Начинаем парсинг категорий...'))
        
        # Получаем список всех категорий
        categories = self.get_categories()
        
        if not categories:
            self.stdout.write(self.style.ERROR('Не удалось получить список категорий'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Найдено категорий: {len(categories)}'))
        
        # Обрабатываем каждую категорию
        for idx, (category_name, category_url) in enumerate(categories, 1):
            self.stdout.write(f'\n[{idx}/{len(categories)}] Обрабатываем категорию: {category_name}')
            
            # Проверяем, существует ли категория
            category_slug = self.generate_slug(category_name)
            if skip_existing:
                if Category.objects.filter(slug=category_slug).exists():
                    self.stdout.write(self.style.WARNING(f'  Категория "{category_name}" уже существует, пропускаем'))
                    continue
            
            # Создаем или получаем категорию
            category = self.get_or_create_category(category_name, category_slug)
            
            # Парсим фотографии категории
            images = self.get_category_images(category_url)
            
            if not images:
                self.stdout.write(self.style.WARNING(f'  Не найдено фотографий для категории "{category_name}"'))
                continue
            
            self.stdout.write(f'  Найдено фотографий: {len(images)}')
            
            # Скачиваем и сохраняем фотографии
            for img_idx, img_url in enumerate(images, 1):
                try:
                    self.download_and_save_image(category, img_url, img_idx)
                    self.stdout.write(f'  [{img_idx}/{len(images)}] Скачано: {os.path.basename(img_url)}')
                    time.sleep(delay)  # Задержка между запросами
                except Exception as e:
                    self.errors_count += 1
                    logger.error(f'Ошибка при скачивании {img_url}: {e}')
                    self.stdout.write(self.style.ERROR(f'  Ошибка при скачивании: {img_url}'))
            
            time.sleep(delay)  # Задержка между категориями
        
        # Итоговая статистика
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Парсинг завершен!'))
        self.stdout.write(f'Скачано фотографий: {self.downloaded_count}')
        self.stdout.write(f'Ошибок: {self.errors_count}')

    def get_categories(self):
        """
        Получает список всех категорий со страницы /nashi-raboty
        
        Returns:
            list of tuples: [(category_name, category_url), ...]
        """
        try:
            response = self.session.get(self.CATEGORIES_URL, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
        except Exception as e:
            logger.error(f'Ошибка при получении страницы категорий: {e}')
            return []
        
        soup = BeautifulSoup(response.text, 'lxml')
        categories = []
        
        # Ищем все таблицы (table)
        tables = soup.find_all('table')
        
        for table in tables:
            # В каждой таблице ищем ссылки (a)
            links = table.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Убираем число из названия, если есть (например, "Элементы салона (53)")
                category_name = re.sub(r'\s*\(\d+\)\s*$', '', text).strip()
                
                if not category_name:
                    continue
                
                # Проверяем разные форматы ссылок на категорию
                category_url = None
                
                # Формат 1: /nashi-raboty/category/8-elementy-salona
                if '/nashi-raboty/category/' in href or '/category/' in href:
                    if href.startswith('http'):
                        category_url = href
                    else:
                        category_url = urljoin(self.BASE_URL, href)
                
                # Формат 2: index.php?option=com_phocagallery&view=category&id=8:elementy-salona
                elif 'com_phocagallery' in href and 'view=category' in href:
                    if href.startswith('http'):
                        category_url = href
                    elif href.startswith('/'):
                        category_url = urljoin(self.BASE_URL, href)
                    else:
                        category_url = urljoin(self.CATEGORIES_URL, href)
                
                if category_url and category_name:
                    categories.append((category_name, category_url))
        
        # Удаляем дубликаты, сохраняя порядок
        seen = set()
        unique_categories = []
        for name, url in categories:
            if (name, url) not in seen:
                seen.add((name, url))
                unique_categories.append((name, url))
        
        return unique_categories

    def get_category_images(self, category_url):
        """
        Получает список URL всех изображений из категории
        
        Args:
            category_url: URL страницы категории
            
        Returns:
            list: Список URL изображений
        """
        try:
            response = self.session.get(category_url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
        except Exception as e:
            logger.error(f'Ошибка при получении страницы категории {category_url}: {e}')
            return []
        
        soup = BeautifulSoup(response.text, 'lxml')
        images = []
        
        # Ищем блоки phocagallery-box-file pg-box-image
        gallery_boxes = soup.find_all(class_=re.compile(r'phocagallery-box-file|pg-box-image'))
        
        for box in gallery_boxes:
            # В блоке ищем slimbox
            slimbox = box.find('a', class_=re.compile(r'slimbox'))
            if not slimbox:
                # Иногда slimbox может быть в другом месте, ищем любую ссылку с изображением
                slimbox = box.find('a', href=True)
            
            if slimbox:
                img_url = slimbox.get('href', '')
                if img_url:
                    # Если относительный URL, делаем абсолютным
                    if not img_url.startswith('http'):
                        img_url = urljoin(self.BASE_URL, img_url)
                    # Проверяем, что это действительно изображение
                    if any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                        images.append(img_url)
        
        # Если не нашли через phocagallery-box-file, ищем другие варианты
        if not images:
            # Ищем все ссылки с изображениями в галерее
            gallery_links = soup.find_all('a', href=re.compile(r'\.(jpg|jpeg|png|gif)', re.I))
            for link in gallery_links:
                img_url = link.get('href', '')
                if img_url:
                    # Проверяем, что это изображение из галереи
                    if 'phocagallery' in img_url.lower() or any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                        if not img_url.startswith('http'):
                            img_url = urljoin(self.BASE_URL, img_url)
                        images.append(img_url)
        
        # Удаляем дубликаты
        images = list(dict.fromkeys(images))
        
        return images

    def download_and_save_image(self, category, image_url, order):
        """
        Скачивает изображение и сохраняет его как Work
        
        Args:
            category: Объект Category
            image_url: URL изображения
            order: Порядок сортировки
        """
        try:
            # Скачиваем изображение
            response = self.session.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Получаем имя файла
            parsed_url = urlparse(image_url)
            filename = os.path.basename(parsed_url.path)
            
            # Если имя файла пустое или не имеет расширения, генерируем
            if not filename or '.' not in filename:
                content_type = response.headers.get('Content-Type', '')
                if 'image/jpeg' in content_type:
                    ext = '.jpg'
                elif 'image/png' in content_type:
                    ext = '.png'
                elif 'image/gif' in content_type:
                    ext = '.gif'
                else:
                    ext = '.jpg'  # По умолчанию
                filename = f'work_{category.slug}_{order}{ext}'
            
            # Проверяем, не существует ли уже такая работа
            # (проверяем по URL или имени файла)
            existing_work = Work.objects.filter(
                category=category,
                image__icontains=filename
            ).first()
            
            if existing_work:
                logger.info(f'Работа с изображением {filename} уже существует, пропускаем')
                return
            
            # Создаем ContentFile из скачанных данных
            image_content = ContentFile(response.content)
            
            # Создаем Work объект
            work = Work.objects.create(
                category=category,
                order=order,
                is_active=True
            )
            
            # Сохраняем изображение
            work.image.save(filename, image_content, save=True)
            
            self.downloaded_count += 1
            logger.info(f'Сохранено изображение: {filename} для категории {category.name}')
            
        except Exception as e:
            logger.error(f'Ошибка при скачивании изображения {image_url}: {e}')
            raise

    def get_or_create_category(self, name, slug):
        """
        Создает или получает категорию
        
        Args:
            name: Название категории
            slug: Slug категории
            
        Returns:
            Category object
        """
        category, created = Category.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'is_active': True,
                'order': 0
            }
        )
        
        if created:
            logger.info(f'Создана новая категория: {name} (slug: {slug})')
        else:
            # Обновляем название, если оно изменилось
            if category.name != name:
                category.name = name
                category.save()
        
        return category

    def generate_slug(self, name):
        """
        Генерирует slug из названия
        
        Args:
            name: Название категории
            
        Returns:
            str: Slug
        """
        base_slug = slugify(name)
        
        # Если slug пустой, используем fallback
        if not base_slug:
            base_slug = f'category-{hash(name) % 10000}'
        
        # Проверяем уникальность
        slug = base_slug
        counter = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1
        
        return slug
