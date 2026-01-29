"""
Админка services приложения
"""
from .service_admin import ServiceAdmin
from .service_image_admin import ServiceImageAdmin, ServiceImageInline

__all__ = ['ServiceAdmin', 'ServiceImageAdmin', 'ServiceImageInline']

