"""
Команда для импорта отзывов из JSON файла в базу данных
"""
import json
import html
import sys
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from reviews.models import Review


class Command(BaseCommand):
    help = 'Импортирует отзывы из JSON файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Путь к JSON файлу с отзывами',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, какие отзывы будут импортированы, без фактического создания',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Пропускать отзывы, которые уже существуют (по имени и тексту)',
        )
        parser.add_argument(
            '--default-rating',
            type=int,
            default=5,
            choices=[1, 2, 3, 4, 5],
            help='Рейтинг по умолчанию для отзывов без рейтинга (по умолчанию: 5)',
        )

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        dry_run = options['dry_run']
        skip_existing = options['skip_existing']
        default_rating = options['default_rating']
        
        # Настройка кодировки для вывода
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        
        # Проверяем существование файла
        json_path = Path(json_file_path)
        if not json_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {json_file_path}')
            )
            return
        
        # Читаем JSON файл
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка парсинга JSON: {e}')
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка чтения файла: {e}')
            )
            return
        
        # Ищем данные таблицы f9vru_easybook
        reviews_data = None
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get('type') == 'table' and item.get('name') == 'f9vru_easybook':
                    reviews_data = item.get('data', [])
                    break
        
        if not reviews_data:
            self.stdout.write(
                self.style.ERROR('Не найдены данные таблицы f9vru_easybook в JSON файле')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Найдено {len(reviews_data)} отзывов для импорта')
        )
        
        # Статистика
        imported = 0
        skipped = 0
        errors = 0
        
        # Обрабатываем каждый отзыв
        for idx, review_data in enumerate(reviews_data, 1):
            try:
                # Извлекаем данные
                name = review_data.get('name', '').strip()
                text = review_data.get('text', '').strip()
                created_at_str = review_data.get('created_at', '')
                
                # Пропускаем пустые отзывы
                if not name or not text:
                    self.stdout.write(
                        self.style.WARNING(f'Отзыв #{idx}: пропущен (пустое имя или текст)')
                    )
                    skipped += 1
                    continue
                
                # Декодируем HTML-сущности
                name = html.unescape(name)
                text = html.unescape(text)
                
                # Обрезаем текст до 1000 символов (ограничение модели)
                if len(text) > 1000:
                    text = text[:997] + '...'
                    self.stdout.write(
                        self.style.WARNING(f'Отзыв #{idx}: текст обрезан до 1000 символов')
                    )
                
                # Обрезаем имя до 100 символов
                if len(name) > 100:
                    name = name[:100]
                    self.stdout.write(
                        self.style.WARNING(f'Отзыв #{idx}: имя обрезано до 100 символов')
                    )
                
                # Парсим дату
                created_at = None
                if created_at_str:
                    try:
                        # Формат: "2021-07-12 07:34:13"
                        created_at = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            # Пробуем другие форматы
                            created_at = datetime.fromisoformat(created_at_str.replace(' ', 'T'))
                        except ValueError:
                            self.stdout.write(
                                self.style.WARNING(f'Отзыв #{idx}: не удалось распарсить дату "{created_at_str}", будет использована текущая дата')
                            )
                
                # Проверяем существование отзыва (если нужно)
                if skip_existing:
                    existing = Review.objects.filter(
                        name=name,
                        text__startswith=text[:100]  # Проверяем первые 100 символов
                    ).first()
                    if existing:
                        self.stdout.write(
                            self.style.WARNING(f'Отзыв #{idx}: "{name[:50]}..." уже существует, пропущен')
                        )
                        skipped += 1
                        continue
                
                if dry_run:
                    self.stdout.write(
                        f'[DRY RUN] Отзыв #{idx}: {name} - {text[:50]}... (рейтинг: {default_rating}, дата: {created_at or "текущая"})'
                    )
                    imported += 1
                else:
                    # Создаем отзыв
                    try:
                        review = Review(
                            name=name,
                            car='Не указано',  # Поле обязательное, но в старых отзывах нет
                            rating=default_rating,
                            text=text,
                            is_published=True,  # Старые отзывы сразу публикуем
                        )
                        
                        # Сохраняем отзыв
                        review.save()
                    except Exception as save_error:
                        # Если ошибка при сохранении, выводим детали
                        self.stdout.write(
                            self.style.ERROR(f'Отзыв #{idx}: ошибка при сохранении - {save_error}')
                        )
                        self.stdout.write(
                            self.style.ERROR(f'  Имя: {name[:50]}...')
                        )
                        self.stdout.write(
                            self.style.ERROR(f'  Текст: {text[:100]}...')
                        )
                        errors += 1
                        continue
                    
                    # Обновляем created_at напрямую через SQL, так как это поле auto_now_add
                    if created_at:
                        try:
                            with connection.cursor() as cursor:
                                # Конвертируем UUID в строку для SQLite
                                review_id_str = str(review.id)
                                # SQLite принимает datetime в формате ISO (YYYY-MM-DDTHH:MM:SS.ffffff)
                                created_at_iso = created_at.isoformat()
                                # Используем список для параметров (не кортеж)
                                cursor.execute(
                                    "UPDATE reviews_review SET created_at = ? WHERE id = ?",
                                    [created_at_iso, review_id_str]
                                )
                            review.refresh_from_db()
                        except Exception as sql_error:
                            # Игнорируем ошибку обновления даты, отзыв уже создан
                            pass
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Отзыв #{idx}: "{name[:50]}..." успешно импортирован')
                    )
                    imported += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Отзыв #{idx}: ошибка импорта - {e}')
                )
                errors += 1
                continue
        
        # Итоговая статистика
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS(f'Импорт завершен:'))
        self.stdout.write(f'  Импортировано: {imported}')
        self.stdout.write(f'  Пропущено: {skipped}')
        self.stdout.write(f'  Ошибок: {errors}')
        self.stdout.write('=' * 60)
