from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def _build_sqlite_url(sqlite_path: str) -> str:
    if sqlite_path.startswith("/"):
        return f"sqlite+aiosqlite:////{sqlite_path.lstrip('/')}"
    return f"sqlite+aiosqlite:///{sqlite_path}"


DATABASE_URL = _build_sqlite_url(settings.sqlite_path)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
