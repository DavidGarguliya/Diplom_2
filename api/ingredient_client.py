"""Клиент для работы с ингредиентами."""

from __future__ import annotations

import allure
import requests

from .client import BaseApiClient


class IngredientApiClient(BaseApiClient):
    """Клиент эндпоинтов ингредиентов."""

    @allure.step("API: получение списка ингредиентов")
    def get_ingredients(self) -> requests.Response:
        """Получает список доступных ингредиентов."""
        return self._request(method="GET", path="/ingredients")
