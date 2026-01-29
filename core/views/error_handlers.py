"""
Обработчики ошибок (404, 500 и т.д.)
"""
from django.shortcuts import render


def handler404(request, exception):
    """
    Обработчик 404 ошибки
    Возвращает правильный HTTP статус 404
    """
    return render(request, '404.html', status=404)


def handler500(request):
    """
    Обработчик 500 ошибки
    """
    return render(request, '500.html', status=500)

