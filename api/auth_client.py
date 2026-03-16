"""Клиент для работы с авторизацией и регистрацией."""

from __future__ import annotations

import allure
import requests

from .client import BaseApiClient


class AuthApiClient(BaseApiClient):
    """Клиент эндпоинтов авторизации пользователя."""

    @allure.step("API: регистрация пользователя")
    def register_user(self, payload: dict) -> requests.Response:
        """Отправляет запрос на регистрацию пользователя."""
        return self._request(method="POST", path="/auth/register", payload=payload)

    @allure.step("API: логин пользователя")
    def login_user(self, payload: dict) -> requests.Response:
        """Отправляет запрос на логин пользователя."""
        return self._request(method="POST", path="/auth/login", payload=payload)
