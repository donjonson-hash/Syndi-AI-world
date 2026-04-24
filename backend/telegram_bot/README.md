# Syndi Telegram Bot

## Запуск

1. Создать бота через @BotFather в Telegram
2. Добавить токен в `.env`: `SYNDI_TELEGRAM_TOKEN=...`
3. Запустить:

```bash
cd backend
source venv/bin/activate
python telegram_bot/bot.py
```

## Команды

- `/start` — приветствие + inline меню
- `/connect <user_id>` — привязать Syndi аккаунт к Telegram
- `/profile` — мой профиль
- `/avatar` — мой AI-аватар (роль, настроение)
- `/matches` — список моих матчей
- `/help` — помощь

Любое текстовое сообщение (не команда) → передаётся в Kristina-агента,
который отвечает через `agents.kristina.KristinaUXDesigner.process_message`.

## Уведомления

Бот автоматически уведомляет о новых матчах если пользователь выполнил `/connect`.
Связка `telegram_id → user_id` хранится в памяти процесса (MVP). Для продакшена
нужно перенести маппинг в БД.

Внутри `like_routes.py` при создании матча вызывается
`telegram_bot.notifications.send_match_notification` через
`asyncio.create_task` — это не блокирует ответ `/like` и graceful
(исключения логируются).

## Архитектура

- `bot.py` — основной процесс (polling), запускается отдельно от FastAPI.
- `notifications.py` — лёгкая отправка сообщений через Telegram HTTP API,
  используется внутри FastAPI. Не тянет `python-telegram-bot`.

## Graceful degradation

Без `SYNDI_TELEGRAM_TOKEN`:
- `bot.main()` логирует предупреждение и выходит.
- `notifications.send_match_notification` возвращает `False`.
- FastAPI работает как обычно — матчи/лайки не ломаются.
