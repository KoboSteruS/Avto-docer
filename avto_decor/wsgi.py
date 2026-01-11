"""
WSGI config for avto_decor project.
"""
import os
from django.core.wsgi import get_wsgi_application

# Используем production настройки по умолчанию
# Для разработки можно переопределить через переменную окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avto_decor.settings.production')

application = get_wsgi_application()

