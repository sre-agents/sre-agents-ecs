from pydantic_settings import BaseSettings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    model_provider: str = "openai"
    model: str = "doubao-1-5-pro-256k-250115"
    model_api_base_url: str = "https://ark.cn-beijing.volces.com/api/v3/"
    model_api_key: str = ""

    judge_model: str = "doubao-1-5-pro-256k-250115"
    judge_model_api_base_url: str = "https://ark.cn-beijing.volces.com/api/v3/"
    judge_model_api_key: str = ""

    prometheus_pushgateway_url: str = ""
    prometheus_pushgateway_username: str = ""
    prometheus_pushgateway_password: str = ""

    ecs_mcp_server: str = ""

    embedding_model: str = "doubao-embedding-text-240715"
    embedding_dim: int = 2560
    embedding_model_api_base_url: str = (
        "https://ark.cn-beijing.volces.com/api/v3/embeddings"
    )
    embedding_model_api_key: str = ""

    opensearch_host: str = ""
    opensearch_port: str = "9200"
    opensearch_username: str = ""
    opensearch_password: str = ""

    kb_backend: str = "local"
    kb_search_topk: int = 2

    longterm_mem_backend: str = "local"
    longterm_mem_storage_mode: str = "useronly"
    longterm_mem_search_topk: int = 2

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


try:
    settings = Settings()
    logger.info(f"Settings loaded: {settings.model_dump()}")

    if settings.model_api_key == "":
        raise ValueError("MODEL_API_KEY is a null string.")

    if settings.judge_model_api_key == "":
        raise ValueError("JUDGE_MODEL_API_KEY is a null string.")
except ValueError as e:
    print(e)
