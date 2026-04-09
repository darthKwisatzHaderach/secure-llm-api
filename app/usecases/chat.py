"""Сценарий чата с LLM: контекст, сохранение истории, вызов OpenRouter."""

from app.db.models import ChatMessage
from app.repositories.chat_messages import ChatMessageRepository
from app.services.openrouter_client import OpenRouterClient


class ChatUsecase:
    def __init__(
        self,
        messages: ChatMessageRepository,
        llm: OpenRouterClient,
    ) -> None:
        self._messages = messages
        self._llm = llm

    async def ask(
        self,
        user_id: int,
        *,
        prompt: str,
        system: str | None,
        max_history: int,
        temperature: float,
    ) -> str:
        """
        Порядок по ТЗ: собрать messages → сохранить prompt в БД → вызвать модель → сохранить ответ.
        """
        api_messages: list[dict[str, str]] = []
        if system:
            api_messages.append({"role": "system", "content": system})

        history = await self._messages.get_recent_by_user(user_id, limit=max_history)
        for row in history:
            api_messages.append({"role": row.role, "content": row.content})

        api_messages.append({"role": "user", "content": prompt})

        await self._messages.add_message(user_id=user_id, role="user", content=prompt)

        answer = await self._llm.chat_completions(api_messages, temperature=temperature)

        await self._messages.add_message(user_id=user_id, role="assistant", content=answer)

        return answer

    async def get_history(self, user_id: int, *, limit: int = 500) -> list[ChatMessage]:
        """История для API (последние limit сообщений в хронологическом порядке)."""
        return await self._messages.get_recent_by_user(user_id, limit=limit)

    async def clear_history(self, user_id: int) -> None:
        await self._messages.delete_all_by_user(user_id)
