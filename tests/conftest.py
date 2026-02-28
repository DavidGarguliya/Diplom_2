"""Общие фикстуры для API-тестов Stellar Burgers."""

from __future__ import annotations

import uuid

import allure
import pytest

from api import StellarBurgersApi
from helpers import attach_json, attach_text

BASE_URL = "https://stellarburgers.education-services.ru/api"  # Базовый URL тестового API.


@pytest.fixture(scope="session")
def api_client() -> StellarBurgersApi:
    """Инициализирует API-клиент для всех тестов."""
    with allure.step("Инициализация API-клиента"):
        attach_text("Базовый URL API", BASE_URL)
        return StellarBurgersApi(base_url=BASE_URL)


@pytest.fixture
def user_payload_factory():
    """Создаёт уникальные данные пользователя для каждого вызова."""

    def _build_payload() -> dict:
        with allure.step("Генерация уникальных данных пользователя"):
            unique_suffix = uuid.uuid4().hex
            payload = {
                "email": f"qa_{unique_suffix}@mail.com",
                "password": "Pass1234",  # Валидный пароль для регистрации и логина.
                "name": f"QA_{unique_suffix[:8]}",
            }
            attach_json("Сгенерированный payload пользователя", payload)
            return payload

    return _build_payload


@pytest.fixture
def created_users(api_client: StellarBurgersApi):
    """Собирает токены созданных пользователей и удаляет их после теста."""
    access_tokens: list[str] = []

    def _remember(access_token: str | None) -> None:
        with allure.step("Регистрация токена пользователя на удаление"):
            if access_token:
                access_tokens.append(access_token)
                attach_text("Токен сохранён", f"Количество токенов в очереди удаления: {len(access_tokens)}")

    yield _remember

    with allure.step("Teardown: удаление пользователей, созданных в тесте"):
        for index, token in enumerate(access_tokens, start=1):
            with allure.step(f"Удаление пользователя №{index}"):
                response = api_client.delete_user(token)
                attach_text("Результат удаления пользователя", f"HTTP {response.status_code}")


@pytest.fixture(scope="session")
def ingredient_ids(api_client: StellarBurgersApi) -> list[str]:
    """Возвращает валидные id ингредиентов для тестов заказов."""
    with allure.step("Получение валидных ингредиентов для тестов"):
        response = api_client.get_ingredients()
        assert response.status_code == 200, "Не удалось получить список ингредиентов"

        body = response.json()
        assert body.get("success") is True, "Ответ /ingredients вернул success=false"
        data = body.get("data", [])
        assert len(data) >= 2, "Для тестов нужно минимум два ингредиента"
        selected_ids = [data[0]["_id"], data[1]["_id"]]
        attach_json("ID ингредиентов для тестов", selected_ids)
        return selected_ids
