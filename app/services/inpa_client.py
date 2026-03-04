from typing import Any

import httpx

from app.core.config import get_settings


class InpaClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._base_url = self._settings.inpa_base_url.rstrip("/")
        self._path = self._settings.inpa_search_path

    async def fetch_page(self, page: int, size: int, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}{self._path}"
        params = {"page": page, "size": size}
        body = payload or {}

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.inpa.gov.it",
            "User-Agent": self._settings.user_agent,
        }

        timeout = httpx.Timeout(self._settings.inpa_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, params=params, json=body, headers=headers)
            response.raise_for_status()
            return response.json()
