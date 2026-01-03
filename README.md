# Avto-Decor - Студия Автомобильного Интерьера

Многостраничный сайт на Django для студии автомобильного тюнинга Avto-Декор.

## Описание

Сайт представляет собой редизайн существующего сайта с сохранением всех роутеров и структуры. Реализован на Django с использованием современного дизайна в темной теме с красными акцентами.

## Структура проекта

```
avto_decor/
├── avto_decor/          # Основной проект
│   ├── settings/        # Настройки (base, development, production)
│   ├── urls.py          # Главный URL-конфигуратор
│   └── wsgi.py          # WSGI конфигурация
├── core/                # Основное приложение (главная, о студии)
├── services/            # Приложение услуг
├── works/               # Приложение работ
├── reviews/             # Приложение отзывов
├── contacts/            # Приложение контактов
├── templates/           # Шаблоны
└── static/              # Статические файлы
```

## Роутеры

### Основные страницы:
- `/` - Главная страница
- `/uslugi` - Список услуг
- `/nashi-raboty` - Наши работы
- `/otzyvy` - Отзывы
- `/o-studii` - О студии
- `/kontakty` - Контакты

### Страницы услуг:
- `/uslugi/avtotyuning`
- `/uslugi/akvaprint`
- `/uslugi/aerografiya`
- `/uslugi/vosstanovlenie-air-bag`
- `/uslugi/dekorativnaya-otdelka-salona`
- `/uslugi/detejling`
- `/uslugi/zolocheni`
- `/uslugi/kozhgalantereya`
- `/uslugi/nanokeramika`
- `/uslugi/music`
- `/uslugi/pereoborudovanie-salonov`
- `/uslugi/peretyazhka-salona`
- `/uslugi/polirovka-avtomobilya`
- `/uslugi/restavratsiya-mebeli`
- `/uslugi/signalizatsiya`
- `/uslugi/ustanovka-podogreva-sidenij-i-rulya`
- `/uslugi/ustanovka-predvpuskovogo-podogrevatelya-dvigatelya`
- `/uslugi/flokirovaniy`
- `/uslugi/hrom`
- `/uslugi/prof-khimchistka`
- `/uslugi/chip-tyuning`
- `/uslugi/vibro-shumoizolyatsiya`

## Установка

1. Клонируйте репозиторий или создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Примените миграции:
```bash
python manage.py migrate
```

4. Создайте суперпользователя (опционально):
```bash
python manage.py createsuperuser
```

5. Запустите сервер разработки:
```bash
python manage.py runserver
```

Сайт будет доступен по адресу: http://127.0.0.1:8000/

## Переменные окружения

Для production создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## Особенности

- **BaseModel**: Все модели наследуются от BaseModel с полями uuid, created_at, updated_at
- **Модульная структура**: Каждое приложение имеет свою структуру (models/, views/, urls.py)
- **Современный дизайн**: Темная тема с красными акцентами, градиенты, адаптивная верстка
- **Tailwind CSS**: Используется через CDN для быстрой разработки
- **Русскоязычный интерфейс**: Все тексты на русском языке

## Функционал

### Отзывы
- Пользователи могут оставлять отзывы через форму на странице `/otzyvy`
- Отзывы требуют модерации перед публикацией (поле `is_published`)
- В админ-панели можно управлять отзывами: публиковать, скрывать, редактировать
- Автоматический расчет среднего рейтинга на основе опубликованных отзывов

### Админ-панель
Для доступа к админ-панели создайте суперпользователя:
```bash
python manage.py createsuperuser
```

Затем перейдите на `/admin/` и войдите с созданными учетными данными.

## Следующие шаги

1. Наполнение контентом страниц услуг
2. Добавление моделей для услуг и работ
3. Добавление функционала фильтрации работ
4. Форма обратной связи
5. Интеграция карты (Yandex Maps / Google Maps)

## Технологии

- Django 4.2+
- Python 3.8+
- Tailwind CSS (CDN)
- SQLite (для разработки)

## Лицензия

Проект разработан для студии Avto-Декор.

