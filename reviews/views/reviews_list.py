"""
View для списка отзывов
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from loguru import logger
from reviews.models import Review
from reviews.forms import ReviewForm


class ReviewsListView(View):
    """
    Страница со списком отзывов с возможностью добавления нового отзыва
    
    Обрабатывает GET и POST запросы:
    - GET: отображает список опубликованных отзывов и форму
    - POST: сохраняет новый отзыв в БД (требует модерации)
    """
    template_name = 'reviews/reviews_list.html'
    
    def get(self, request):
        """
        Обработка GET запроса - отображение отзывов и формы
        """
        try:
            # Получаем только опубликованные отзывы
            reviews = Review.objects.filter(is_published=True)
            
            # Вычисляем средний рейтинг
            average_rating = 0.0
            total_reviews = reviews.count()
            
            if total_reviews > 0:
                total_rating = sum(review.rating for review in reviews)
                average_rating = round(total_rating / total_reviews, 1)
            else:
                average_rating = 0.0
            
            # Создаем пустую форму
            form = ReviewForm()
            
            context = {
                'reviews': reviews,
                'average_rating': average_rating,
                'total_reviews': total_reviews,
                'form': form,
            }
            
            return render(request, self.template_name, context)
            
        except Exception as e:
            logger.error(f'Ошибка при получении отзывов: {e}')
            messages.error(request, 'Произошла ошибка при загрузке отзывов. Попробуйте позже.')
            return render(request, self.template_name, {
                'reviews': Review.objects.none(),
                'average_rating': 0,
                'total_reviews': 0,
                'form': ReviewForm(),
            })
    
    def post(self, request):
        """
        Обработка POST запроса - сохранение нового отзыва
        """
        try:
            form = ReviewForm(request.POST)
            
            if form.is_valid():
                # Сохраняем отзыв (по умолчанию не опубликован, требует модерации)
                review = form.save(commit=False)
                review.is_published = False  # Требует модерации
                review.save()
                
                logger.info(f'Создан новый отзыв от {review.name} для автомобиля {review.car}')
                messages.success(
                    request,
                    'Спасибо за ваш отзыв! Он будет опубликован после модерации.'
                )
                return redirect('reviews:list')
            else:
                # Форма невалидна - показываем ошибки
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
                
        except Exception as e:
            logger.error(f'Ошибка при сохранении отзыва: {e}')
            messages.error(request, 'Произошла ошибка при сохранении отзыва. Попробуйте позже.')
        
        # Если форма невалидна или произошла ошибка - показываем форму с ошибками
        try:
            reviews = Review.objects.filter(is_published=True)
            total_reviews = reviews.count()
            average_rating = 0
            if total_reviews > 0:
                total_rating = sum(review.rating for review in reviews)
                average_rating = round(total_rating / total_reviews, 1)
            else:
                average_rating = 0.0
        except Exception:
            reviews = Review.objects.none()
            total_reviews = 0
            average_rating = 0.0
        
        context = {
            'reviews': reviews,
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'form': form if 'form' in locals() else ReviewForm(),
        }
        
        return render(request, self.template_name, context)

