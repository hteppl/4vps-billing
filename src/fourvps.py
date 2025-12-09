import logging
from dataclasses import dataclass
from datetime import datetime

import aiohttp

logger = logging.getLogger(__name__)

BASE_URL = "https://4vps.su/api"
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=30)


@dataclass
class Server:
    id: int
    name: str
    price: float
    expired: datetime
    status: str
    ipv4: str
    tariff: str


class FourVPSClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._session: aiohttp.ClientSession | None = None

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers=self._headers,
                timeout=REQUEST_TIMEOUT,
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict | None:
        session = await self._get_session()
        url = f"{BASE_URL}/{endpoint}"

        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    logger.error("Invalid 4VPS API key")
                    return None

                data = await response.json()

                if data.get("error"):
                    logger.error(f"4VPS API error: {data.get('errorMessage', 'Unknown error')}")
                    return None

                return data

        except aiohttp.ClientError as e:
            logger.error(f"4VPS API request failed: {e}")
            return None

    async def get_balance(self) -> float | None:
        result = await self._request("GET", "userBalance")

        if result is None:
            return None

        balance = result.get("data", {}).get("userBalance")
        if balance is not None:
            return float(balance)

        logger.error("Balance not found in response")
        return None

    async def get_servers(self) -> list[Server] | None:
        result = await self._request("GET", "myservers")

        if result is None:
            return None

        servers_data = result.get("data", {}).get("serverlist", [])
        servers = []

        for s in servers_data:
            try:
                server = Server(
                    id=int(s["id"]),
                    name=s.get("name", "Unknown"),
                    price=float(s.get("price", 0)),
                    expired=datetime.fromtimestamp(int(s["expired"])),
                    status=s.get("status", "unknown"),
                    ipv4=s.get("ipv4", ""),
                    tariff=s.get("tname", ""),
                )
                servers.append(server)
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to parse server data: {e}")
                continue

        return servers
