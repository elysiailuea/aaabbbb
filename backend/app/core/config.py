from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    admin_username: str = "admin"
    admin_password: str = "admin123"

    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_minutes: int = 720

    database_url: str = "postgresql+psycopg://app:app@postgres:5432/honeypot"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    redis_url: str = "redis://redis:6379/2"

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()