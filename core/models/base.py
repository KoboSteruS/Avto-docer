"""
Базовая модель с общими полями
"""
import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Базовая модель с общими полями для всех моделей проекта.
    Содержит uuid, created_at и updated_at.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

