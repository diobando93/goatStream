from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/goatstream"
    sports_api_url: str = "https://www.thesportsdb.com/api/v1/json/3"
    events_fetch_hour: int = 0  # UTC hour to run the daily events ingest
    admin_secret: str = "changeme"  # override via ADMIN_SECRET env var
    # Max event duration in minutes per sport — controls the LIVE→FINISHED fallback
    max_duration_football: int = 180
    max_duration_f1: int = 240
    max_duration_basketball: int = 180
    max_duration_default: int = 180  # fallback for unlisted sports

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
