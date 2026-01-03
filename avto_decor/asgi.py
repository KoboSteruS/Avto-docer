"""
ASGI config for avto_decor project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avto_decor.settings.development')

application = get_asgi_application()

