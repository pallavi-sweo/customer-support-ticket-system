import urllib.parse
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str
    env: str

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    jwt_secret: str
    jwt_algorithm: str
    jwt_expire_minutes: int

    bootstrap_admin_email: str | None = None
    bootstrap_admin_password: str | None = None

    @property
    def database_url(self) -> str:
        password = urllib.parse.quote_plus(self.db_password)
        return (
            f"mysql+pymysql://{self.db_user}:"
            f"{password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}"
        )


settings = Settings()
