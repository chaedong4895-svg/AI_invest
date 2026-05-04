from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite:///./ai_invest.db"
    redis_url: str = "redis://localhost:6379/0"

    openai_api_key: str = ""
    openai_model_report: str = "gpt-4o"
    openai_model_news: str = "gpt-4o-mini"

    telegram_bot_token: str = ""
    telegram_admin_chat_id: str = ""

    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@example.com"

    admin_secret_key: str = "change-this-secret"
    frontend_url: str = "http://localhost:3000"

    # KST 기준 스케줄 (UTC로 변환: KST - 9h)
    schedule_collect_hour_utc: int = 21   # KST 06:05
    schedule_collect_minute_utc: int = 5
    schedule_notify_hour_utc: int = 22    # KST 07:00
    schedule_notify_minute_utc: int = 0

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
