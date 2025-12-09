import logging
import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class Config:
    fourvps_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    telegram_topic_id: int | None
    notification_time: str
    timezone: ZoneInfo
    prediction_days: int
    locale: str
    balance_check_interval: int

    @property
    def notification_hour(self) -> int:
        return int(self.notification_time.split(":")[0])

    @property
    def notification_minute(self) -> int:
        return int(self.notification_time.split(":")[1])


def load_config() -> Config | None:
    missing = []

    fourvps_api_key = os.getenv("FOURVPS_API_KEY")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    telegram_topic_id = os.getenv("TELEGRAM_TOPIC_ID")
    notification_time = os.getenv("NOTIFICATION_TIME", "09:00")
    timezone_str = os.getenv("TIMEZONE", "Europe/Moscow")
    prediction_days = int(os.getenv("PREDICTION_DAYS", "7"))
    locale = os.getenv("LOCALE", "ru")
    balance_check_interval = int(os.getenv("BALANCE_CHECK_INTERVAL", "1800"))

    if not fourvps_api_key:
        missing.append("FOURVPS_API_KEY")
    if not telegram_bot_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not telegram_chat_id:
        missing.append("TELEGRAM_CHAT_ID")

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please copy .env.example to .env and fill in the values")
        return None

    try:
        timezone = ZoneInfo(timezone_str)
    except Exception:
        logger.error(f"Invalid timezone: {timezone_str}")
        return None

    return Config(
        fourvps_api_key=fourvps_api_key,
        telegram_bot_token=telegram_bot_token,
        telegram_chat_id=telegram_chat_id,
        telegram_topic_id=int(telegram_topic_id) if telegram_topic_id else None,
        notification_time=notification_time,
        timezone=timezone,
        prediction_days=prediction_days,
        locale=locale,
        balance_check_interval=balance_check_interval,
    )
