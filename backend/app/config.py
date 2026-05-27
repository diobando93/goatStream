from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/goatstream"
    sports_api_url: str = "https://www.thesportsdb.com/api/v1/json/3"
    events_fetch_hour: int = 0  # UTC hour to run the daily events ingest
    admin_secret: str = "changeme"  # override via ADMIN_SECRET env var

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
