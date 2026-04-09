"""Доменные исключения: бизнес-слой не зависит от FastAPI."""


class AppError(Exception):
    """Базовая ошибка приложения."""

    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(message)


class ConflictError(AppError):
    """Конфликт данных (например, email уже занят)."""


class UnauthorizedError(AppError):
    """Неавторизован (неверные учётные данные или токен)."""


class ForbiddenError(AppError):
    """Недостаточно прав."""


class NotFoundError(AppError):
    """Сущность не найдена."""


class ExternalServiceError(AppError):
    """Ошибка внешнего сервиса (например, OpenRouter)."""
