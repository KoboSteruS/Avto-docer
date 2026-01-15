"""
Команда для массовой загрузки контент-блоков в БД
"""
from django.core.management.base import BaseCommand
from core.models import ContentBlock


class Command(BaseCommand):
    help = 'Загружает контент-блоки в БД'

    def handle(self, *args, **options):
        # Список всех контент-блоков
        blocks = [
            # Главная страница
            {'page': 'home', 'block_key': 'about_subtitle', 'content': '🚗 Детейлинг в <span class="text-red-700">Авто-Декор</span>', 'is_html': True, 'description': 'Заголовок секции "О компании"'},
            {'page': 'home', 'block_key': 'about_description', 'content': 'Ваш автомобиль будет как <strong class="text-white">новый</strong>!', 'is_html': True, 'description': 'Описание в секции "О компании"'},
            
            # О студии
            {'page': 'about', 'block_key': 'main_title', 'content': '🚗 Детейлинг в <span class="text-red-700">Авто-Декор</span> — ваш автомобиль будет как новый!', 'is_html': True, 'description': 'Главный заголовок'},
            {'page': 'about', 'block_key': 'main_subtitle', 'content': 'Мы предлагаем <strong class="text-white">профессиональный детейлинг</strong> вашего автомобиля!', 'is_html': True, 'description': 'Подзаголовок'},
            
            # Контакты
            {'page': 'contacts', 'block_key': 'title', 'content': 'Контакты', 'is_html': False, 'description': 'Заголовок страницы'},
            {'page': 'contacts', 'block_key': 'subtitle', 'content': 'Свяжитесь с нами удобным способом', 'is_html': False, 'description': 'Подзаголовок'},
            {'page': 'contacts', 'block_key': 'info_title', 'content': 'Контактная информация', 'is_html': False, 'description': 'Заголовок контактов'},
            {'page': 'contacts', 'block_key': 'form_title', 'content': 'Оставить заявку', 'is_html': False, 'description': 'Заголовок формы'},
            {'page': 'contacts', 'block_key': 'find_title', 'content': 'Как нас найти', 'is_html': False, 'description': 'Заголовок "Как нас найти"'},
            {'page': 'contacts', 'block_key': 'find_text', 'content': 'Мы находимся по адресу...', 'is_html': False, 'description': 'Текст про расположение'},
            {'page': 'contacts', 'block_key': 'cta_title', 'content': 'Готовы обсудить ваш проект?', 'is_html': False, 'description': 'Заголовок CTA'},
            {'page': 'contacts', 'block_key': 'cta_text', 'content': 'Свяжитесь с нами для консультации', 'is_html': False, 'description': 'Текст CTA'},
            
            # Услуги
            {'page': 'services', 'block_key': 'title', 'content': 'Наши <span class="text-red-700">Услуги</span>', 'is_html': True, 'description': 'Заголовок страницы'},
            {'page': 'services', 'block_key': 'subtitle', 'content': 'Мы предлагаем полный спектр услуг по тюнингу и улучшению автомобильного интерьера', 'is_html': False, 'description': 'Подзаголовок'},
            {'page': 'services', 'block_key': 'cta_title', 'content': 'Нужна консультация?', 'is_html': False, 'description': 'Заголовок CTA'},
            {'page': 'services', 'block_key': 'cta_text', 'content': 'Свяжитесь с нами для подробной консультации и расчета стоимости услуг', 'is_html': False, 'description': 'Текст CTA'},
            {'page': 'services', 'block_key': 'about_title', 'content': 'О <span class="text-red-700">услуге</span>', 'is_html': True, 'description': 'Заголовок "О услуге"'},
            {'page': 'services', 'block_key': 'details_title', 'content': 'Подробнее об <span class="text-red-700">услуге</span>', 'is_html': True, 'description': 'Заголовок "Подробнее"'},
            {'page': 'services', 'block_key': 'features_title', 'content': 'Включает <span class="text-red-700">направления</span>', 'is_html': True, 'description': 'Заголовок "Включает"'},
            {'page': 'services', 'block_key': 'advantages_title', 'content': 'Преимущества <span class="text-red-700">услуги</span>', 'is_html': True, 'description': 'Заголовок "Преимущества"'},
            {'page': 'services', 'block_key': 'service_cta_title', 'content': 'Заинтересовала услуга?', 'is_html': False, 'description': 'Заголовок CTA на странице услуги'},
            {'page': 'services', 'block_key': 'service_cta_text', 'content': 'Свяжитесь с нами для консультации и расчета стоимости', 'is_html': False, 'description': 'Текст CTA на странице услуги'},
            
            # Статьи
            {'page': 'articles', 'block_key': 'title', 'content': 'Наши <span class="text-red-700">Статьи</span>', 'is_html': True, 'description': 'Заголовок страницы'},
            {'page': 'articles', 'block_key': 'subtitle', 'content': 'Полезные статьи о тюнинге, уходе за автомобилем и новинках индустрии', 'is_html': False, 'description': 'Подзаголовок'},
            {'page': 'articles', 'block_key': 'related_title', 'content': 'Похожие <span class="text-red-700">статьи</span>', 'is_html': True, 'description': 'Заголовок похожих статей'},
            
            # Наши работы
            {'page': 'works', 'block_key': 'title', 'content': 'Наши <span class="text-red-700">Работы</span>', 'is_html': True, 'description': 'Заголовок страницы'},
            {'page': 'works', 'block_key': 'subtitle', 'content': 'Примеры наших работ по тюнингу и улучшению автомобилей', 'is_html': False, 'description': 'Подзаголовок'},
            
            # Отзывы
            {'page': 'reviews', 'block_key': 'title', 'content': 'Отзывы <span class="text-red-700">Клиентов</span>', 'is_html': True, 'description': 'Заголовок страницы'},
            {'page': 'reviews', 'block_key': 'subtitle', 'content': 'Мнения наших клиентов о качестве работы студии Avto-Декор', 'is_html': False, 'description': 'Подзаголовок'},
            {'page': 'reviews', 'block_key': 'form_title', 'content': 'Оставить отзыв', 'is_html': False, 'description': 'Заголовок формы'},
            {'page': 'reviews', 'block_key': 'cta_title', 'content': 'Станьте нашим клиентом', 'is_html': False, 'description': 'Заголовок CTA'},
            {'page': 'reviews', 'block_key': 'cta_text', 'content': 'Присоединяйтесь к сотням довольных клиентов студии Avto-Декор', 'is_html': False, 'description': 'Текст CTA'},
        ]
        
        created = 0
        updated = 0
        
        for block_data in blocks:
            block, created_flag = ContentBlock.objects.update_or_create(
                page=block_data['page'],
                block_key=block_data['block_key'],
                defaults={
                    'content': block_data['content'],
                    'is_html': block_data.get('is_html', False),
                    'description': block_data.get('description', ''),
                }
            )
            
            if created_flag:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Создан: {block}'))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f'↻ Обновлен: {block}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nГотово! Создано: {created}, Обновлено: {updated}'))
