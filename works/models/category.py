"""
Модель категории работ
"""
from django.db import models
from django.utils.text import slugify
from core.models import BaseModel


class Category(BaseModel):
    """
    Модель категории работ
    
    Attributes:
        name: Название категории
        slug: URL-путь категории
        image: Изображение категории (превью)
        order: Порядок сортировки
        is_active: Флаг активности
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название категории',
        help_text='Название категории работ (например: Элементы салона, Рули)'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='URL-путь',
        help_text='Уникальный URL-путь для категории'
    )
    image = models.ImageField(
        upload_to='works/categories/',
        verbose_name='Изображение',
        help_text='Превью изображение категории',
        blank=True,
        null=True
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок сортировки',
        help_text='Чем меньше число, тем выше категория в списке'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Показывать категорию на сайте'
    )

    class Meta:
        verbose_name = 'Категория работ'
        verbose_name_plural = 'Категории работ'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        """
        Автоматическое создание slug из названия, если не указан
        """
        if not self.slug or self.slug.strip() == '':
            base_slug = slugify(self.name)
            if not base_slug:
                # Если slug все еще пустой (например, только спецсимволы), используем id
                base_slug = f'category-{self.id}' if self.id else 'category'
            self.slug = base_slug
        super().save(*args, **kwargs)
    
    def get_works_count(self):
        """
        Возвращает количество работ в категории
        """
        return self.works.filter(is_active=True).count()
    
    def get_random_work_image(self):
        """
        Возвращает случайное фото из активных работ категории
        
        Returns:
            Work object или None, если нет активных работ
        """
        from .work import Work
        works = self.works.filter(is_active=True)
        if works.exists():
            return works.order_by('?').first()
        return None

