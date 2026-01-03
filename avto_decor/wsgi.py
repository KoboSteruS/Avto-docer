"""
WSGI config for avto_decor project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avto_decor.settings.development')

application = get_wsgi_application()

