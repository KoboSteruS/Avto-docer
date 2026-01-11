# Быстрая инструкция по деплою

## Сервер: 195.133.49.72
## Путь проекта: /root/Avto-docer

---

## 1. Копирование файлов с локальной машины (Windows)

### Вариант A: Через Git Bash или WSL

```bash
# Переходим в директорию проекта
cd F:\Projects\Avto-Decor

# Копируем базу данных
scp db.sqlite3 root@195.133.49.72:/root/Avto-docer/

# Копируем папку media (рекурсивно)
scp -r media root@195.133.49.72:/root/Avto-docer/
```

### Вариант B: Через PowerShell (если установлен OpenSSH)

```powershell
cd F:\Projects\Avto-Decor
scp db.sqlite3 root@195.133.49.72:/root/Avto-docer/
scp -r media root@195.133.49.72:/root/Avto-docer/
```

### Вариант C: Через WinSCP или FileZilla (GUI)

1. Подключитесь к серверу через SFTP:
   - Хост: `195.133.49.72`
   - Пользователь: `root`
   - Порт: `22`

2. Перетащите файлы:
   - `db.sqlite3` → `/root/Avto-docer/`
   - Папку `media/` → `/root/Avto-docer/`

---

## 2. Systemd сервис

**Создайте файл:** `/etc/systemd/system/avto-decor.service`

```ini
[Unit]
Description=Avto-Decor Gunicorn daemon
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/Avto-docer
Environment="PATH=/root/Avto-docer/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=avto_decor.settings.production"
ExecStart=/root/Avto-docer/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --access-logfile /root/Avto-docer/logs/access.log \
    --error-logfile /root/Avto-docer/logs/error.log \
    avto_decor.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Команды:**

```bash
mkdir -p /root/Avto-docer/logs
systemctl daemon-reload
systemctl start avto-decor
systemctl enable avto-decor
systemctl status avto-decor
```

---

## 3. Nginx конфигурация

**Создайте файл:** `/etc/nginx/sites-available/avto-decor`

```nginx
server {
    listen 80;
    server_name 195.133.49.72;

    client_max_body_size 100M;

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

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

**Команды:**

```bash
ln -s /etc/nginx/sites-available/avto-decor /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # опционально
nginx -t
systemctl restart nginx
```

---

## 4. Настройка на сервере

```bash
cd /root/Avto-docer

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Создаем .env файл
nano .env
```

**Содержимое .env:**
```env
SECRET_KEY=сгенерируйте-ключ-командой-ниже
DEBUG=False
ALLOWED_HOSTS=195.133.49.72
SECURE_SSL_REDIRECT=False
```

**Генерация SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Продолжение настройки:**
```bash
# Устанавливаем права на media и БД
chmod -R 755 media/
chmod 644 db.sqlite3

# Применяем миграции
python manage.py migrate

# Собираем статические файлы
python manage.py collectstatic --noinput

# Создаем суперпользователя (если нужно)
python manage.py createsuperuser
```

---

## 5. Проверка

```bash
# Проверяем статус сервисов
systemctl status avto-decor
systemctl status nginx

# Проверяем логи
journalctl -u avto-decor -n 50
tail -f /root/Avto-docer/logs/error.log

# Проверяем работу
curl http://127.0.0.1:8000
curl http://195.133.49.72
```

---

## Полезные команды

```bash
# Перезапуск сервисов
systemctl restart avto-decor
systemctl restart nginx

# Просмотр логов
journalctl -u avto-decor -f
tail -f /var/log/nginx/error.log

# Обновление кода
cd /root/Avto-docer
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart avto-decor
```
