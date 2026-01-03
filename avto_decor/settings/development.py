"""
Настройки для разработки
"""
from .base import *

DEBUG = True

# Дополнительные настройки для разработки
# debug_toolbar можно добавить позже, если нужно (не поддерживает Python 3.13)
# if DEBUG:
#     try:
#         import debug_toolbar
#         INSTALLED_APPS += ['debug_toolbar']
#         MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
#         INTERNAL_IPS = ['127.0.0.1']
#     except ImportError:
#         pass

