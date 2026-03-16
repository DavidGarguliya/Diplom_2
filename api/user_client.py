"""Клиент для работы с пользователем."""

from __future__ import annotations

import allure
import requests

from .client import BaseApiClient


class UserApiClient(BaseApiClient):
    """Клиент пользовательских эндпоинтов."""

    @allure.step("API: удаление пользователя")
    def delete_user(self, access_token: str) -> requests.Response:
        """Удаляет пользователя по токену авторизации."""
        return self._request(
            method="DELETE",
            path="/auth/user",
            headers={"Authorization": access_token},
        )
