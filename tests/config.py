import os

from dotenv import load_dotenv

load_dotenv()

#
# LiteLLM configs
#
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")
JUDGE_LLM = os.getenv(
    "JUDGE_LLM", "doubao-1-5-pro-256k-250115"
)  # We used this model because of its long-context and strong-fc capabilities
JUDGE_LLM_API_BASE_URL = os.getenv("JUDGE_LLM_API_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3/")
JUDGE_LLM_API_KEY = os.getenv("JUDGE_LLM_API_KEY", "")

assert JUDGE_LLM_API_KEY != "", (
    "Please set model JUDGE_LLM_API_KEY in environment variables (e.g., `.env` file)."
)