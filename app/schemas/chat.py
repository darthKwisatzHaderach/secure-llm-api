from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Запрос к LLM с опциональной системной инструкцией и параметрами контекста."""

    prompt: str = Field(min_length=1, description="Текущий запрос пользователя")
    system: str | None = Field(default=None, description="Системная инструкция для модели")
    max_history: int = Field(
        default=20,
        ge=1,
        le=200,
        description="Сколько последних сообщений истории подмешать в контекст",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Температура выборки (креативность модели)",
    )


class ChatResponse(BaseModel):
    """Ответ модели пользователю."""

    answer: str


class ChatMessagePublic(BaseModel):
    """Одно сообщение в истории (для GET /chat/history)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime
