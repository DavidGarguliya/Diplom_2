"""Вспомогательные утилиты для шагов и вложений Allure."""

from __future__ import annotations

import json
from typing import Any

import allure
import requests

SENSITIVE_FIELDS = {"password", "accessToken", "refreshToken", "authorization"}


def mask_sensitive_data(data: Any) -> Any:
    """Маскирует чувствительные поля перед вложением в отчёт."""
    if isinstance(data, dict):
        masked: dict[str, Any] = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                masked[key] = "***СКРЫТО***"
            else:
                masked[key] = mask_sensitive_data(value)
        return masked
    if isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data


def attach_json(name: str, data: Any) -> None:
    """Прикладывает JSON-вложение к шагу Allure."""
    allure.attach(
        json.dumps(mask_sensitive_data(data), ensure_ascii=False, indent=2),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_text(name: str, text: str) -> None:
    """Прикладывает текстовое вложение к шагу Allure."""
    allure.attach(
        text,
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )


def attach_request_details(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    payload: Any | None = None,
) -> None:
    """Прикладывает детали HTTP-запроса к отчёту."""
    attach_text("HTTP-запрос: метод и URL", f"{method} {url}")
    if headers:
        attach_json("HTTP-запрос: заголовки", headers)
    if params:
        attach_json("HTTP-запрос: query-параметры", params)
    if payload is not None:
        attach_json("HTTP-запрос: тело", payload)


def attach_response_details(response: requests.Response) -> None:
    """Прикладывает детали HTTP-ответа к отчёту."""
    attach_text(
        "HTTP-ответ: статус",
        f"{response.status_code} {response.reason}",
    )
    attach_json("HTTP-ответ: заголовки", dict(response.headers))
    try:
        attach_json("HTTP-ответ: тело JSON", response.json())
    except ValueError:
        attach_text("HTTP-ответ: тело TEXT", response.text)
