"""Настройки тестового проекта."""

from __future__ import annotations

import os

DEFAULT_BASE_URL = "https://stellarburgers.education-services.ru/api"
BASE_URL_ENV_VAR = "STELLAR_BURGERS_BASE_URL"


def resolve_base_url(cli_base_url: str | None = None) -> str:
    """Возвращает базовый URL API с учётом аргумента запуска и окружения."""
    if cli_base_url:
        return cli_base_url.rstrip("/")

    env_base_url = os.getenv(BASE_URL_ENV_VAR)
    if env_base_url:
        return env_base_url.rstrip("/")

    return DEFAULT_BASE_URL
