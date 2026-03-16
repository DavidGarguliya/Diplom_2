"""Тесты эндпоинта создания пользователя."""

from __future__ import annotations

import allure

from api import AuthApiClient
from data import USER_ALREADY_EXISTS_MESSAGE, USER_REQUIRED_FIELDS_MESSAGE
from helpers import attach_json


@allure.parent_suite("Дипломная работа")
@allure.suite("API-тесты Stellar Burgers")
@allure.sub_suite("Пользователи")
@allure.epic("Stellar Burgers API")
@allure.feature("Создание пользователя")
class TestUserCreation:
    """Проверки для POST /auth/register."""

    @allure.title("Создание уникального пользователя")
    @allure.story("Успешная регистрация нового пользователя")
    @allure.description("Проверяем, что уникальный пользователь создаётся и возвращаются токены.")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_unique_user_success(
        self,
        auth_client: AuthApiClient,
        user_payload_factory,
        created_users,
    ) -> None:
        """Должен успешно создаваться новый уникальный пользователь."""
        with allure.step("Подготовить данные нового пользователя"):
            payload = user_payload_factory()
            attach_json("Payload регистрации", payload)

        with allure.step("Отправить запрос на регистрацию"):
            response = auth_client.register_user(payload)  # Выполняем запрос на регистрацию.

        with allure.step("Проверить статус-код и тело ответа"):
            assert response.status_code == 200
            body = response.json()
            attach_json("Тело ответа регистрации", body)
            assert body["success"] is True
            assert body["user"]["email"] == payload["email"]
            assert body["user"]["name"] == payload["name"]
            assert body["accessToken"].startswith("Bearer ")
            assert body["refreshToken"]

        with allure.step("Сохранить пользователя для последующего удаления"):
            created_users(body["accessToken"])

    @allure.title("Создание уже зарегистрированного пользователя")
    @allure.story("Повторная регистрация существующего пользователя")
    @allure.description("Проверяем, что API блокирует регистрацию уже существующего email.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_duplicate_user_fails(
        self,
        auth_client: AuthApiClient,
        user_payload_factory,
        created_users,
    ) -> None:
        """Должна возвращаться ошибка при повторной регистрации."""
        with allure.step("Подготовить данные пользователя для двойной регистрации"):
            payload = user_payload_factory()
            attach_json("Payload для первой и второй регистрации", payload)

        with allure.step("Выполнить первую успешную регистрацию"):
            first_response = auth_client.register_user(payload)
            first_body = first_response.json()
            attach_json("Ответ первой регистрации", first_body)
            created_users(first_body.get("accessToken"))

        with allure.step("Выполнить повторную регистрацию с теми же данными"):
            duplicate_response = auth_client.register_user(payload)

        with allure.step("Проверить корректную ошибку повторной регистрации"):
            assert first_response.status_code == 200
            assert duplicate_response.status_code == 403
            duplicate_body = duplicate_response.json()
            attach_json("Ответ повторной регистрации", duplicate_body)
            assert duplicate_body["success"] is False
            assert duplicate_body["message"] == USER_ALREADY_EXISTS_MESSAGE

    @allure.title("Создание пользователя без обязательного поля")
    @allure.story("Регистрация без обязательного поля")
    @allure.description("Проверяем, что без поля name API возвращает ошибку валидации.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user_without_required_field_fails(
        self,
        auth_client: AuthApiClient,
        user_payload_factory,
    ) -> None:
        """Должна возвращаться ошибка, если не передано обязательное поле."""
        with allure.step("Подготовить payload без обязательного поля name"):
            payload = user_payload_factory()
            payload.pop("name")  # Удаляем обязательное поле для негативной проверки.
            attach_json("Payload без поля name", payload)

        with allure.step("Отправить запрос на регистрацию с невалидным payload"):
            response = auth_client.register_user(payload)

        with allure.step("Проверить код и сообщение об ошибке"):
            assert response.status_code == 403
            body = response.json()
            attach_json("Ответ с ошибкой валидации", body)
            assert body["success"] is False
            assert body["message"] == USER_REQUIRED_FIELDS_MESSAGE
