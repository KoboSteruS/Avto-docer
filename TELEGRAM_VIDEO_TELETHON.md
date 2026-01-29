# 🎬 Telethon Worker для скачивания больших видео

## Описание

Отдельный воркер на базе Telethon для скачивания больших видео (>20MB) из Telegram каналов. Видео скачиваются на сервер и отдаются через Django/Nginx.

---

## Архитектура

```
Пост в ТГ канале
    ↓
Bot API (run_unified_bot)
    ↓
Сохраняет:
  - telegram_channel_username
  - telegram_message_id
  - video_status = 'pending'
    ↓
Telethon Worker
    ↓
Скачивает видео через MTProto
    ↓
Сохраняет в Article.video_file
    ↓
Статус = 'ready'
    ↓
Django отдаёт <video src="/media/...">
```

---

## Установка

### 1. Установить Telethon

```bash
pip install telethon
```

Или через requirements.txt (уже добавлено):
```bash
pip install -r requirements.txt
```

### 2. Первый запуск (авторизация)

При первом запуске Telethon запросит:

1. **Номер телефона** (в формате +7XXXXXXXXXX)
2. **Код подтверждения** (придёт в Telegram)
3. **Пароль 2FA** (если включена двухфакторная аутентификация)

После авторизации создастся файл `telethon_worker/session.session` — его нужно сохранить!

---

## Использование

### Вариант 1: Django Management Command (рекомендуется)

```bash
# Одноразовая обработка
python manage.py download_pending_videos

# С лимитом
python manage.py download_pending_videos --limit 5

# В бесконечном цикле (для systemd)
python manage.py download_pending_videos --loop --interval 60
```

### Вариант 2: Прямой запуск worker

```bash
python telethon_worker/worker.py
```

---

## Systemd Unit (для production)

Создайте файл `/etc/systemd/system/telethon-video-worker.service`:

```ini
[Unit]
Description=Telethon Video Downloader Worker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Avto-docer
Environment="PATH=/root/Avto-docer/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=avto_decor.settings.production"
ExecStart=/root/Avto-docer/venv/bin/python manage.py download_pending_videos --loop --interval 300
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Команды:**

```bash
# Включить автозапуск
systemctl enable telethon-video-worker

# Запустить
systemctl start telethon-video-worker

# Проверить статус
systemctl status telethon-video-worker

# Логи
journalctl -u telethon-video-worker -f
```

---

## Статусы видео

- **`ready`** — видео готово (скачано или <20MB)
- **`pending`** — ожидает скачивания (>20MB)
- **`downloading`** — скачивается прямо сейчас
- **`error`** — ошибка при скачивании

---

## Как это работает

### 1. Бот получает видео

```python
if file_size > 20 * 1024 * 1024:  # > 20MB
    article.telegram_channel_username = channel_username
    article.telegram_message_id = message_id
    article.video_status = 'pending'
    article.save()
```

### 2. Worker обрабатывает pending

```python
# Находит все статьи со статусом 'pending'
pending = Article.objects.filter(video_status='pending')

# Скачивает через Telethon
file_path = await client.download_media(msg.media)

# Сохраняет в Django
article.video_file.save(file_name, file)
article.video_status = 'ready'
```

### 3. Сайт отдаёт видео

```django
{% if article.video_file %}
<video src="{{ article.video_file.url }}" controls></video>
{% elif article.video_status == 'pending' %}
<!-- Показываем статус "Ожидает скачивания" -->
{% endif %}
```

---

## Важные моменты

### ⚠️ Безопасность

1. **Session файл** (`telethon_worker/session.session`) — **НЕ коммитить в Git!**
2. Добавьте в `.gitignore`:
   ```
   telethon_worker/session.session
   telethon_worker/*.session
   ```

### ⚠️ Ограничения Telegram

1. **FloodWait** — если слишком много запросов, Telegram может заблокировать на время
2. **Rate limits** — не более 20-30 запросов в секунду
3. **2FA** — если включена, нужен пароль при первом запуске

### ⚠️ Хранение видео

- Видео сохраняются в `media/articles/videos/`
- Убедитесь, что есть место на диске!
- Для production лучше использовать S3 или другой объектный storage

---

## Troubleshooting

### Ошибка: "SessionPasswordNeededError"

**Решение:** Отключите 2FA в настройках Telegram или введите пароль при первом запуске.

### Ошибка: "FloodWaitError"

**Решение:** Worker автоматически возвращает статус в `pending` и попробует позже.

### Видео не скачивается

**Проверьте:**
1. Правильность `telegram_channel_username` (без @)
2. Правильность `telegram_message_id`
3. Доступность канала для вашего аккаунта
4. Логи worker: `journalctl -u telethon-video-worker -f`

---

## Мониторинг

### Проверка pending видео

```python
from articles.models import Article

pending = Article.objects.filter(video_status='pending').count()
downloading = Article.objects.filter(video_status='downloading').count()
errors = Article.objects.filter(video_status='error').count()

print(f"Pending: {pending}, Downloading: {downloading}, Errors: {errors}")
```

### Ручной перезапуск скачивания

```python
# В Django shell
from articles.models import Article

article = Article.objects.get(id='...')
article.video_status = 'pending'
article.save()
```

---

## Production рекомендации

1. **Отдельный процесс** — worker должен работать отдельно от Gunicorn
2. **Мониторинг** — настройте алерты на большое количество `error` статусов
3. **Очистка** — периодически удаляйте старые видео или переносите в архив
4. **Backup session** — сохраните `session.session` в безопасное место

---

## Следующие шаги

1. ✅ Установить Telethon
2. ✅ Создать миграцию для `video_status`
3. ✅ Запустить worker первый раз (авторизация)
4. ✅ Настроить systemd unit
5. ✅ Протестировать на реальном видео >20MB

