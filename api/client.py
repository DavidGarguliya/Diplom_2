"""Клиент для API Stellar Burgers."""

from __future__ import annotations

from typing import Any

import allure
import requests

from helpers.allure import attach_request_details, attach_response_details


class StellarBurgersApi:
    """Обёртка над HTTP-запросами к Stellar Burgers API."""

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

    @allure.step("API: регистрация пользователя")
    def register_user(self, payload: dict) -> requests.Response:
        """Отправляет запрос на регистрацию пользователя."""
        return self._request(method="POST", path="/auth/register", payload=payload)

    @allure.step("API: логин пользователя")
    def login_user(self, payload: dict) -> requests.Response:
        """Отправляет запрос на логин пользователя."""
        return self._request(method="POST", path="/auth/login", payload=payload)

    @allure.step("API: удаление пользователя")
    def delete_user(self, access_token: str) -> requests.Response:
        """Удаляет пользователя по токену авторизации."""
        return self._request(
            method="DELETE",
            path="/auth/user",
            headers={"Authorization": access_token},
        )

    @allure.step("API: получение списка ингредиентов")
    def get_ingredients(self) -> requests.Response:
        """Получает список доступных ингредиентов."""
        return self._request(method="GET", path="/ingredients")

    @allure.step("API: создание заказа")
    def create_order(
        self,
        ingredients: list[str] | None = None,
        access_token: str | None = None,
    ) -> requests.Response:
        """Создаёт заказ с ингредиентами (или без них)."""
        payload = {}
        if ingredients is not None:
            payload["ingredients"] = ingredients

        headers = {}
        if access_token:
            headers["Authorization"] = access_token

        return self._request(
            method="POST",
            path="/orders",
            payload=payload,
            headers=headers,
        )

    @allure.step("API: получение заказов пользователя")
    def get_user_orders(self, access_token: str) -> requests.Response:
        """Получает историю заказов текущего пользователя."""
        return self._request(
            method="GET",
            path="/orders",
            headers={"Authorization": access_token},
        )
