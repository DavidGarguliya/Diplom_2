# API автотесты Stellar Burgers

## Стек
- `pytest`
- `requests`
- `allure-pytest`

## Структура проекта
```text
api/
├── __init__.py
└── client.py
helpers/
├── __init__.py
└── allure.py
tests/
├── conftest.py
├── test_order_creation.py
├── test_user_creation.py
└── test_user_login.py
```

- `api` содержит API-слой и клиент для работы с эндпоинтами.
- `helpers` содержит вспомогательные утилиты, не связанные напрямую с тест-кейсами.
- `tests/conftest.py` остаётся точкой входа для общих фикстур.

## Установка
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск тестов
```bash
pytest
```

## Генерация Allure-результатов
```bash
pytest --alluredir=allure-results
```
