from pydantic import BaseModel, ConfigDict


class UserPublic(BaseModel):
    """Публичные данные пользователя (без пароля и хеша)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
