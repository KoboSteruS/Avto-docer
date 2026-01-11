"""
Настройки для production
"""
from .base import *
import os

DEBUG = False

# Безопасность
# Отключаем SSL настройки, если SSL не используется
USE_SSL = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SECURE_SSL_REDIRECT = USE_SSL
SESSION_COOKIE_SECURE = USE_SSL
CSRF_COOKIE_SECURE = USE_SSL
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Разрешаем все хосты для начала (можно ограничить позже)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
