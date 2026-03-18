# Подключение DeepSeek API к Syndi

Это руководство поможет настроить интеграцию с DeepSeek API для получения умных ответов от AI-агентов.

## 📋 Содержание

1. [Получение API ключа](#получение-api-ключа)
2. [Настройка проекта](#настройка-проекта)
3. [Проверка работы](#проверка-работы)
4. [Решение проблем](#решение-проблем)

---

## Получение API ключа

### Шаг 1: Регистрация на DeepSeek Platform

1. Перейдите на [platform.deepseek.com](https://platform.deepseek.com/)
2. Нажмите "Sign Up" и создайте аккаунт
3. Подтвердите email

### Шаг 2: Получение API ключа

1. Войдите в личный кабинет
2. Перейдите в раздел **API Keys**
3. Нажмите **"Create API Key"**
4. Скопируйте ключ (начинается с `sk-`)

⚠️ **Важно:** Ключ показывается только один раз! Сохраните его в надёжном месте.

### Шаг 3: Пополнение баланса (опционально)

DeepSeek предоставляет **бесплатные токены** для тестирования:
- 10M токенов для новых пользователей
- Достаточно для разработки и тестирования

Для production использования пополните баланс:
- Цены: ~$0.001-0.002 за 1K токенов
- Оплата картой или криптовалютой

---

## Настройка проекта

### Шаг 1: Создание .env файла

```bash
cd /mnt/okcomputer/output/syndi
cp .env.example .env
```

### Шаг 2: Редактирование .env

Откройте `.env` и добавьте API ключ:

```env
# AI Services
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

Убедитесь, что установлен `aiohttp`:
```bash
pip install aiohttp==3.9.1
```

### Шаг 4: Запуск сервера

```bash
uvicorn api.main:app --reload
```

---

## Проверка работы

### Проверка статуса LLM сервиса

```bash
curl http://localhost:8000/agents
```

Ответ должен показать доступность LLM:
```json
[
  {
    "id": "kristina_ux_001",
    "name": "Кристина",
    "role": "ux_designer",
    ...
  }
]
```

### Тестирование Кристины с DeepSeek

```bash
curl -X POST "http://localhost:8000/agents/kristina_ux_001/chat?user_id=test123" \
  -H "Content-Type: application/json" \
  -d '{"message": "Как провести исследование пользователей?"}'
```

При успешной настройке ответ будет сгенерирован DeepSeek API и будет более естественным и контекстуальным.

---

## Как это работает

### Архитектура интеграции

```
Пользователь → API Endpoint → KristinaAgent → LLMService → DeepSeek API
                                              ↓
                                       Fallback (шаблоны)
```

### Логика работы

1. **Проверка доступности**: При запуске проверяется наличие `DEEPSEEK_API_KEY`
2. **Генерация ответа**: Кристина отправляет запрос к DeepSeek API
3. **Fallback**: Если API недоступен, используются шаблонные ответы
4. **Память**: Контекст разговора сохраняется для персонализации

### Параметры запроса

```python
{
    "model": "deepseek-chat",      # Модель DeepSeek
    "temperature": 0.7,             # Креативность (0-2)
    "max_tokens": 1500,             # Максимальная длина ответа
    "messages": [                   # История разговора
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ]
}
```

---

## Решение проблем

### Проблема: "DeepSeek API key не найден"

**Причина:** Отсутствует `DEEPSEEK_API_KEY` в переменных окружения

**Решение:**
```bash
# Проверьте, что ключ установлен
echo $DEEPSEEK_API_KEY

# Если пусто, установите
export DEEPSEEK_API_KEY=sk-your-key-here

# Или используйте .env файл
python -c "from dotenv import load_dotenv; load_dotenv()"
```

### Проблема: "Ошибка подключения к DeepSeek API"

**Причина:** Проблемы с сетью или API недоступен

**Решение:**
1. Проверьте интернет-соединение
2. Проверьте статус DeepSeek: [status.deepseek.com](https://status.deepseek.com)
3. Убедитесь, что ключ активен

### Проблема: "Rate limit exceeded"

**Причина:** Превышен лимит запросов

**Решение:**
- Подождите 1 минуту
- Проверьте лимиты в личном кабинете
- Рассмотрите upgrade тарифа

### Проблема: Медленные ответы

**Причина:** Высокая нагрузка на API

**Решение:**
- Используйте `max_tokens` для ограничения длины
- Включите кэширование ответов
- Используйте fallback для простых запросов

---

## Дополнительные возможности

### Потоковая генерация (Streaming)

Для получения ответа частями (как в ChatGPT):

```python
from services.llm import get_llm_service

llm = get_llm_service()

async for chunk in llm.generate_stream(
    system_prompt="...",
    user_message="..."
):
    print(chunk, end="")
```

### Настройка температуры

- **0.0-0.3**: Консервативные, предсказуемые ответы
- **0.4-0.7**: Сбалансированные (рекомендуется)
- **0.8-1.0**: Креативные, разнообразные ответы
- **1.1-2.0**: Очень креативные, возможны галлюцинации

### Использование разных моделей

DeepSeek предлагает несколько моделей:

| Модель | Описание | Использование |
|--------|----------|---------------|
| `deepseek-chat` | Основная модель | Общие задачи |
| `deepseek-coder` | Для кода | Программирование |
| `deepseek-reasoner` | Для рассуждений | Сложные задачи |

---

## Безопасность

### Хранение API ключа

✅ **Правильно:**
- Храните в `.env` файле
- Не коммитьте `.env` в git
- Используйте переменные окружения в production

❌ **Неправильно:**
- Хардкодить ключ в коде
- Публиковать ключ в открытых репозиториях
- Отправлять ключ в чатах

### .gitignore

Убедитесь, что `.env` в `.gitignore`:

```gitignore
# Environment
.env
.env.local
.env.production
```

---

## Стоимость

### Бесплатный уровень

- 10M токенов для новых пользователей
- Достаточно для разработки

### Платный уровень

| Модель | Input | Output |
|--------|-------|--------|
| deepseek-chat | $0.001/1K | $0.002/1K |
| deepseek-coder | $0.001/1K | $0.002/1K |

### Оптимизация расходов

1. **Используйте fallback** для простых вопросов
2. **Ограничивайте max_tokens**
3. **Кэшируйте частые запросы**
4. **Используйте короткий контекст**

---

## Примеры использования

### Пример 1: UX-консультация

```python
import asyncio
from agents import get_kristina

async def main():
    kristina = get_kristina()
    
    response = await kristina.process_message(
        user_id="user123",
        message="Как улучшить onboarding в приложении?"
    )
    
    print(response.content)

asyncio.run(main())
```

### Пример 2: С потоковой генерацией

```python
from services.llm import get_llm_service

async def stream_response():
    llm = get_llm_service()
    
    async for chunk in llm.generate_stream(
        system_prompt="Ты UX-дизайнер...",
        user_message="Расскажи про CJM"
    ):
        print(chunk, end="", flush=True)

asyncio.run(stream_response())
```

---

## Полезные ссылки

- [DeepSeek Platform](https://platform.deepseek.com/)
- [DeepSeek API Docs](https://platform.deepseek.com/docs)
- [Pricing](https://platform.deepseek.com/pricing)
- [Status Page](https://status.deepseek.com/)

---

## Поддержка

Если у вас возникли проблемы:

1. Проверьте логи сервера
2. Убедитесь, что API ключ активен
3. Проверьте баланс на счету
4. Обратитесь в поддержку DeepSeek

---

**Готово!** Теперь Кристина использует DeepSeek API для генерации умных ответов. 🚀
