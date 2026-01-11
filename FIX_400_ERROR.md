# Исправление ошибки 400 (Bad Request)

## Проблема
Ошибка 400 обычно возникает из-за:
1. Неправильно настроенного ALLOWED_HOSTS
2. SSL настройки включены без SSL сертификата
3. Отсутствует или неправильный .env файл

## Решение

### 1. Проверьте логи на сервере:

```bash
# Логи Gunicorn
tail -f /root/Avto-docer/logs/error.log

# Логи Nginx
tail -f /var/log/nginx/error.log

# Логи systemd
journalctl -u avto-decor -n 50
```

### 2. Создайте/обновите .env файл:

```bash
cd /root/Avto-docer
nano .env
```

**Содержимое .env:**
```env
SECRET_KEY=ваш-сгенерированный-ключ
DEBUG=False
ALLOWED_HOSTS=195.133.49.72,localhost,127.0.0.1
SECURE_SSL_REDIRECT=False
```

**Генерация SECRET_KEY (если еще не создан):**
```bash
source venv/bin/activate
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Обновите код на сервере:

```bash
cd /root/Avto-docer
source venv/bin/activate
git pull
```

### 4. Перезапустите сервисы:

```bash
systemctl restart avto-decor
systemctl restart nginx
```

### 5. Проверьте работу:

```bash
# Проверка локально на сервере
curl http://127.0.0.1:8000

# Проверка через Nginx
curl http://195.133.49.72
```

### 6. Если ошибка сохраняется, временно включите DEBUG:

В файле `/root/Avto-docer/.env`:
```env
DEBUG=True
```

Перезапустите:
```bash
systemctl restart avto-decor
```

Это покажет детальную информацию об ошибке в браузере.

### 7. Проверьте права доступа:

```bash
chmod -R 755 /root/Avto-docer
chmod 644 /root/Avto-docer/db.sqlite3
chmod -R 755 /root/Avto-docer/media
```

### 8. Проверьте, что Pillow установлен:

```bash
source venv/bin/activate
pip install Pillow
```

### 9. Если нужно добавить Pillow в requirements.txt:

Обновите файл на локальной машине и закоммитьте:
```txt
Django>=4.2.0,<5.0.0
loguru>=0.7.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
gunicorn>=21.2.0
Pillow>=10.0.0
```

Затем на сервере:
```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
```
