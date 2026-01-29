# SEO Настройка - Инструкции

## ✅ Выполнено

1. ✅ SEO мета-теги (description, keywords, og теги) добавлены в base.html
2. ✅ Модель ServiceImage для дополнительных изображений услуг создана
3. ✅ Галочка согласия на обработку персональных данных добавлена в формы
4. ✅ Страница политики конфиденциальности создана (`/privacy/`)
5. ✅ Сообщение о куки файлах добавлено
6. ✅ robots.txt создан
7. ✅ sitemap.xml создан и доступен по адресу `/sitemap.xml`
8. ✅ Страница 404 с правильным HTTP статусом настроена

## 🔧 Требуется настройка на сервере

### 1. Favicon

Создайте файлы favicon:
- `static/favicon.ico` - ICO формат (16x16, 32x32, 48x48)
- `static/favicon.svg` - SVG формат (уже создан как заглушка)
- `static/favicon.png` - PNG формат для Apple Touch Icon (180x180)

**Рекомендация**: Используйте логотип Avto-Декор для создания favicon.

### 2. Редирект с домена без www на www.avto-decor.com

Добавьте в конфигурацию Nginx (`/etc/nginx/sites-available/avto-decor.com`):

```nginx
# Редирект с домена без www на www
server {
    listen 80;
    listen 443 ssl;
    server_name avto-decor.com;
    
    ssl_certificate /etc/letsencrypt/live/avto-decor.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/avto-decor.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    return 301 https://www.avto-decor.com$request_uri;
}

server {
    listen 80;
    server_name www.avto-decor.com;
    return 301 https://www.avto-decor.com$request_uri;
}
```

**Важно**: Убедитесь, что основной server блок использует `server_name www.avto-decor.com;`

### 3. Отдача robots.txt и sitemap.xml

Добавьте в конфигурацию Nginx:

```nginx
# robots.txt
location = /robots.txt {
    alias /root/Avto-docer/staticfiles/robots.txt;
    access_log off;
    log_not_found off;
}

# sitemap.xml
location = /sitemap.xml {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 4. HTML файл для Яндекс Вебмастера

Создайте файл `yandex_VERIFICATION_CODE.html` в корне проекта (рядом с `manage.py`).

**Где взять VERIFICATION_CODE:**
1. Зайдите в Яндекс Вебмастер: https://webmaster.yandex.ru/
2. Добавьте сайт `www.avto-decor.com`
3. Выберите способ подтверждения "HTML-файл"
4. Скачайте файл или скопируйте содержимое
5. Разместите файл в корне проекта

**Настройка Nginx для отдачи HTML файла:**

```nginx
# HTML файл для Яндекс Вебмастера
location ~ ^/(yandex_[a-zA-Z0-9]+\.html|google[0-9a-f]+\.html)$ {
    root /root/Avto-docer;
    access_log off;
    log_not_found off;
}
```

## 📋 Миграции

После добавления модели `ServiceImage` выполните:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 🎯 Дальнейшие шаги

1. Создайте favicon файлы из логотипа
2. Настройте редирект в Nginx
3. Добавьте HTML файл для Яндекс Вебмастера
4. Проверьте работу sitemap.xml: https://www.avto-decor.com/sitemap.xml
5. Проверьте работу robots.txt: https://www.avto-decor.com/robots.txt
6. Добавьте дополнительные изображения для услуг через админку Django

## 📝 Примечания

- Перелинковка со старых ссылок будет настроена после анализа данных из Яндекс Вебмастера
- Все SEO мета-теги можно переопределить в дочерних шаблонах через блоки `{% block meta_description %}`, `{% block meta_keywords %}`, и т.д.

