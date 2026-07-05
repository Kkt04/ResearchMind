from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    groq_api_key: str = ""
    cognee_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    database_url: str = "sqlite+aiosqlite:///./researchmind.db"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()