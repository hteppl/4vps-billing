import asyncio
import logging
from datetime import datetime, timedelta

from .config import Config
from .fourvps import FourVPSClient, Server
from .i18n import I18n, create_i18n
from .telegram import TelegramClient

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, telegram: TelegramClient, config: Config):
        self.telegram = telegram
        self.config = config
        self.i18n: I18n = create_i18n(config.locale)

    def _get_daily_payments(self, servers: list[Server]) -> dict[str, float]:
        now = datetime.now(self.config.timezone)
        cutoff = now + timedelta(days=self.config.prediction_days)

        daily: dict[datetime, float] = {}
        for server in servers:
            expired_aware = server.expired.replace(tzinfo=self.config.timezone)
            if expired_aware <= cutoff:
                day = expired_aware.replace(hour=0, minute=0, second=0, microsecond=0)
                daily[day] = daily.get(day, 0) + server.price

        return {day.strftime("%d.%m.%Y"): amount for day, amount in sorted(daily.items())}

    def _format_prediction(self, balance: float, servers: list[Server]) -> str:
        daily_payments = self._get_daily_payments(servers)
        total_payments = sum(daily_payments.values())

        lines = [
            self.i18n.get("balance-report-title") + "\n",
            self.i18n.get("balance-current", balance=f"{balance:.2f}"),
        ]

        if daily_payments:
            lines.append("\n" + self.i18n.get("predictions-title", days=self.config.prediction_days) + "\n")

            running_balance = balance
            negative_day = None
            for day, amount in daily_payments.items():
                running_balance -= amount
                lines.append(
                    self.i18n.get(
                        "predictions-day",
                        date=day,
                        amount=f"{amount:.2f}",
                        remaining=f"{running_balance:.2f}",
                    )
                )
                if running_balance < 0 and negative_day is None:
                    negative_day = day

            lines.append("\n" + self.i18n.get("predictions-total", total=f"{total_payments:.2f}"))

            if negative_day:
                lines.append("\n" + self.i18n.get("warning-insufficient", date=negative_day))
        else:
            lines.append("\n" + self.i18n.get("predictions-none", days=self.config.prediction_days))

        now = datetime.now(self.config.timezone)
        lines.append(
            "\n"
            + self.i18n.get(
                "report-time",
                time=now.strftime("%d.%m.%Y %H:%M:%S %Z"),
            )
        )

        return "\n".join(lines)

    async def send_balance_report(self, client: FourVPSClient) -> bool:
        logger.info("Checking balance...")

        balance, servers = await asyncio.gather(
            client.get_balance(),
            client.get_servers(),
        )

        if balance is None:
            message = "\n\n".join(
                [
                    self.i18n.get("error-balance-failed"),
                    self.i18n.get("error-balance-failed-desc"),
                ]
            )
            return await self.telegram.send_message(message)

        if servers is None:
            now = datetime.now(self.config.timezone)
            message = "\n".join(
                [
                    self.i18n.get("balance-report-title") + "\n",
                    self.i18n.get("balance-current", balance=f"{balance:.2f}"),
                    self.i18n.get("error-servers-failed"),
                    "\n"
                    + self.i18n.get(
                        "report-time",
                        time=now.strftime("%d.%m.%Y %H:%M:%S %Z"),
                    ),
                ]
            )
            return await self.telegram.send_message(message)

        message = self._format_prediction(balance, servers)
        return await self.telegram.send_message(message)
