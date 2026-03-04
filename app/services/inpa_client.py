import asyncio
import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class InpaClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._base_url = self._settings.inpa_base_url.rstrip("/")
        self._path = self._settings.inpa_search_path

    async def fetch_page(self, page: int, size: int, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}{self._path}"
        params = {"page": page, "size": size}
        body = payload or {}
        timeout = httpx.Timeout(self._settings.inpa_timeout_seconds)

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.inpa.gov.it",
            "User-Agent": self._settings.user_agent,
        }

        max_attempts = 4
        for attempt in range(1, max_attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(url, params=params, json=body, headers=headers)
                    response.raise_for_status()
                    logger.info(
                        "inpa page fetched page=%s size=%s status=%s attempt=%s",
                        page,
                        size,
                        response.status_code,
                        attempt,
                    )
                    return response.json()
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                retryable = status >= 500 or status == 429
                if not retryable or attempt == max_attempts:
                    raise
                await asyncio.sleep(0.5 * (2 ** (attempt - 1)))
            except (httpx.TimeoutException, httpx.TransportError):
                if attempt == max_attempts:
                    raise
                await asyncio.sleep(0.5 * (2 ** (attempt - 1)))

        return {"content": []}
