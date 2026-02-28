"""Тесты эндпоинта создания заказа."""

from __future__ import annotations

import allure

from api import StellarBurgersApi
from helpers import attach_json, attach_text


@allure.parent_suite("Дипломная работа")
@allure.suite("API-тесты Stellar Burgers")
@allure.sub_suite("Заказы")
@allure.epic("Stellar Burgers API")
@allure.feature("Создание заказа")
class TestOrderCreation:
    """Проверки для POST /orders."""

    @allure.title("Создание заказа с авторизацией")
    @allure.story("Авторизованный пользователь создаёт заказ")
    @allure.description("Проверяем создание заказа с токеном и наличие заказа в персональной ленте.")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_order_with_authorization_success(
        self,
        api_client: StellarBurgersApi,
        user_payload_factory,
        created_users,
        ingredient_ids,
    ) -> None:
        """Авторизованный пользователь должен успешно создать заказ."""
        with allure.step("Подготовить пользователя и получить токен"):
            payload = user_payload_factory()
            attach_json("Payload регистрации пользователя", payload)
            register_response = api_client.register_user(payload)  # Создаём пользователя для авторизованного заказа.
            register_body = register_response.json()
            attach_json("Ответ регистрации пользователя", register_body)
            access_token = register_body.get("accessToken")
            created_users(access_token)

        with allure.step("Подготовить ингредиенты заказа"):
            attach_json("Ингредиенты для авторизованного заказа", ingredient_ids)

        with allure.step("Создать заказ от авторизованного пользователя"):
            response = api_client.create_order(ingredients=ingredient_ids, access_token=access_token)

        with allure.step("Проверить ответ на создание заказа"):
            assert register_response.status_code == 200
            assert response.status_code == 200
            body = response.json()
            attach_json("Ответ создания авторизованного заказа", body)
            assert body["success"] is True
            assert body["order"]["number"] > 0
            assert len(body["order"]["ingredients"]) >= 2

        with allure.step("Проверить наличие заказа в персональной ленте"):
            user_orders_response = api_client.get_user_orders(access_token)
            assert user_orders_response.status_code == 200
            user_orders_body = user_orders_response.json()
            attach_json("Персональная лента заказов пользователя", user_orders_body)
            assert user_orders_body["success"] is True
            order_number = body["order"]["number"]
            assert any(order["number"] == order_number for order in user_orders_body["orders"])

    @allure.title("Создание заказа без авторизации")
    @allure.story("Неавторизованный пользователь создаёт заказ")
    @allure.description("Проверяем создание заказа без токена авторизации.")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_order_without_authorization_success(
        self,
        api_client: StellarBurgersApi,
        ingredient_ids,
    ) -> None:
        """Неавторизованный пользователь тоже может создать заказ."""
        with allure.step("Подготовить ингредиенты заказа без авторизации"):
            attach_json("Ингредиенты заказа без токена", ingredient_ids)

        with allure.step("Отправить запрос на создание заказа без токена"):
            response = api_client.create_order(ingredients=ingredient_ids)  # Отправляем заказ без токена.

        with allure.step("Проверить успешное создание заказа"):
            assert response.status_code == 200
            body = response.json()
            attach_json("Ответ создания заказа без авторизации", body)
            assert body["success"] is True
            assert body["order"]["number"] > 0

    @allure.title("Создание заказа с ингредиентами")
    @allure.story("Создание заказа с валидными ингредиентами")
    @allure.description("Проверяем успешное создание заказа при передаче валидного ингредиента.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_order_with_ingredients_success(
        self,
        api_client: StellarBurgersApi,
        ingredient_ids,
    ) -> None:
        """При передаче валидных ингредиентов заказ должен создаться."""
        with allure.step("Подготовить один валидный ингредиент"):
            order_ingredients = [ingredient_ids[0]]
            attach_json("Ингредиенты заказа", order_ingredients)

        with allure.step("Отправить запрос на создание заказа"):
            response = api_client.create_order(ingredients=order_ingredients)

        with allure.step("Проверить успешный ответ"):
            assert response.status_code == 200
            body = response.json()
            attach_json("Ответ создания заказа с ингредиентами", body)
            assert body["success"] is True
            assert body["name"]
            assert body["order"]["number"] > 0

    @allure.title("Создание заказа без ингредиентов")
    @allure.story("Создание заказа с пустым списком ингредиентов")
    @allure.description("Проверяем валидацию API: заказ без ингредиентов должен быть отклонён.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_order_without_ingredients_fails(
        self,
        api_client: StellarBurgersApi,
    ) -> None:
        """При пустом списке ингредиентов должна вернуться ошибка."""
        with allure.step("Отправить запрос на создание заказа без ингредиентов"):
            response = api_client.create_order(ingredients=[])

        with allure.step("Проверить код и сообщение ошибки"):
            assert response.status_code == 400
            body = response.json()
            attach_json("Ответ API при пустых ингредиентах", body)
            assert body["success"] is False
            assert body["message"] == "Ingredient ids must be provided"

    @allure.title("Создание заказа с неверным хешем ингредиентов")
    @allure.story("Создание заказа с невалидным хешем ингредиента")
    @allure.description("Проверяем реакцию API на невалидный хеш ингредиента.")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_order_with_invalid_ingredient_hash_fails(
        self,
        api_client: StellarBurgersApi,
    ) -> None:
        """При невалидном хеше ингредиента API возвращает 500."""
        with allure.step("Подготовить невалидный хеш ингредиента"):
            invalid_ingredients = ["invalidhash"]
            attach_json("Невалидные ингредиенты", invalid_ingredients)

        with allure.step("Отправить запрос с невалидным хешем"):
            response = api_client.create_order(
                ingredients=invalid_ingredients
            )  # Невалидный формат id ингредиента.

        with allure.step("Проверить ответ API при невалидном хеше"):
            assert response.status_code == 500
            attach_text("Тело ответа с ошибкой 500", response.text)
            assert "Internal Server Error" in response.text
