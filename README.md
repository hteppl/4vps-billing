<p align="center">
  <img src="https://4vps.su/assets/img/logo_billing.svg" alt="4VPS Billing" width="600">
</p>

## 4vps-billing

<p align="left">
  <a href="https://github.com/hteppl/4vps-billing/releases/"><img src="https://img.shields.io/github/v/release/hteppl/4vps-billing.svg" alt="Release"></a>
  <a href="https://hub.docker.com/r/hteppl/4vps-billing/"><img src="https://img.shields.io/badge/DockerHub-4vps--billing-blue" alt="DockerHub"></a>
  <a href="https://github.com/hteppl/4vps-billing/actions"><img src="https://img.shields.io/github/actions/workflow/status/hteppl/4vps-billing/dockerhub-publish.yaml" alt="Build"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python 3.12"></a>
  <a href="https://opensource.org/licenses/GPL-3.0"><img src="https://img.shields.io/badge/license-GPLv3-green.svg" alt="License: GPL v3"></a>
</p>

Сервис мониторинга баланса [4VPS](https://4vps.su) с уведомлениями в Telegram. Отправляет ежедневные отчёты о балансе с прогнозом платежей и уведомляет о пополнениях в реальном времени.

## Возможности

- **Ежедневные отчёты** - Отправка отчёта о балансе в заданное время
- **Прогноз платежей** - Расчёт предстоящих списаний на N дней вперёд
- **Предупреждения** - Уведомление о недостатке средств для оплаты серверов
- **Отслеживание пополнений** - Мгновенные уведомления о пополнении баланса
- **Мультиязычность** - Поддержка русского и английского языков
- **Поддержка топиков** - Работа с форумными чатами Telegram

## Требования

Перед началом убедитесь, что у вас есть:

- **Аккаунт 4VPS** с активными серверами
- **API ключ 4VPS** - Получите на [странице API](https://4vps.su/dashboard/api)
- **Telegram бот** - Создайте через [@BotFather](https://t.me/BotFather)
- **Chat ID** - Получите через [@username_to_id_bot](https://t.me/username_to_id_bot)

## Конфигурация

Скопируйте [`.env.example`](.env.example) в `.env` и заполните значения:

```env
# Telegram бот токен
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# ID чата для уведомлений
TELEGRAM_CHAT_ID=your_chat_id_here

# ID топика для форумных чатов (опционально)
TELEGRAM_TOPIC_ID=

# API ключ 4VPS
FOURVPS_API_KEY=your_api_key_here

# Язык сообщений (ru, en)
LOCALE=ru

# Время отправки ежедневного отчёта (24-часовой формат)
NOTIFICATION_TIME=09:00

# Количество дней для прогноза платежей
PREDICTION_DAYS=7

# Часовой пояс
TIMEZONE=Europe/Moscow

# Интервал проверки баланса для отслеживания пополнений (в секундах)
BALANCE_CHECK_INTERVAL=1800
```

### Описание параметров

| Переменная               | Описание                         | По умолчанию  | Обязательно |
|--------------------------|----------------------------------|---------------|-------------|
| `TELEGRAM_BOT_TOKEN`     | Токен Telegram бота от BotFather | -             | Да          |
| `TELEGRAM_CHAT_ID`       | ID чата для отправки уведомлений | -             | Да          |
| `TELEGRAM_TOPIC_ID`      | ID топика для форумных групп     | -             | Нет         |
| `FOURVPS_API_KEY`        | API ключ от 4VPS                 | -             | Да          |
| `LOCALE`                 | Язык сообщений (ru/en)           | ru            | Нет         |
| `NOTIFICATION_TIME`      | Время ежедневного отчёта         | 09:00         | Нет         |
| `PREDICTION_DAYS`        | Дней для прогноза платежей       | 7             | Нет         |
| `TIMEZONE`               | Часовой пояс                     | Europe/Moscow | Нет         |
| `BALANCE_CHECK_INTERVAL` | Интервал проверки пополнений     | 1800          | Нет         |

## Установка

### Docker (рекомендуется)

1. Создайте `docker-compose.yml`:

```yaml
services:
  4vps-billing:
    build: .
    container_name: 4vps-billing
    restart: unless-stopped
    env_file:
      - .env
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

2. Создайте и настройте `.env` файл:

```bash
cp .env.example .env
nano .env
```

3. Запустите контейнер:

```bash
docker compose up -d && docker compose logs -f
```

### Ручная установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/hteppl/4vps-billing.git
cd 4vps-billing
```

2. Создайте виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate     # Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте и настройте `.env` файл:

```bash
cp .env.example .env
```

5. Запустите приложение:

```bash
python -m src
```

## Как это работает

1. **Запуск** - При старте сервис отправляет начальный отчёт о балансе с прогнозом платежей

2. **Ежедневные отчёты** - В заданное время (`NOTIFICATION_TIME`) отправляется отчёт с текущим балансом и предстоящими списаниями

3. **Мониторинг пополнений** - Сервис периодически проверяет баланс и отправляет уведомление при обнаружении пополнения

4. **Предупреждения** - Если баланса не хватит для оплаты серверов, в отчёте будет предупреждение с датой

### Логи

Для диагностики проблем используйте логи:

```bash
# Docker
docker compose logs -f

# Ручная установка
# Логи выводятся в stdout с временными метками
```

## Лицензия

Проект распространяется под лицензией [GNU General Public License v3.0](LICENSE).
