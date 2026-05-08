from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    GROQ_API_KEY: str = ""
    TESSERACT_PATH: Optional[str] = None
    DEBUG: bool = False
    MAX_FILE_SIZE_MB: int = 10

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()