import asyncio
import logging
from datetime import datetime

from .config import Config
from .fourvps import FourVPSClient, Server
from .i18n import I18n, create_i18n
from .telegram import TelegramClient

logger = logging.getLogger(__name__)


class BalanceMonitor:
    def __init__(self, telegram: TelegramClient, client: FourVPSClient, config: Config):
        self.telegram = telegram
        self.client = client
        self.config = config
        self.i18n: I18n = create_i18n(config.locale)
        self._last_balance: float | None = None
        self._last_servers: dict[int, datetime] = {}
        self._running = False
        self._task: asyncio.Task | None = None

    def _format_topup(self, amount: float, new_balance: float) -> str:
        now = datetime.now(self.config.timezone)
        return "\n".join(
            [
                self.i18n.get("topup-title") + "\n",
                self.i18n.get("topup-amount", amount=f"{amount:.2f}"),
                self.i18n.get("topup-balance", balance=f"{new_balance:.2f}"),
                "\n"
                + self.i18n.get(
                    "report-time",
                    time=now.strftime("%d.%m.%Y %H:%M:%S %Z"),
                ),
            ]
        )

    def _calculate_renewed_cost(self, servers: list[Server]) -> float:
        renewed_cost = 0.0
        for server in servers:
            last_expired = self._last_servers.get(server.id)
            if last_expired is not None and server.expired > last_expired:
                renewed_cost += server.price
                logger.debug(f"Server {server.name} renewed: +{server.price:.2f} ₽")
        return renewed_cost

    def _update_servers(self, servers: list[Server]):
        self._last_servers = {s.id: s.expired for s in servers}

    async def _check_balance(self):
        balance = await self.client.get_balance()
        servers = await self.client.get_servers()

        if balance is None:
            return

        if self._last_balance is not None:
            balance_diff = balance - self._last_balance
            renewed_cost = 0.0

            if servers:
                renewed_cost = self._calculate_renewed_cost(servers)

            topup_amount = balance_diff + renewed_cost

            if topup_amount > 0:
                logger.info(f"Top-up detected: +{topup_amount:.2f} ₽")
                message = self._format_topup(topup_amount, balance)
                await self.telegram.send_message(message)

        self._last_balance = balance
        if servers:
            self._update_servers(servers)

    async def _run(self):
        while self._running:
            try:
                await self._check_balance()
            except Exception as e:
                logger.error(f"Balance monitor error: {e}")

            await asyncio.sleep(self.config.balance_check_interval)

    def start(self):
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"Balance monitor started (interval: {self.config.balance_check_interval}s)")

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Balance monitor stopped")

    async def init_balance(self):
        self._last_balance = await self.client.get_balance()
        servers = await self.client.get_servers()

        if servers:
            self._update_servers(servers)

        if self._last_balance is not None:
            logger.info(f"Initial balance: {self._last_balance:.2f} ₽")
