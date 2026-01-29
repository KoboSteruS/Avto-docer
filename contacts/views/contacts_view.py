"""
View для страницы контактов
"""
import json
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from contacts.forms import ContactForm
from contacts.services.telegram_service import TelegramService


class ContactsView(TemplateView):
    """
    Страница контактов с формой заявки
    """
    template_name = 'contacts/contacts.html'
    
    def get_context_data(self, **kwargs):
        """
        Добавляет форму в контекст
        """
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Обработка POST-запроса с формой заявки
        """
        form = ContactForm(request.POST)
        
        if form.is_valid():
            try:
                # Отправляем заявку в Telegram
                telegram_service = TelegramService()
                success = telegram_service.send_contact_request(
                    name=form.cleaned_data['name'],
                    phone=form.cleaned_data['phone'],
                    email=form.cleaned_data.get('email', ''),
                    message=form.cleaned_data['message']
                )
                
                if success:
                    messages.success(
                        request,
                        'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.'
                    )
                else:
                    messages.error(
                        request,
                        'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позвонить нам по телефону.'
                    )
            except Exception as e:
                messages.error(
                    request,
                    'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позвонить нам по телефону.'
                )
            
            return redirect('contacts:contacts')
        
        # Если форма невалидна, показываем ошибки
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


@require_http_methods(["POST"])
def submit_contact_form_ajax(request):
    """
    AJAX endpoint для отправки формы заявки из модального окна
    """
    form = ContactForm(request.POST)
    
    # Проверяем согласие на обработку персональных данных
    if not form.data.get('privacy_consent'):
        return JsonResponse({
            'success': False,
            'errors': {'privacy_consent': ['Необходимо согласие на обработку персональных данных']},
            'message': 'Необходимо согласие на обработку персональных данных.'
        }, status=400)
    
    if form.is_valid():
        try:
            # Отправляем заявку в Telegram
            telegram_service = TelegramService()
            success = telegram_service.send_contact_request(
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data.get('email', ''),
                message=form.cleaned_data['message']
            )
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позвонить нам по телефону.'
                }, status=500)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позвонить нам по телефону.'
            }, status=500)
    
    # Если форма невалидна, возвращаем ошибки
    errors = {}
    for field, field_errors in form.errors.items():
        errors[field] = field_errors
    
    return JsonResponse({
        'success': False,
        'errors': errors,
        'message': 'Пожалуйста, исправьте ошибки в форме.'
    }, status=400)

