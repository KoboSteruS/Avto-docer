"""
Команда для обновления услуги "Чип-тюнинг" с подробной информацией
"""
from django.core.management.base import BaseCommand
from services.models import Service
from loguru import logger


class Command(BaseCommand):
    """
    Команда для обновления услуги "Чип-тюнинг" с детальной информацией
    """
    help = 'Обновляет услугу "Чип-тюнинг" с подробной информацией'

    def handle(self, *args, **options):
        """
        Обновление услуги "Чип-тюнинг"
        """
        try:
            service = Service.objects.get(slug='chip-tyuning')
        except Service.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Услуга "Чип-тюнинг" не найдена. Сначала создайте её через create_services.')
            )
            return

        # Краткое описание для карточек
        short_description = (
            'Увеличение мощности и крутящего момента двигателя до 40%. Снижение расхода топлива. '
            'Безопасно для двигателя, не влияет на гарантию автомобиля.'
        )

        # Основное описание
        description = (
            'Больше мощности, больше динамики для вашего автомобиля.\n\n'
            'Чип-тюнинг автомобиля позволяет значительно улучшить характеристики двигателя без механических изменений. '
            'С помощью программной оптимизации мы увеличиваем мощность и крутящий момент двигателя до 40%, снижаем расход '
            'топлива в среднем на 1 литр на 100 км. Процедура полностью безопасна для двигателя и не влияет на гарантию автомобиля.'
        )

        # Дополнительный контент (HTML поддерживается)
        content = (
            '<h2>Преимущества чип-тюнинга</h2>\n'
            '<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">\n'
            '<div class="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg p-6 border border-red-900/20">\n'
            '<h3 class="text-xl font-bold text-red-700 mb-3">Увеличение мощности</h3>\n'
            '<p class="text-white">Увеличение мощности и крутящего момента двигателя до 40%</p>\n'
            '</div>\n'
            '<div class="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg p-6 border border-red-900/20">\n'
            '<h3 class="text-xl font-bold text-red-700 mb-3">Экономия топлива</h3>\n'
            '<p class="text-white">Снижение расхода топлива в среднем на 1 литр / 100 км</p>\n'
            '</div>\n'
            '<div class="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-lg p-6 border border-red-900/20">\n'
            '<h3 class="text-xl font-bold text-red-700 mb-3">Безопасность</h3>\n'
            '<p class="text-white">Полностью безопасен для двигателя, не влияет на гарантию автомобиля</p>\n'
            '</div>\n'
            '</div>\n\n'
            '<h2>Оборудование для чип-тюнинга</h2>\n\n'
            '<h3>MS-Chip</h3>\n'
            '<p class="text-lg font-semibold text-red-700 mb-4">Увеличит мощность двигателя</p>\n'
            '<ul class="space-y-2 mb-6">\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Увеличение мощности и крутящего момента двигателя до 30%</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Снижение расхода топлива в среднем на 15%</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Современный микропроцессор (ST Microelectronics и Atmel)</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Безопасно для двигателя, не вмешивается в работу ЭБУ</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>8 различных программ управления</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Подключение через штатные разъемы автомобиля</span>\n'
            '</li>\n'
            '</ul>\n\n'
            '<h3>MS-Chip Sport</h3>\n'
            '<p class="text-lg font-semibold text-red-700 mb-4">Еще больше мощности и возможностей</p>\n'
            '<ul class="space-y-2 mb-6">\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Увеличение мощности и крутящего момента двигателя до 40%</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Снижение расхода топлива в среднем на 15%</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Современный микропроцессор (ST Microelectronics и Atmel)</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Безопасно для двигателя, не вмешивается в работу ЭБУ</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>8 различных программ управления</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Подключение через штатные разъемы автомобиля</span>\n'
            '</li>\n'
            '</ul>\n\n'
            '<h3>MS-Chip Speed Boost</h3>\n'
            '<p class="text-lg font-semibold text-red-700 mb-4">Повысит отклик педали газа</p>\n'
            '<ul class="space-y-2 mb-6">\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Увеличение отклика педали газа</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Совместим с блоком управления MS-Chip</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Современный микропроцессор (ST Microelectronics и Atmel)</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Безопасен и полностью совместим с электроникой автомобиля</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Выбор трех режимов работы: Спорт, Спорт+ и Эко</span>\n'
            '</li>\n'
            '<li class="flex items-start gap-2">\n'
            '<span class="text-red-700 mt-1">✓</span>\n'
            '<span>Подключение через штатные разъемы автомобиля</span>\n'
            '</li>\n'
            '</ul>'
        )

        # Список направлений/услуг
        features = (
            'Увеличение мощности до 40%\n'
            'Увеличение крутящего момента до 40%\n'
            'Снижение расхода топлива на 1 л/100 км\n'
            'Безопасно для двигателя\n'
            'Не влияет на гарантию автомобиля\n'
            'MS-Chip - увеличение мощности до 30%\n'
            'MS-Chip Sport - увеличение мощности до 40%\n'
            'MS-Chip Speed Boost - улучшение отклика педали газа\n'
            'Современные микропроцессоры ST Microelectronics и Atmel\n'
            'Не вмешивается в работу ЭБУ\n'
            '8 различных программ управления\n'
            'Подключение через штатные разъемы\n'
            'Три режима работы: Спорт, Спорт+ и Эко\n'
            'Совместимость с электроникой автомобиля\n'
            'Чип-тюнинг в Петрозаводске'
        )

        # Обновляем услугу
        service.short_description = short_description
        service.description = description
        service.content = content
        service.features = features
        service.save()

        logger.info(f'Услуга "{service.title}" успешно обновлена')
        self.stdout.write(
            self.style.SUCCESS(f'Услуга "{service.title}" успешно обновлена с подробной информацией')
        )
