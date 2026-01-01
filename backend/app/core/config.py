import urllib.parse
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Ticket System"
    env: str = "dev"

    database_url: str | None = None

    db_user: str | None = None
    db_password: str | None = None
    db_host: str | None = None
    db_port: int | None = None
    db_name: str | None = None

    # NEW: store CA cert content (PEM) or a path
    db_ssl_ca_pem: str | None = None
    db_ssl_ca_path: str | None = None

    jwt_secret: str = "test-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    bootstrap_admin_email: str | None = None
    bootstrap_admin_password: str | None = None

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        if all([self.db_user, self.db_password, self.db_host, self.db_port, self.db_name]):
            password = urllib.parse.quote_plus(self.db_password)
            return (
                f"mysql+pymysql://{self.db_user}:{password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )

        return "sqlite+pysqlite:///:memory:"


settings = Settings()
