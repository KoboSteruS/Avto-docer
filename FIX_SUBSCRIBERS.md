# Исправление проблемы с подписчиками Telegram бота

## Проблема

Бот не видит подписчиков, хотя они отправили `/start`.

## Диагностика

### 1. Проверьте список подписчиков

```bash
python manage.py check_subscribers
```

Эта команда покажет:
- Путь к файлу с подписчиками
- Существует ли файл
- Количество подписчиков
- Список всех chat_id

### 2. Проверьте, что бот запущен

```bash
# Проверьте процессы
ps aux | grep run_telegram_bot

# Или проверьте логи systemd
sudo journalctl -u avto-decor-telegram-bot -n 50
```

### 3. Проверьте файл подписчиков вручную

Файл должен находиться по пути: `data/telegram_subscribers.json`

```bash
# Проверьте существование файла
ls -la data/telegram_subscribers.json

# Посмотрите содержимое
cat data/telegram_subscribers.json
```

Файл должен выглядеть так:
```json
{
  "subscribers": [
    "123456789",
    "987654321"
  ]
}
```

## Решение

### Вариант 1: Бот не запущен

1. Запустите бота:
```bash
python manage.py run_telegram_bot
```

2. Отправьте боту `/start` в Telegram

3. Проверьте, что подписчик добавлен:
```bash
python manage.py check_subscribers
```

### Вариант 2: Файл не создается (проблемы с правами)

1. Создайте директорию вручную:
```bash
mkdir -p data
chmod 755 data
```

2. Создайте файл вручную (если нужно):
```bash
echo '{"subscribers": []}' > data/telegram_subscribers.json
chmod 644 data/telegram_subscribers.json
```

3. Запустите бота и отправьте `/start`

### Вариант 3: Бот запущен, но не обрабатывает команды

1. Проверьте логи бота на наличие ошибок

2. Перезапустите бота:
```bash
# Если через systemd
sudo systemctl restart avto-decor-telegram-bot

# Если через screen
screen -r telegram-bot
# Нажмите Ctrl+C для остановки
python manage.py run_telegram_bot
```

3. Отправьте боту `/start` заново

### Вариант 4: Добавление подписчиков вручную

Если нужно добавить подписчика вручную:

1. Узнайте chat_id (отправьте боту `/chat_id` или `/status`)

2. Отредактируйте файл `data/telegram_subscribers.json`:
```json
{
  "subscribers": [
    "ваш_chat_id_1",
    "ваш_chat_id_2"
  ]
}
```

3. Проверьте:
```bash
python manage.py check_subscribers
```

## Проверка работы

1. Запустите бота:
```bash
python manage.py run_telegram_bot
```

2. В другом терминале проверьте подписчиков:
```bash
python manage.py check_subscribers
```

3. Отправьте боту `/start` в Telegram

4. Снова проверьте подписчиков - должен появиться новый chat_id

5. Отправьте тестовую заявку через форму на сайте `/kontakty`

6. Проверьте Telegram - должно прийти уведомление

## Автозапуск бота на сервере

Для постоянной работы бота создайте systemd сервис:

```bash
sudo nano /etc/systemd/system/avto-decor-telegram-bot.service
```

Содержимое:
```ini
[Unit]
Description=Avto-Decor Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Avto-docer
Environment="PATH=/root/Avto-docer/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=avto_decor.settings.production"
Environment="TELEGRAM_BOT_TOKEN=8389210453:AAE0pUO2PflNa8UWqXWRN-SEnf8LvplsdrA"
ExecStart=/root/Avto-docer/venv/bin/python manage.py run_telegram_bot
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable avto-decor-telegram-bot
sudo systemctl start avto-decor-telegram-bot
sudo systemctl status avto-decor-telegram-bot
```

## Логи для отладки

Включите подробное логирование:

```bash
# В логах бота вы увидите:
# - Попытки добавления подписчиков
# - Путь к файлу подписчиков
# - Количество подписчиков
# - Список всех chat_id

# Просмотр логов systemd
sudo journalctl -u avto-decor-telegram-bot -f

# Просмотр последних 100 строк
sudo journalctl -u avto-decor-telegram-bot -n 100
```

## Частые проблемы

### Файл создается в неправильной директории

Проверьте путь к файлу:
```bash
python manage.py check_subscribers
```

Если путь неправильный, установите переменную окружения:
```bash
export TELEGRAM_SUBSCRIBERS_FILE="/правильный/путь/telegram_subscribers.json"
```

### Бот не видит команды

Убедитесь, что:
1. Бот запущен и работает
2. Вы отправляете команды правильному боту
3. В логах нет ошибок подключения к API

### Подписчики не получают сообщения

1. Проверьте, что подписчики есть в списке
2. Проверьте, что бот не заблокирован пользователями
3. Проверьте логи на наличие ошибок отправки
