"""Тесты эндпоинта логина пользователя."""

from __future__ import annotations

import allure

from api import AuthApiClient
from data import LOGIN_INCORRECT_MESSAGE, WRONG_USER_PASSWORD
from helpers import attach_json


@allure.parent_suite("Дипломная работа")
@allure.suite("API-тесты Stellar Burgers")
@allure.sub_suite("Пользователи")
@allure.epic("Stellar Burgers API")
@allure.feature("Логин пользователя")
class TestUserLogin:
    """Проверки для POST /auth/login."""

    @allure.title("Вход под существующим пользователем")
    @allure.story("Успешный вход пользователя")
    @allure.description("Проверяем вход под заранее созданным пользователем.")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_existing_user_success(
        self,
        auth_client: AuthApiClient,
        authorized_user,
    ) -> None:
        """Существующий пользователь должен успешно логиниться."""
        with allure.step("Подготовить payload для входа"):
            payload = authorized_user["payload"]
            register_response = authorized_user["response"]
            login_payload = {"email": payload["email"], "password": payload["password"]}
            attach_json("Payload логина", login_payload)

        with allure.step("Отправить запрос на вход"):
            login_response = auth_client.login_user(login_payload)

        with allure.step("Проверить успешный логин и структуру ответа"):
            assert register_response.status_code == 200
            assert login_response.status_code == 200
            body = login_response.json()
            attach_json("Ответ логина", body)
            assert body["success"] is True
            assert body["user"]["email"] == payload["email"]
            assert body["user"]["name"] == payload["name"]
            assert body["accessToken"].startswith("Bearer ")
            assert body["refreshToken"]

    @allure.title("Вход с неверным логином и паролем")
    @allure.story("Невалидные учётные данные")
    @allure.description("Проверяем, что API возвращает 401 при неверных кредах.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_with_wrong_credentials_fails(
        self,
        auth_client: AuthApiClient,
        user_payload_factory,
    ) -> None:
        """При неверных кредах должен вернуться 401."""
        with allure.step("Подготовить невалидные данные для входа"):
            payload = user_payload_factory()
            wrong_login_payload = {
                "email": payload["email"],  # Используем уникальный несуществующий email.
                "password": WRONG_USER_PASSWORD,
            }
            attach_json("Невалидный payload логина", wrong_login_payload)

        with allure.step("Отправить запрос с неверными данными"):
            response = auth_client.login_user(wrong_login_payload)  # Логинимся с неверными данными.

        with allure.step("Проверить код и сообщение ошибки"):
            assert response.status_code == 401
            body = response.json()
            attach_json("Ответ на невалидный логин", body)
            assert body["success"] is False
            assert body["message"] == LOGIN_INCORRECT_MESSAGE
