# API автотесты Stellar Burgers

## Стек
- `pytest`
- `requests`
- `allure-pytest`

## Структура проекта
```text
api/
├── __init__.py
├── auth_client.py
├── client.py
├── ingredient_client.py
├── order_client.py
└── user_client.py
helpers/
├── __init__.py
└── allure.py
data/
├── __init__.py
├── order_data.py
└── user_data.py
settings.py
tests/
├── conftest.py
├── test_order_creation.py
├── test_user_creation.py
└── test_user_login.py
```

- `api` содержит API-слой и отдельные клиенты по зонам ответственности.
- `helpers` содержит вспомогательные утилиты, не связанные напрямую с тест-кейсами.
- `data` содержит тестовые данные и ожидаемые ответы API.
- `settings.py` содержит конфигурацию проекта и базовый URL API.
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

## Переопределение базового URL API
Через аргумент запуска:
```bash
pytest --base-url https://stellarburgers.education-services.ru/api
```

Через переменную окружения:
```bash
export STELLAR_BURGERS_BASE_URL=https://stellarburgers.education-services.ru/api
pytest
```

## Генерация Allure-результатов
```bash
pytest --alluredir=allure-results
```
