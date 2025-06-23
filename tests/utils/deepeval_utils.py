from deepeval.key_handler import KEY_FILE_HANDLER, KeyValues
from deepeval.models import LocalModel

from src.config import settings

def create_eval_model(
        model_name: str = settings.judge_model,
        api_key: str = settings.judge_model_api_key,
        api_base: str = settings.judge_model_api_base_url,
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