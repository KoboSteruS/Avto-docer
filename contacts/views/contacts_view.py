"""
View для страницы контактов
"""
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
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

