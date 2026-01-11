# Исправление прав доступа для Nginx

## Проблема
Nginx работает от пользователя www-data, но файлы принадлежат root. Нужно изменить владельца.

## Решение

### 1. Измените владельца всех файлов на www-data:

```bash
cd /root/Avto-docer

# Изменяем владельца
chown -R www-data:www-data staticfiles/
chown -R www-data:www-data media/
chown -R www-data:www-data static/

# Устанавливаем правильные права
chmod -R 755 staticfiles/
chmod -R 755 media/
chmod -R 755 static/

# Права на файлы
find staticfiles/ -type f -exec chmod 644 {} \;
find media/ -type f -exec chmod 644 {} \;
find static/ -type f -exec chmod 644 {} \;
```

### 2. Проверьте структуру staticfiles:

```bash
# Проверяем, что Logo.png в правильном месте
ls -la staticfiles/img/Logo.png

# Если файла нет, проверьте исходную папку static
ls -la static/img/Logo.png

# Если файл есть в static, но нет в staticfiles, пересоберите статику
source venv/bin/activate
python manage.py collectstatic --noinput --clear
```

### 3. Проверьте права на media/works:

```bash
# Проверяем права на папку works
ls -la media/works/ | head -20

# Если права неправильные, исправляем
chmod -R 755 media/works/
find media/works/ -type f -exec chmod 644 {} \;
chown -R www-data:www-data media/works/
```

### 4. Перезапустите Nginx:

```bash
systemctl restart nginx
```

### 5. Проверьте работу:

```bash
# Проверяем доступность файлов
curl -I http://195.133.49.72/static/img/Logo.png
curl -I http://195.133.49.72/media/works/phoca_thumb_l_p1070632.jpg
```

### 6. Если проблема сохраняется, проверьте SELinux:

```bash
# Проверьте статус SELinux
getenforce

# Если включен, временно отключите для теста
setenforce 0

# Или установите правильный контекст
chcon -R -t httpd_sys_content_t /root/Avto-docer/staticfiles/
chcon -R -t httpd_sys_content_t /root/Avto-docer/media/
```

### 7. Альтернатива: изменить пользователя nginx на root:

Если ничего не помогает, можно изменить пользователя nginx:

```bash
nano /etc/nginx/nginx.conf
```

Найдите строку:
```nginx
user www-data;
```

Замените на:
```nginx
user root;
```

Затем:
```bash
nginx -t
systemctl restart nginx
```

**Внимание:** Это менее безопасно, но может решить проблему с правами.
