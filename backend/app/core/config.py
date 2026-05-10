from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "MissedRun Self-hosted"
    app_env: str = "development"
    database_url: str = "postgresql://missedrun:missedrun@postgres:5432/missedrun"

    backend_cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str = "MissedRun"
    smtp_reply_to: str | None = None

    alert_email: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
