import logging

from aiogram import Bot

from .config import Config

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self, bot: Bot, config: Config):
        self.bot = bot
        self.config = config

    async def send_message(self, text: str) -> bool:
        try:
            await self.bot.send_message(
                chat_id=self.config.telegram_chat_id,
                text=text,
                parse_mode="HTML",
                message_thread_id=self.config.telegram_topic_id,
            )
            logger.info("Telegram message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    async def close(self):
        await self.bot.session.close()
