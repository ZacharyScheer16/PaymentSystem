"""Application configuration. Works with zero setup — defaults to a local SQLite file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "sqlite:///./payments.db"
    cors_origins: str = "http://localhost:5173"

    # NOTE: this default is fine for local dev only. A real deployment must
    # set JWT_SECRET to a long random value via the environment — anyone who
    # knows this secret can forge valid tokens for any user.
    jwt_secret: str = "dev-secret-change-in-production-please"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
