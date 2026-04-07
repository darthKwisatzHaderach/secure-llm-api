from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(alias="APP_NAME")
    env: str = Field(alias="ENV")

    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_alg: str = Field(alias="JWT_ALG")
    access_token_expire_minutes: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    sqlite_path: str = Field(alias="SQLITE_PATH")

    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(alias="OPENROUTER_BASE_URL")
    openrouter_model: str = Field(alias="OPENROUTER_MODEL")
    openrouter_site_url: str = Field(alias="OPENROUTER_SITE_URL")
    openrouter_app_name: str = Field(alias="OPENROUTER_APP_NAME")

    cors_allow_origins: list[str] = Field(default_factory=list, alias="CORS_ALLOW_ORIGINS")


settings = Settings()
