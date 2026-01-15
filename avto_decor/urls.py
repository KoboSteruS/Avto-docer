"""
Главный URL-конфигуратор проекта Avto-Decor
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('uslugi/', include('services.urls')),
    path('', include('works.urls')),
    path('otzyvy/', include('reviews.urls')),
    path('kontakty/', include('contacts.urls')),
    path('stati/', include('articles.urls')),
]

# Статика и медиа для разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

