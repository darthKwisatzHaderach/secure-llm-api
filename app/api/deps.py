"""DI: сессия БД, репозитории, usecases, текущий пользователь по JWT."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import UnauthorizedError as DomainUnauthorizedError
from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.repositories.chat_messages import ChatMessageRepository
from app.repositories.users import UserRepository
from app.services.openrouter_client import OpenRouterClient, create_openrouter_client
from app.usecases.auth import AuthUsecase
from app.usecases.chat import ChatUsecase

# Swagger: логин по форме OAuth2; токен вводится через Authorize
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


def get_user_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> UserRepository:
    return UserRepository(session)


def get_chat_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> ChatMessageRepository:
    return ChatMessageRepository(session)


def get_openrouter_client() -> OpenRouterClient:
    return create_openrouter_client(settings)


def get_auth_usecase(
    users: Annotated[UserRepository, Depends(get_user_repo)],
) -> AuthUsecase:
    return AuthUsecase(users)


def get_chat_usecase(
    messages: Annotated[ChatMessageRepository, Depends(get_chat_repo)],
    llm: Annotated[OpenRouterClient, Depends(get_openrouter_client)],
) -> ChatUsecase:
    return ChatUsecase(messages, llm)


async def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> int:
    """Декодирование JWT; доменная ошибка → HTTP 401."""
    try:
        payload = decode_access_token(token)
    except DomainUnauthorizedError as e:
        raise HTTPException(status_code=401, detail=e.message) from e

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="В токене отсутствует sub")

    try:
        return int(sub)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=401, detail="Некорректный идентификатор в sub") from e
