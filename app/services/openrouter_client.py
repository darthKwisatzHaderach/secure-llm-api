"""HTTP-клиент OpenRouter (Chat Completions), без БД и без знания о пользователях."""

from typing import Any

import httpx

from app.core.config import Settings
from app.core.errors import ExternalServiceError


class OpenRouterClient:
    """
    Вызов POST /chat/completions относительно base URL из настроек
    (например https://openrouter.ai/api/v1).
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        site_url: str,
        app_title: str,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._site_url = site_url
        self._app_title = app_title

    def _headers(self) -> dict[str, str]:
        # Referer в HTTP — стандартное имя заголовка (в логах сервера часто пишут как HTTP-Referer)
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Referer": self._site_url,
            "X-Title": self._app_title,
            "Content-Type": "application/json",
        }

    async def chat_completions(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
    ) -> str:
        """
        Отправка списка сообщений {role, content} и возврат текста ответа assistant.
        """
        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, headers=self._headers(), json=payload)
        except httpx.RequestError as e:
            raise ExternalServiceError(f"Ошибка сети при обращении к OpenRouter: {e}") from e

        if response.status_code >= 400:
            body_preview = (response.text or "")[:500]
            raise ExternalServiceError(
                f"OpenRouter вернул ошибку HTTP {response.status_code}: {body_preview}"
            )

        try:
            data = response.json()
            choices = data["choices"]
            first = choices[0]
            msg = first["message"]
            content = msg.get("content")
            if content is None:
                return ""
            if isinstance(content, str):
                return content.strip()
            return str(content).strip()
        except (KeyError, IndexError, TypeError) as e:
            raise ExternalServiceError("Некорректная структура ответа OpenRouter") from e


def create_openrouter_client(settings: Settings) -> OpenRouterClient:
    """Сборка клиента из настроек окружения."""
    return OpenRouterClient(
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        site_url=settings.openrouter_site_url,
        app_title=settings.openrouter_app_name,
    )
