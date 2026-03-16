"""Вспомогательные модули тестового проекта."""

from .allure import (
    attach_json,
    attach_request_details,
    attach_response_details,
    attach_text,
    mask_sensitive_data,
)

__all__ = [
    "attach_json",
    "attach_request_details",
    "attach_response_details",
    "attach_text",
    "mask_sensitive_data",
]
