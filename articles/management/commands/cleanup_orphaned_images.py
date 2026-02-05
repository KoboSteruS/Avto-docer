"""
Команда для очистки записей ArticleImage, которые ссылаются на несуществующие статьи
"""
from django.core.management.base import BaseCommand
from articles.models import ArticleImage, Article
from loguru import logger


class Command(BaseCommand):
    help = 'Очищает записи ArticleImage, которые ссылаются на несуществующие статьи'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, что будет удалено, без фактического удаления',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        logger.info('=' * 80)
        logger.info('🧹 ОЧИСТКА ОРФАННЫХ ИЗОБРАЖЕНИЙ СТАТЕЙ')
        logger.info('=' * 80)
        
        # Находим все ArticleImage
        all_images = ArticleImage.objects.all()
        logger.info(f'Всего изображений в базе: {all_images.count()}')
        
        # Находим изображения с несуществующими статьями
        orphaned_count = 0
        orphaned_images = []
        
        for image in all_images:
            try:
                # Пытаемся получить статью
                article = image.article
                if not article:
                    orphaned_images.append(image)
                    orphaned_count += 1
            except Article.DoesNotExist:
                # Статья не существует
                orphaned_images.append(image)
                orphaned_count += 1
            except Exception as e:
                # Другая ошибка (например, article_id содержит не UUID)
                logger.warning(f'Ошибка при проверке изображения {image.id}: {e}')
                orphaned_images.append(image)
                orphaned_count += 1
        
        if orphaned_count == 0:
            logger.info('✅ Орфанных изображений не найдено')
            return
        
        logger.info('')
        logger.info(f'⚠️  Найдено орфанных изображений: {orphaned_count}')
        logger.info('')
        
        if dry_run:
            logger.info('🔍 РЕЖИМ ПРОСМОТРА (dry-run) - ничего не будет удалено')
            logger.info('')
            for image in orphaned_images[:10]:  # Показываем первые 10
                try:
                    article_id = image.article_id if hasattr(image, 'article_id') else 'N/A'
                    logger.info(f'   - Изображение ID: {image.id}, article_id: {article_id}')
                except:
                    logger.info(f'   - Изображение ID: {image.id}, article_id: ошибка получения')
            
            if orphaned_count > 10:
                logger.info(f'   ... и ещё {orphaned_count - 10} изображений')
        else:
            logger.info('🗑️  УДАЛЕНИЕ ОРФАННЫХ ИЗОБРАЖЕНИЙ...')
            logger.info('')
            
            deleted_count = 0
            for image in orphaned_images:
                try:
                    image_id = image.id
                    image.delete()
                    deleted_count += 1
                    logger.info(f'   ✅ Удалено изображение ID: {image_id}')
                except Exception as e:
                    logger.error(f'   ❌ Ошибка при удалении изображения {image.id}: {e}')
            
            logger.info('')
            logger.info(f'✅ Удалено изображений: {deleted_count} из {orphaned_count}')
        
        logger.info('')
        logger.info('=' * 80)
