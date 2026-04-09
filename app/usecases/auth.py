"""Регистрация, логин и профиль (без FastAPI / HTTPException)."""

from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.repositories.users import UserRepository


class AuthUsecase:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def register(self, *, email: str, password: str) -> User:
        if await self._users.get_by_email(email) is not None:
            raise ConflictError("Email уже занят")
        password_hash = hash_password(password)
        return await self._users.create(email=email, password_hash=password_hash, role="user")

    async def login(self, *, email: str, password: str) -> str:
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Неверный email или пароль")
        return create_access_token(user_id=user.id, role=user.role)

    async def get_profile(self, user_id: int) -> User:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user
