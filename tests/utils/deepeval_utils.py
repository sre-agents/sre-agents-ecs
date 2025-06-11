from deepeval.key_handler import KEY_FILE_HANDLER, KeyValues
from deepeval.models import LocalModel

from tests.config import (
    JUDGE_LLM_API_BASE_URL,
    JUDGE_LLM_API_KEY,
    JUDGE_LLM
)


def create_eval_model(
        model_name: str = JUDGE_LLM,
        api_key: str = JUDGE_LLM_API_KEY,
        api_base: str = JUDGE_LLM_API_BASE_URL,
):
    KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_NAME, model_name)
    KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_BASE_URL, api_base)
    if api_key:
        KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_API_KEY, api_key)
    if format:
        KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_FORMAT, "json")
    KEY_FILE_HANDLER.write_key(KeyValues.USE_LOCAL_MODEL, "YES")
    KEY_FILE_HANDLER.write_key(KeyValues.USE_AZURE_OPENAI, "NO")

    return LocalModel()