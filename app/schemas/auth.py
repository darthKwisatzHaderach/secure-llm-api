from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Тело запроса регистрации."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128, description="Пароль пользователя")


class TokenResponse(BaseModel):
    """Ответ с JWT (OAuth2 / Swagger)."""

    access_token: str
    token_type: str = "bearer"
