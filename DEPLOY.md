# Инструкция по деплою на сервер

## Сервер: 195.133.49.72
## Путь: /root/Avto-docer

---

## 1. Подготовка SSH ключа

### На локальной машине:

```bash
# Генерируем SSH ключ (если еще нет)
ssh-keygen -t rsa -b 4096 -C "kaynov.roma@mail.ru"

# Копируем публичный ключ
cat ~/.ssh/id_rsa.pub
```

### На сервере (195.133.49.72):

```bash
# Подключаемся к серверу
ssh root@195.133.49.72

# Создаем директорию для ключей (если нет)
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Добавляем публичный ключ в authorized_keys
nano ~/.ssh/authorized_keys
# Вставьте содержимое вашего публичного ключа (id_rsa.pub)

# Устанавливаем правильные права
chmod 600 ~/.ssh/authorized_keys
```

---

## 2. Установка зависимостей на сервере

```bash
# Обновляем систему
apt update && apt upgrade -y

# Устанавливаем Python и pip
apt install -y python3 python3-pip python3-venv

# Устанавливаем nginx
apt install -y nginx

# Устанавливаем git (если нет)
apt install -y git

# Устанавливаем PostgreSQL (опционально, если нужна БД)
# apt install -y postgresql postgresql-contrib
```

---

## 3. Клонирование проекта через Git

```bash
# Переходим в /root
cd /root

# Клонируем репозиторий
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> Avto-docer

# Или если репозиторий приватный, используйте SSH:
# git clone git@github.com:username/avto-decor.git Avto-docer

cd Avto-docer
```

---

## 4. Настройка виртуального окружения

```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем
source venv/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Настройка переменных окружения

```bash
# Создаем файл .env в корне проекта
nano /root/Avto-docer/.env
```

**Содержимое .env:**
```env
SECRET_KEY=ваш-секретный-ключ-сгенерируйте-новый
DEBUG=False
ALLOWED_HOSTS=195.133.49.72,yourdomain.com
SECURE_SSL_REDIRECT=False
```

**Генерация SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 6. Перенос базы данных и media файлов

### На локальной машине (Windows):

**Вариант 1: Прямое копирование (если есть scp в Windows или используете Git Bash/WSL):**

```bash
# Переходим в директорию проекта
cd F:\Projects\Avto-Decor

# Копируем базу данных на сервер
scp db.sqlite3 root@195.133.49.72:/root/Avto-docer/

# Копируем папку media на сервер (рекурсивно)
scp -r media root@195.133.49.72:/root/Avto-docer/
```

**Вариант 2: Через WinSCP или FileZilla (GUI):**
- Подключитесь к серверу через SFTP
- Перетащите файл `db.sqlite3` в `/root/Avto-docer/`
- Перетащите папку `media/` в `/root/Avto-docer/`

**Вариант 3: Через PowerShell (если установлен OpenSSH):**

```powershell
# Переходим в директорию проекта
cd F:\Projects\Avto-Decor

# Копируем базу данных
scp db.sqlite3 root@195.133.49.72:/root/Avto-docer/

# Копируем media (рекурсивно)
scp -r media root@195.133.49.72:/root/Avto-docer/
```

### На сервере:

```bash
cd /root/Avto-docer
source venv/bin/activate

# Если копировали архив media, распаковываем
tar -xzf media_backup.tar.gz
rm media_backup.tar.gz

# Устанавливаем права на media
chmod -R 755 media/

# Проверяем, что БД скопировалась
ls -lh db.sqlite3

# Применяем миграции (если нужно)
python manage.py migrate

# Проверяем права на БД
chmod 644 db.sqlite3
```

---


---

## 8. Сбор статических файлов

```bash
cd /root/Avto-docer
source venv/bin/activate

# Собираем статические файлы
python manage.py collectstatic --noinput
```

---

## 9. Создание systemd сервиса для Gunicorn

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

**Команды для управления сервисом:**

```bash
# Создаем директорию для логов
mkdir -p /root/Avto-docer/logs

# Перезагружаем systemd
systemctl daemon-reload

# Запускаем сервис
systemctl start avto-decor

# Включаем автозапуск
systemctl enable avto-decor

# Проверяем статус
systemctl status avto-decor

# Просмотр логов
journalctl -u avto-decor -f
```

---

## 10. Настройка Nginx

**Создайте файл:** `/etc/nginx/sites-available/avto-decor`

```nginx
server {
    listen 80;
    server_name 195.133.49.72 yourdomain.com;

    client_max_body_size 100M;

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

    # Проксирование на Gunicorn
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

**Активируем конфигурацию:**

```bash
# Создаем символическую ссылку
ln -s /etc/nginx/sites-available/avto-decor /etc/nginx/sites-enabled/

# Удаляем дефолтный конфиг (опционально)
rm /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
nginx -t

# Перезапускаем nginx
systemctl restart nginx

# Проверяем статус
systemctl status nginx
```

---

## 11. Настройка файрвола (если нужно)

```bash
# Разрешаем HTTP и HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Включаем файрвол
ufw enable

# Проверяем статус
ufw status
```

---

## 12. Создание суперпользователя

```bash
cd /root/Avto-docer
source venv/bin/activate
python manage.py createsuperuser
```

---

## 13. Проверка работы

```bash
# Проверяем, что Gunicorn работает
curl http://127.0.0.1:8000

# Проверяем через Nginx
curl http://195.133.49.72

# Проверяем логи
tail -f /root/Avto-docer/logs/error.log
tail -f /var/log/nginx/error.log
```

---

## 14. Полезные команды для управления

```bash
# Перезапуск Gunicorn
systemctl restart avto-decor

# Перезапуск Nginx
systemctl restart nginx

# Просмотр логов Gunicorn
journalctl -u avto-decor -n 50

# Просмотр логов Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Обновление кода из Git
cd /root/Avto-docer
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart avto-decor
```

---

## 15. Настройка SSL (опционально, для HTTPS)

```bash
# Устанавливаем Certbot
apt install -y certbot python3-certbot-nginx

# Получаем сертификат
certbot --nginx -d yourdomain.com

# Автоматическое обновление
certbot renew --dry-run
```

После получения сертификата обновите `.env`:
```env
SECURE_SSL_REDIRECT=True
```

И перезапустите:
```bash
systemctl restart avto-decor
```

---

## Структура файлов на сервере

```
/root/Avto-docer/
├── .env                    # Переменные окружения
├── db.sqlite3              # База данных
├── media/                  # Медиа файлы
├── staticfiles/            # Собранные статические файлы
├── logs/                   # Логи приложения
│   ├── django.log
│   ├── access.log
│   └── error.log
└── venv/                   # Виртуальное окружение
```

---

## Troubleshooting

### Если сайт не открывается:

1. Проверьте статус сервисов:
```bash
systemctl status avto-decor
systemctl status nginx
```

2. Проверьте логи:
```bash
journalctl -u avto-decor -n 100
tail -f /var/log/nginx/error.log
```

3. Проверьте порты:
```bash
netstat -tlnp | grep 8000
netstat -tlnp | grep 80
```

4. Проверьте права доступа:
```bash
chmod -R 755 /root/Avto-docer
chown -R root:root /root/Avto-docer
```

---

## Важные замечания

- **Безопасность**: Не храните `.env` в Git, он уже в `.gitignore`
- **Бэкапы**: Регулярно делайте бэкапы БД и media файлов
- **Логи**: Регулярно проверяйте логи на ошибки
- **Обновления**: При обновлении кода всегда делайте `migrate` и `collectstatic`
