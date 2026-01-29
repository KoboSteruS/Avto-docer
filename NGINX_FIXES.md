# Исправление проблем Nginx

## Проблемы

1. ❌ `robots.txt` не найден (404)
2. ❌ `favicon.ico` не найден (404)
3. ⚠️ DisallowedHost ошибки (запросы с чужих доменов)

---

## Решение

### 1. Добавить в конфигурацию Nginx (`/etc/nginx/sites-available/avto-decor.com`)

Добавьте эти блоки **ДО** основного `location /`:

```nginx
server {
    server_name www.avto-decor.com avto-decor.com;

    client_max_body_size 100M;

    # robots.txt - отдача из staticfiles
    location = /robots.txt {
        alias /root/Avto-docer/staticfiles/robots.txt;
        access_log off;
        log_not_found off;
        expires 1d;
        add_header Cache-Control "public";
    }

    # favicon.ico - отдача из staticfiles
    location = /favicon.ico {
        alias /root/Avto-docer/staticfiles/img/Logo.ico;
        access_log off;
        log_not_found off;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Статические файлы
    location /static/ {
        alias /root/Avto-docer/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Медиа файлы
    location /media/ {
        alias /root/Avto-docer/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Видео-стриминг из Telegram (ВАЖНО: должен быть ДО location /)
    location /stati/video/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Отключаем буферизацию для стриминга
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_max_temp_file_size 0;
        
        # Увеличиваем таймауты
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        
        # Запрещаем кеширование
        add_header Cache-Control "no-store, no-cache, must-revalidate";
        expires off;
    }

    # sitemap.xml
    location = /sitemap.xml {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        expires 1d;
        add_header Cache-Control "public";
    }

    # Проксирование на Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/avto-decor.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/avto-decor.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

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
    if ($host = www.avto-decor.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name www.avto-decor.com;
    return 404; # managed by Certbot
}
```

---

## 2. Проверка файлов

Убедитесь, что файлы существуют:

```bash
# Проверяем robots.txt
ls -la /root/Avto-docer/staticfiles/robots.txt

# Проверяем favicon
ls -la /root/Avto-docer/staticfiles/img/Logo.ico

# Если файлов нет, выполните collectstatic
cd /root/Avto-docer
source venv/bin/activate
python manage.py collectstatic --noinput
```

---

## 3. DisallowedHost ошибки

Эти ошибки возникают, когда кто-то пытается обратиться к серверу с других доменов (например, `selhozinstrument.ru`). 

**Вариант 1: Игнорировать (рекомендуется)**
- Это не критично, просто засоряет логи
- Nginx уже должен фильтровать такие запросы

**Вариант 2: Настроить фильтрацию в Nginx**

Добавьте в начало основного server блока:

```nginx
# Блокируем запросы с неправильными Host заголовками
if ($host !~ ^(www\.)?avto-decor\.com$) {
    return 444;  # Закрываем соединение без ответа
}
```

**Вариант 3: Настроить логирование только важных ошибок**

В `avto_decor/settings/production.py` можно настроить фильтрацию логов, но это не обязательно.

---

## 4. Применение изменений

```bash
# Проверяем конфигурацию
nginx -t

# Если всё ОК, перезапускаем Nginx
systemctl restart nginx

# Проверяем статус
systemctl status nginx
```

---

## 5. Проверка

После применения изменений проверьте:

```bash
# robots.txt
curl -I https://www.avto-decor.com/robots.txt

# favicon.ico
curl -I https://www.avto-decor.com/favicon.ico

# sitemap.xml
curl -I https://www.avto-decor.com/sitemap.xml
```

Все должны возвращать `200 OK`.

