# 🚀 Развёртывание Telethon Worker на Production сервере

## Шаг 1: Установка Telethon

На сервере выполните:

```bash
cd /root/Avto-docer
source venv/bin/activate
pip install telethon
```

Или если используете requirements.txt:

```bash
pip install -r requirements.txt
```

---

## Шаг 2: Первый запуск (авторизация)

**⚠️ ВАЖНО:** Первый запуск нужно сделать вручную, чтобы пройти авторизацию!

```bash
cd /root/Avto-docer
source venv/bin/activate
python manage.py download_pending_videos --limit 1
```

Telethon запросит:
1. **Номер телефона** (формат: +7XXXXXXXXXX)
2. **Код подтверждения** (придёт в Telegram)
3. **Пароль 2FA** (если включена двухфакторная аутентификация)

После авторизации создастся файл:
```
/root/Avto-docer/telethon_worker/session.session
```

**Сохраните этот файл!** Он нужен для последующих запусков.

---

## Шаг 3: Копирование systemd unit файла

Скопируйте файл `telethon-video-worker.service` на сервер:

```bash
# На вашем локальном компьютере (если файл там)
scp telethon-video-worker.service root@ваш-сервер:/etc/systemd/system/

# Или создайте файл прямо на сервере
nano /etc/systemd/system/telethon-video-worker.service
```

Вставьте содержимое из файла `telethon-video-worker.service`.

**Проверьте пути в файле:**
- `WorkingDirectory=/root/Avto-docer` - путь к вашему проекту
- `ExecStart=/root/Avto-docer/venv/bin/python` - путь к Python в venv
- `DJANGO_SETTINGS_MODULE=avto_decor.settings.production` - ваши production настройки

---

## Шаг 4: Активация и запуск сервиса

```bash
# Перезагрузить systemd
systemctl daemon-reload

# Включить автозапуск
systemctl enable telethon-video-worker

# Запустить сервис
systemctl start telethon-video-worker

# Проверить статус
systemctl status telethon-video-worker
```

---

## Шаг 5: Проверка работы

### Просмотр логов

```bash
# Последние логи
journalctl -u telethon-video-worker -n 50

# Логи в реальном времени
journalctl -u telethon-video-worker -f

# Логи за последний час
journalctl -u telethon-video-worker --since "1 hour ago"
```

### Проверка в Django

```bash
# В Django shell
python manage.py shell

from articles.models import Article

# Проверить pending видео
pending = Article.objects.filter(video_status='pending').count()
print(f"Pending: {pending}")

# Проверить готовые видео
ready = Article.objects.filter(video_status='ready', video_file__isnull=False).count()
print(f"Ready: {ready}")

# Проверить ошибки
errors = Article.objects.filter(video_status='error').count()
print(f"Errors: {errors}")
```

---

## Управление сервисом

```bash
# Запустить
systemctl start telethon-video-worker

# Остановить
systemctl stop telethon-video-worker

# Перезапустить
systemctl restart telethon-video-worker

# Статус
systemctl status telethon-video-worker

# Отключить автозапуск
systemctl disable telethon-video-worker

# Включить автозапуск
systemctl enable telethon-video-worker
```

---

## Troubleshooting

### Проблема: Сервис не запускается

**Проверьте:**
1. Пути в systemd unit файле
2. Права доступа к файлам
3. Логи: `journalctl -u telethon-video-worker -n 100`

### Проблема: "SessionPasswordNeededError"

**Решение:** Отключите 2FA в настройках Telegram или введите пароль при первом запуске.

### Проблема: Видео не скачиваются

**Проверьте:**
1. Правильность `telegram_channel_username` (без @)
2. Правильность `telegram_message_id`
3. Доступность канала для вашего аккаунта
4. Логи: `journalctl -u telethon-video-worker -f`

### Проблема: "FloodWaitError"

**Решение:** Worker автоматически вернёт статус в `pending` и попробует позже. Это нормально.

---

## Мониторинг

### Проверка количества pending видео

```bash
# В Django shell
python manage.py shell

from articles.models import Article
pending = Article.objects.filter(video_status='pending').count()
print(f"Pending videos: {pending}")
```

### Ручной перезапуск скачивания

```bash
# В Django shell
python manage.py shell

from articles.models import Article

# Найти статью с ошибкой
article = Article.objects.filter(video_status='error').first()

# Вернуть в очередь
article.video_status = 'pending'
article.save()
```

---

## Настройка интервала

По умолчанию worker проверяет новые видео каждые 300 секунд (5 минут).

Чтобы изменить интервал, отредактируйте systemd unit:

```bash
nano /etc/systemd/system/telethon-video-worker.service
```

Измените строку:
```
ExecStart=/root/Avto-docer/venv/bin/python manage.py download_pending_videos --loop --interval 300
```

На нужный интервал (в секундах), например:
```
ExecStart=/root/Avto-docer/venv/bin/python manage.py download_pending_videos --loop --interval 60
```

Затем:
```bash
systemctl daemon-reload
systemctl restart telethon-video-worker
```

---

## Безопасность

### ⚠️ Session файл

Файл `telethon_worker/session.session` содержит данные авторизации. 

**НЕ коммитьте его в Git!** (уже добавлено в `.gitignore`)

**Сделайте backup:**
```bash
# Создать backup
cp /root/Avto-docer/telethon_worker/session.session /root/telethon-session-backup.session

# Восстановить из backup
cp /root/telethon-session-backup.session /root/Avto-docer/telethon_worker/session.session
```

---

## Готово! ✅

После выполнения всех шагов worker будет:
- ✅ Автоматически запускаться при загрузке сервера
- ✅ Проверять новые видео каждые 5 минут
- ✅ Скачивать большие видео (>20MB) из Telegram
- ✅ Автоматически перезапускаться при ошибках
- ✅ Логировать все действия

---

## Полезные команды

```bash
# Посмотреть все логи
journalctl -u telethon-video-worker

# Логи за сегодня
journalctl -u telethon-video-worker --since today

# Логи с ошибками
journalctl -u telethon-video-worker -p err

# Очистить старые логи (опционально)
journalctl --vacuum-time=7d
```

