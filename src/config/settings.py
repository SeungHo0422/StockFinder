from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 예시 환경변수
    MONITOR_INTERVAL_MINUTES: int = 5
    TELEGRAM_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 