# Исправление ошибки 403 (Forbidden) для статических и медиа файлов

## Проблема
Nginx не может прочитать статические файлы и media из-за прав доступа.

## Решение на сервере

### 1. Установите правильные права доступа:

```bash
cd /root/Avto-docer

# Права на директории
chmod -R 755 static/
chmod -R 755 media/
chmod -R 755 staticfiles/

# Права на файлы
find static/ -type f -exec chmod 644 {} \;
find media/ -type f -exec chmod 644 {} \;
find staticfiles/ -type f -exec chmod 644 {} \;

# Убедитесь, что nginx может читать
chmod -R o+r static/
chmod -R o+r media/
chmod -R o+r staticfiles/
```

### 2. Проверьте владельца файлов:

```bash
# Должен быть root:root (или www-data:www-data, если nginx работает от этого пользователя)
ls -la /root/Avto-docer/static/
ls -la /root/Avto-docer/media/
ls -la /root/Avto-docer/staticfiles/
```

### 3. Если нужно изменить владельца на www-data:

```bash
# Проверьте, какой пользователь у nginx
ps aux | grep nginx

# Если nginx работает от www-data:
chown -R www-data:www-data /root/Avto-docer/staticfiles/
chown -R www-data:www-data /root/Avto-docer/media/
chown -R www-data:www-data /root/Avto-docer/static/

# Или оставьте root, но дайте права на чтение всем
chmod -R 755 /root/Avto-docer/staticfiles/
chmod -R 755 /root/Avto-docer/media/
chmod -R 755 /root/Avto-docer/static/
```

### 4. Проверьте конфигурацию Nginx:

Убедитесь, что в `/etc/nginx/sites-available/avto-decor` правильные пути:

```nginx
location /static/ {
    alias /root/Avto-docer/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /root/Avto-docer/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 5. Перезапустите Nginx:

```bash
nginx -t  # Проверка конфигурации
systemctl restart nginx
```

### 6. Проверьте, что файлы существуют:

```bash
ls -la /root/Avto-docer/staticfiles/img/Logo.png
ls -la /root/Avto-docer/media/
```

### 7. Если файлы не собраны, соберите статику:

```bash
cd /root/Avto-docer
source venv/bin/activate
python manage.py collectstatic --noinput
```

### 8. Проверьте SELinux (если включен):

```bash
# Проверьте статус SELinux
getenforce

# Если включен, отключите временно для теста:
setenforce 0

# Или установите правильный контекст:
chcon -R -t httpd_sys_content_t /root/Avto-docer/staticfiles/
chcon -R -t httpd_sys_content_t /root/Avto-docer/media/
```

### 9. Проверьте логи Nginx:

```bash
tail -f /var/log/nginx/error.log
```

Там должна быть информация о том, почему доступ запрещен.

### 10. Альтернативное решение - изменить пользователя nginx:

Если проблема сохраняется, можно изменить пользователя nginx в `/etc/nginx/nginx.conf`:

```nginx
user root;
```

Но это менее безопасно. Лучше правильно настроить права.
