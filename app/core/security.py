"""Хеширование паролей и JWT без привязки к БД и роутам."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.errors import UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Хеш пароля для хранения в БД."""
    return pwd_context.hash(plain)


def verify_password(plain: str, password_hash: str) -> bool:
    """Проверка пароля против сохранённого хеша."""
    return pwd_context.verify(plain, password_hash)


def create_access_token(*, user_id: int, role: str) -> str:
    """
    Access JWT: sub (id пользователя), role, exp, iat.
    sub — строка, как принято в JWT.
    """
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Декодирование и проверка подписи и срока действия.
    При ошибке — UnauthorizedError (не HTTP).
    """
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_alg],
        )
    except JWTError as e:
        raise UnauthorizedError("Невалидный или истёкший токен") from e
