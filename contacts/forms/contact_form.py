"""
Форма для заявки с контактной страницы
"""
import re
from django import forms


class ContactForm(forms.Form):
    """
    Форма для отправки заявки через контактную страницу
    
    Поля:
    - name: Имя клиента
    - phone: Телефон
    - email: Email (опционально)
    - message: Сообщение/заявка
    """
    
    name = forms.CharField(
        max_length=100,
        label='Ваше имя',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700',
            'placeholder': 'Введите ваше имя',
            'required': True,
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700',
            'placeholder': '+7 (999) 123-45-67',
            'required': True,
            'type': 'tel',
        })
    )
    
    email = forms.EmailField(
        required=False,
        label='Email (необязательно)',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700',
            'placeholder': 'example@mail.ru',
        })
    )
    
    message = forms.CharField(
        max_length=1000,
        label='Сообщение',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700 resize-none',
            'placeholder': 'Опишите вашу заявку или вопрос...',
            'rows': 5,
            'required': True,
        })
    )
    
    privacy_consent = forms.BooleanField(
        required=True,
        label='Согласие на обработку персональных данных',
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-red-700 bg-gray-800 border-gray-700 rounded focus:ring-red-700 focus:ring-2',
            'required': True,
        })
    )
    
    def clean_name(self):
        """
        Валидация имени
        Запрещает ссылки и подозрительные символы
        """
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError('Имя должно содержать минимум 2 символа')
            if len(name) > 100:
                raise forms.ValidationError('Имя не должно превышать 100 символов')
            
            # Проверка на наличие ссылок в имени
            url_patterns = [
                r'https?://',
                r'www\.',
                r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',
                r'<a\s+href',
                r'href\s*=',
            ]
            
            for pattern in url_patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    raise forms.ValidationError('Имя не должно содержать ссылки')
        
        return name
    
    def clean_phone(self):
        """
        Валидация телефона
        """
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = phone.strip()
            # Удаляем все символы кроме цифр и +
            phone_clean = ''.join(c for c in phone if c.isdigit() or c == '+')
            if len(phone_clean) < 10:
                raise forms.ValidationError('Введите корректный номер телефона')
        return phone
    
    def clean_message(self):
        """
        Валидация сообщения
        Запрещает ссылки и HTML-теги
        """
        message = self.cleaned_data.get('message')
        if message:
            message = message.strip()
            if len(message) < 10:
                raise forms.ValidationError('Сообщение должно содержать минимум 10 символов')
            if len(message) > 1000:
                raise forms.ValidationError('Сообщение не должно превышать 1000 символов')
            
            # Проверка на наличие ссылок (http, https, www, .com, .ru и т.д.)
            url_patterns = [
                r'https?://',  # http:// или https://
                r'www\.',      # www.
                r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',  # домены типа example.com, site.ru
                r'<a\s+href',  # HTML-теги ссылок
                r'href\s*=',   # атрибут href
            ]
            
            for pattern in url_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    raise forms.ValidationError(
                        'В сообщении запрещены ссылки. Пожалуйста, опишите ваш вопрос без ссылок.'
                    )
            
            # Проверка на HTML-теги
            if re.search(r'<[^>]+>', message):
                raise forms.ValidationError(
                    'В сообщении запрещены HTML-теги. Пожалуйста, используйте только обычный текст.'
                )
        
        return message
