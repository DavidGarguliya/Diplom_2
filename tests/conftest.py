"""Общие фикстуры для API-тестов Stellar Burgers."""

from __future__ import annotations

import logging
import uuid

import allure
import pytest

from api import AuthApiClient, IngredientApiClient, OrderApiClient, UserApiClient
from data import DEFAULT_USER_PASSWORD
from helpers import attach_json, attach_text
from settings import BASE_URL_ENV_VAR, resolve_base_url

logger = logging.getLogger(__name__)


def pytest_addoption(parser) -> None:
    """Добавляет аргумент запуска для переопределения базового URL API."""
    parser.addoption(
        "--base-url",
        action="store",
        default=None,
        help=f"Базовый URL API Stellar Burgers. Можно также задать через {BASE_URL_ENV_VAR}.",
    )


@pytest.fixture(scope="session")
def base_url(pytestconfig) -> str:
    """Возвращает базовый URL API из аргумента запуска, окружения или дефолта."""
    with allure.step("Определение базового URL API"):
        resolved_base_url = resolve_base_url(pytestconfig.getoption("--base-url"))
        attach_text("Базовый URL API", resolved_base_url)
        return resolved_base_url


@pytest.fixture(scope="session")
def auth_client(base_url: str) -> AuthApiClient:
    """Инициализирует клиент авторизации для всех тестов."""
    with allure.step("Инициализация клиента авторизации"):
        return AuthApiClient(base_url=base_url)


@pytest.fixture(scope="session")
def user_client(base_url: str) -> UserApiClient:
    """Инициализирует клиент пользователя для всех тестов."""
    with allure.step("Инициализация клиента пользователя"):
        return UserApiClient(base_url=base_url)


@pytest.fixture(scope="session")
def ingredient_client(base_url: str) -> IngredientApiClient:
    """Инициализирует клиент ингредиентов для всех тестов."""
    with allure.step("Инициализация клиента ингредиентов"):
        return IngredientApiClient(base_url=base_url)


@pytest.fixture(scope="session")
def order_client(base_url: str) -> OrderApiClient:
    """Инициализирует клиент заказов для всех тестов."""
    with allure.step("Инициализация клиента заказов"):
        return OrderApiClient(base_url=base_url)


@pytest.fixture
def user_payload_factory():
    """Создаёт уникальные данные пользователя для каждого вызова."""

    def _build_payload() -> dict:
        with allure.step("Генерация уникальных данных пользователя"):
            unique_suffix = uuid.uuid4().hex
            payload = {
                "email": f"qa_{unique_suffix}@mail.com",
                "password": DEFAULT_USER_PASSWORD,  # Валидный пароль для регистрации и логина.
                "name": f"QA_{unique_suffix[:8]}",
            }
            attach_json("Сгенерированный payload пользователя", payload)
            return payload

    return _build_payload


@pytest.fixture
def created_users(user_client: UserApiClient):
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
                try:
                    response = user_client.delete_user(token)
                    attach_text("Результат удаления пользователя", f"HTTP {response.status_code}")
                    if response.status_code not in (200, 202):
                        logger.warning(
                            "Неожиданный код ответа при удалении пользователя в teardown: %s",
                            response.status_code,
                        )
                except Exception as error:
                    logger.exception("Ошибка при удалении пользователя в teardown: %s", error)


@pytest.fixture
def authorized_user(
    auth_client: AuthApiClient,
    user_payload_factory,
    created_users,
) -> dict:
    """Создаёт зарегистрированного пользователя с токеном как предусловие теста."""
    with allure.step("Подготовить зарегистрированного пользователя с токеном"):
        payload = user_payload_factory()
        attach_json("Payload регистрации пользователя", payload)
        register_response = auth_client.register_user(payload)
        register_body = register_response.json()
        attach_json("Ответ регистрации пользователя", register_body)
        access_token = register_body.get("accessToken")
        created_users(access_token)
        return {
            "payload": payload,
            "response": register_response,
            "body": register_body,
            "access_token": access_token,
        }


@pytest.fixture(scope="session")
def ingredient_ids(ingredient_client: IngredientApiClient) -> list[str]:
    """Возвращает валидные id ингредиентов для тестов заказов."""
    with allure.step("Получение валидных ингредиентов для тестов"):
        response = ingredient_client.get_ingredients()
        if response.status_code != 200:
            pytest.fail("Не удалось получить список ингредиентов")

        body = response.json()
        if body.get("success") is not True:
            pytest.fail("Ответ /ingredients вернул success=false")

        data = body.get("data", [])
        if len(data) < 2:
            pytest.fail("Для тестов нужно минимум два ингредиента")

        selected_ids = [data[0]["_id"], data[1]["_id"]]
        attach_json("ID ингредиентов для тестов", selected_ids)
        return selected_ids
