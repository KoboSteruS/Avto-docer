# Быстрая настройка Telegram бота

## 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 2. Подписка на уведомления

### Для администраторов и сотрудников:

```bash
# Запустите бота
python manage.py run_telegram_bot

# Найдите бота в Telegram и отправьте ему /start
# Бот автоматически добавит вас в список подписчиков
```

**Команды бота:**
- `/start` - Подписаться на уведомления
- `/stop` - Отписаться
- `/status` - Проверить статус

## 3. Настройка переменных окружения

Добавьте в `.env` или установите в системе:

```bash
export TELEGRAM_BOT_TOKEN="8389210453:AAE0pUO2PflNa8UWqXWRN-SEnf8LvplsdrA"
```

**Примечание:** `TELEGRAM_CHAT_ID` больше не нужен! Список подписчиков хранится в файле `data/telegram_subscribers.json`.

## 4. Запуск бота

### Локально (для тестирования)

```bash
python manage.py run_telegram_bot
```

### На сервере (через systemd)

Создайте `/etc/systemd/system/avto-decor-telegram-bot.service`:

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
Environment="TELEGRAM_CHAT_ID=ваш_chat_id"
ExecStart=/root/Avto-docer/venv/bin/python manage.py run_telegram_bot
Restart=always
RestartSec=10

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

## 5. Проверка работы

1. Откройте страницу `/kontakty`
2. Заполните форму заявки
3. Отправьте форму
4. Проверьте Telegram - **всем подписчикам** должно прийти сообщение с заявкой

## Команды бота

- `/start` - Подписаться на уведомления
- `/stop` - Отписаться от уведомлений
- `/help` - Справка
- `/chat_id` - Показать ваш chat_id
- `/status` - Показать статус подписки

## Важно

- Заявки отправляются **всем**, кто отправил `/start`
- Список подписчиков хранится в `data/telegram_subscribers.json`
- Неактивные подписчики (заблокировали бота) автоматически удаляются
