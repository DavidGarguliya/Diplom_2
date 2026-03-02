"""Базовый HTTP-клиент для API Stellar Burgers."""

from __future__ import annotations

from typing import Any

import allure
import requests

from helpers.allure import attach_request_details, attach_response_details


class BaseApiClient:
    """Базовый клиент с общей логикой HTTP-запросов."""

    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @allure.step("HTTP-запрос к API: {method} {path}")
    def _request(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> requests.Response:
        """Выполняет HTTP-запрос и прикладывает детали в Allure."""
        url = f"{self.base_url}{path}"
        request_headers = headers or {}
        attach_request_details(
            method=method,
            url=url,
            headers=request_headers,
            params=params,
            payload=payload,
        )

        response = requests.request(
            method=method,
            url=url,
            json=payload,
            headers=request_headers,
            params=params,
            timeout=self.timeout,
        )
        attach_response_details(response)
        return response
