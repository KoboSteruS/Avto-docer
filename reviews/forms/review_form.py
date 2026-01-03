"""
Форма для добавления отзыва
"""
from django import forms
from reviews.models import Review


class ReviewForm(forms.ModelForm):
    """
    Форма для создания отзыва
    
    Включает валидацию полей и кастомные виджеты
    """
    
    class Meta:
        model = Review
        fields = ['name', 'car', 'rating', 'text']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700',
                'placeholder': 'Ваше имя',
                'required': True,
            }),
            'car': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700',
                'placeholder': 'Марка и модель автомобиля',
                'required': True,
            }),
            'rating': forms.HiddenInput(attrs={
                'id': 'rating-input',
                'required': True,
            }),
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700 resize-none',
                'placeholder': 'Опишите ваши впечатления от работы студии...',
                'rows': 5,
                'required': True,
            }),
        }
        labels = {
            'name': 'Ваше имя',
            'car': 'Автомобиль',
            'rating': 'Оценка',
            'text': 'Текст отзыва',
        }
        help_texts = {
            'text': 'Максимум 1000 символов',
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы с кастомными настройками
        """
        super().__init__(*args, **kwargs)
        # Rating теперь скрытое поле, управляется через JavaScript

    def clean_text(self):
        """
        Валидация текста отзыва
        """
        text = self.cleaned_data.get('text')
        if text:
            text = text.strip()
            if len(text) < 10:
                raise forms.ValidationError('Текст отзыва должен содержать минимум 10 символов')
            if len(text) > 1000:
                raise forms.ValidationError('Текст отзыва не должен превышать 1000 символов')
        return text

    def clean_name(self):
        """
        Валидация имени
        """
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError('Имя должно содержать минимум 2 символа')
            if len(name) > 100:
                raise forms.ValidationError('Имя не должно превышать 100 символов')
        return name

    def clean_car(self):
        """
        Валидация марки автомобиля
        """
        car = self.cleaned_data.get('car')
        if car:
            car = car.strip()
            if len(car) < 2:
                raise forms.ValidationError('Название автомобиля должно содержать минимум 2 символа')
            if len(car) > 100:
                raise forms.ValidationError('Название автомобиля не должно превышать 100 символов')
        return car

