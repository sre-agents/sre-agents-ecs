from pydantic_settings import BaseSettings

from src.utils.logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    judge_model: str = "doubao-1-5-pro-256k-250115"
    judge_model_api_base_url: str = "https://ark.cn-beijing.volces.com/api/v3/"
    judge_model_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

try:
    settings = Settings()
    logger.info(f"Settings loaded: {settings.model_dump()}")

    if settings.judge_model_api_key == "":
        raise ValueError("JUDGE_MODEL_API_KEY is a null string.")
except ValueError as e:
    print(e)
    print("Please set your JUDGE_MODEL_API_KEY in the .env file.")
