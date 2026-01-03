"""
URL-конфигурация для reviews приложения
"""
from django.urls import path
from reviews.views import ReviewsListView

app_name = 'reviews'

urlpatterns = [
    path('', ReviewsListView.as_view(), name='list'),
]

