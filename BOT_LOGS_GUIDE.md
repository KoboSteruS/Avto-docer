# 📋 Где посмотреть логи Telegram-бота

## 🔍 Проверка статуса бота

На сервере выполни:

```bash
# Проверь, какой сервис запущен
systemctl status telegram-bot
# или
systemctl status avto-decor-telegram-bot

# Посмотри все сервисы с "telegram" в названии
systemctl list-units | grep telegram
```

## 📝 Просмотр логов

### 1. Логи в реальном времени (следить за работой)

```bash
# Если сервис называется telegram-bot
journalctl -u telegram-bot -f

# Если сервис называется avto-decor-telegram-bot
journalctl -u avto-decor-telegram-bot -f
```

### 2. Последние 100 строк логов

```bash
journalctl -u telegram-bot -n 100
# или
journalctl -u avto-decor-telegram-bot -n 100
```

### 3. Логи за сегодня

```bash
journalctl -u telegram-bot --since today
# или
journalctl -u avto-decor-telegram-bot --since today
```

### 4. Только ошибки

```bash
journalctl -u telegram-bot -p err
# или
journalctl -u avto-decor-telegram-bot -p err
```

### 5. Логи за последний час

```bash
journalctl -u telegram-bot --since "1 hour ago"
# или
journalctl -u avto-decor-telegram-bot --since "1 hour ago"
```

## 🚨 Если бот не запущен

### Проверь, запущен ли процесс

```bash
# Посмотри все процессы Python
ps aux | grep python

# Посмотри процессы с "telegram" или "bot"
ps aux | grep -E "telegram|bot"
```

### Запусти бот вручную (для теста)

```bash
cd /root/Avto-docer
source venv/bin/activate

# Запусти бот с новостями
python manage.py run_unified_bot --channel @avto_decor_news --auto-publish
```

### Перезапусти systemd сервис

```bash
# Останови
systemctl stop telegram-bot
# или
systemctl stop avto-decor-telegram-bot

# Запусти
systemctl start telegram-bot
# или
systemctl start avto-decor-telegram-bot

# Проверь статус
systemctl status telegram-bot
# или
systemctl status avto-decor-telegram-bot
```

## 🔧 Проверка конфигурации сервиса

```bash
# Посмотри конфигурацию сервиса
cat /etc/systemd/system/telegram-bot.service
# или
cat /etc/systemd/system/avto-decor-telegram-bot.service
```

## ⚠️ Частые проблемы

### 1. Бот не собирает новые новости

**Причины:**
- Бот не запущен
- Бот запущен без параметра `--channel`
- Канал указан неправильно
- Бот не имеет доступа к каналу

**Решение:**
```bash
# Проверь, запущен ли бот
systemctl status telegram-bot

# Посмотри логи
journalctl -u telegram-bot -n 50

# Если бот не запущен или запущен неправильно, перезапусти:
systemctl restart telegram-bot
```

### 2. Ошибка 409 Conflict

**Причина:** Два процесса одновременно читают обновления

**Решение:**
```bash
# Останови все процессы Python
pkill -f "run_unified_bot"
pkill -f "run_telegram_bot"

# Перезапусти сервис
systemctl restart telegram-bot
```

### 3. Бот не видит новые посты

**Проверь:**
- Бот добавлен в канал как администратор (или имеет доступ)
- Канал указан правильно (с @ или без)
- В логах нет ошибок доступа

```bash
# Посмотри последние логи
journalctl -u telegram-bot -n 100 | grep -i "error\|channel\|канал"
```

## 📊 Полезные команды

```bash
# Посмотреть все логи за последние 24 часа
journalctl -u telegram-bot --since "24 hours ago"

# Поиск по логам
journalctl -u telegram-bot | grep "новость\|пост\|channel"

# Экспорт логов в файл
journalctl -u telegram-bot --since "1 day ago" > bot_logs.txt
```
