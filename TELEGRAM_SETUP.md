# 📱 Настройка Telegram уведомлений

## 🚀 Быстрая настройка

### 1. Создание Telegram бота

1. **Откройте Telegram** и найдите бота `@BotFather`
2. **Отправьте команду** `/newbot`
3. **Введите имя бота** (например: "Теннис Монитор")
4. **Введите username бота** (например: "tennis_monitor_bot")
5. **Скопируйте токен** (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Получение ID чата

1. **Найдите бота** `@userinfobot` в Telegram
2. **Отправьте любое сообщение** боту
3. **Скопируйте ваш Chat ID** (число, например: `123456789`)

### 3. Настройка конфигурации

1. **Скопируйте шаблон:**
   ```bash
   cp telegram_config_template.json telegram_config.json
   ```

2. **Отредактируйте файл** `telegram_config.json`:
   ```json
   {
     "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
     "chat_id": "123456789"
   }
   ```

### 4. Тестирование

```bash
python send_telegram_notification.py
```

Выберите опцию **3** для тестирования соединения.

## 📋 Подробная инструкция

### Шаг 1: Создание бота через BotFather

1. Откройте Telegram
2. Найдите `@BotFather` (официальный бот для создания ботов)
3. Отправьте `/start`
4. Отправьте `/newbot`
5. Введите имя для вашего бота (например: "Мой Теннис Монитор")
6. Введите username (должен заканчиваться на `bot`, например: `my_tennis_monitor_bot`)
7. Скопируйте полученный токен

**Пример диалога:**
```
Вы: /newbot
BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.
Вы: Мой Теннис Монитор
BotFather: Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.
Вы: my_tennis_monitor_bot
BotFather: Done! Congratulations on your new bot. You will find it at t.me/my_tennis_monitor_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. Use this token to access the HTTP API: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Шаг 2: Получение Chat ID

#### Способ 1: Через @userinfobot
1. Найдите `@userinfobot` в Telegram
2. Отправьте любое сообщение
3. Бот пришлет ваш Chat ID

#### Способ 2: Через @getidsbot
1. Найдите `@getidsbot` в Telegram
2. Отправьте любое сообщение
3. Скопируйте ваш ID

#### Способ 3: Через веб-версию
1. Откройте https://web.telegram.org
2. Откройте консоль браузера (F12)
3. Найдите ваш ID в данных

### Шаг 3: Настройка файла конфигурации

Создайте файл `telegram_config.json` в папке проекта:

```json
{
  "bot_token": "ВАШ_ТОКЕН_БОТА",
  "chat_id": "ВАШ_CHAT_ID"
}
```

**Пример заполненного файла:**
```json
{
  "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "chat_id": "987654321"
}
```

### Шаг 4: Проверка настройки

Запустите тест:
```bash
python send_telegram_notification.py
```

Выберите опцию **3** для проверки соединения.

## 🔧 Использование

### Автоматическая отправка уведомления о грунтовых кортах завтра в 22:00

```bash
python send_telegram_notification.py
```

Выберите опцию **1**.

### Интерактивная отправка

```bash
python send_telegram_notification.py
```

Выберите опцию **2** и следуйте инструкциям.

## 📱 Примеры уведомлений

### Уведомление о свободных грунтовых кортах в 22:00:

```
🎾 Свободные теннисные корты
📅 Дата: 2025-09-16
🏟️ Тип корта: Грунт
⏰ Время: 22
✅ Найдено: 10 свободных слотов

⏰ 22-23
  🏟️ Грунт (Корт №4)
  🏟️ Грунт (Корт №5)
  🏟️ Грунт (Корт №6)
  🏟️ Грунт (Корт №7)
  🏟️ Грунт (Корт №8)
  🏟️ Грунт (Корт №9)
  🏟️ Грунт (Корт №10)
  🏟️ Грунт (Корт №11)
  🏟️ Грунт (Корт №12)
  🏟️ Грунт (Корт №13)

🔗 Забронировать
```

## 🛠️ Расширенные настройки

### Настройка переменных окружения

Вместо файла конфигурации можно использовать переменные окружения:

```bash
export TELEGRAM_BOT_TOKEN="ваш_токен"
export TELEGRAM_CHAT_ID="ваш_chat_id"
```

### Автоматизация через cron

Добавьте в crontab для ежедневной проверки в 21:30:

```bash
crontab -e
```

Добавьте строку:
```
30 21 * * * cd /root/tennis-monitor && source venv/bin/activate && python send_telegram_notification.py <<< "1"
```

## 🐛 Устранение неполадок

### Ошибка: "Unauthorized"

**Причина:** Неверный токен бота
**Решение:** Проверьте токен в `telegram_config.json`

### Ошибка: "Chat not found"

**Причина:** Неверный Chat ID
**Решение:** Проверьте Chat ID и убедитесь, что бот добавлен в чат

### Ошибка: "Forbidden: bot was blocked by the user"

**Причина:** Бот заблокирован пользователем
**Решение:** Разблокируйте бота в Telegram

### Ошибка соединения

**Причина:** Проблемы с интернетом или блокировка Telegram
**Решение:** Проверьте интернет-соединение

## 📞 Поддержка

При возникновении проблем:
1. Проверьте правильность токена и Chat ID
2. Убедитесь, что бот не заблокирован
3. Проверьте интернет-соединение
4. Посмотрите логи в консоли

---

**Примечание:** Храните токен бота в безопасности и не публикуйте его в открытом доступе!
