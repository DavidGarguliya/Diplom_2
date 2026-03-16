"""Клиент для работы с заказами."""

from __future__ import annotations

import allure
import requests

from .client import BaseApiClient


class OrderApiClient(BaseApiClient):
    """Клиент эндпоинтов заказов."""

    @allure.step("API: создание заказа")
    def create_order(
        self,
        ingredients: list[str] | None = None,
        access_token: str | None = None,
    ) -> requests.Response:
        """Создаёт заказ с ингредиентами или без них."""
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
