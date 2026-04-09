"""
Фикстуры тестов.

Важно: SQLITE_PATH задаём до любого импорта `app`, иначе engine привяжется к чужой БД.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from starlette.testclient import TestClient

# Изолированная БД для прогона тестов (не трогаем ./app.db разработчика)
_TESTS_DIR = Path(__file__).resolve().parent
os.environ["SQLITE_PATH"] = str(_TESTS_DIR / "test_app.sqlite3")

from app.main import create_app  # noqa: E402


@pytest.fixture
def app() -> Generator:
    """Приложение без подмен зависимостей."""
    application = create_app()
    yield application


@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    """HTTP-клиент с отработкой lifespan (create_all таблиц)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def app_with_fake_llm() -> Generator:
    """OpenRouter заменён заглушкой — сеть не нужна."""
    from app.api import deps
    from app.main import create_app

    class _FakeOpenRouter:
        async def chat_completions(
            self,
            messages: list[dict[str, str]],
            *,
            temperature: float = 0.7,
        ) -> str:
            _ = messages
            _ = temperature
            return "ответ-заглушка"

    application = create_app()
    application.dependency_overrides[deps.get_openrouter_client] = lambda: _FakeOpenRouter()
    try:
        yield application
    finally:
        application.dependency_overrides.clear()


@pytest.fixture
def client_fake_llm(app_with_fake_llm) -> Generator[TestClient, None, None]:
    with TestClient(app_with_fake_llm) as test_client:
        yield test_client
