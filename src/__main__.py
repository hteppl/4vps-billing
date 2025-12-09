import asyncio
import logging
import sys

from aiogram import Bot

from .config import load_config
from .fourvps import FourVPSClient
from .monitor import BalanceMonitor
from .notifier import TelegramNotifier
from .scheduler import BalanceScheduler
from .telegram import TelegramClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    config = load_config()
    if config is None:
        return

    client = FourVPSClient(config.fourvps_api_key)
    bot = Bot(token=config.telegram_bot_token)
    telegram = TelegramClient(bot, config)
    notifier = TelegramNotifier(telegram, config)
    scheduler = BalanceScheduler(config)
    monitor = BalanceMonitor(telegram, client, config)

    async def balance_job():
        await notifier.send_balance_report(client)

    scheduler.schedule_daily(balance_job)

    logger.info("4VPS Balance Notifier started")
    logger.info("Sending initial balance check...")

    if not await notifier.send_balance_report(client):
        logger.error("Initial balance check failed")

    await monitor.init_balance()
    monitor.start()
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Shutting down...")
        monitor.stop()
        scheduler.stop()
        await client.close()
        await telegram.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
