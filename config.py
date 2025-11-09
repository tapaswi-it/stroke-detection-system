# backend/app/config.py

# ✅ Correct imports for Pydantic v2
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:$N8179520236@localhost:5432/brain_stroke_db"
    ML_API_URL: AnyHttpUrl = "http://ml-service.local/predict"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
