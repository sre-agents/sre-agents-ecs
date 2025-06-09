import os

from dotenv import load_dotenv

load_dotenv()

#
# LiteLLM configs
#
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")
LLM = os.getenv(
    "LLM", "doubao-1-5-pro-256k-250115"
)  # We used this model because of its long-context and strong-fc capabilities
API_BASE_URL = os.getenv("API_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3/")
API_KEY = os.getenv("API_KEY", "")

assert API_KEY != "", (
    "Please set model API_KEY in environment variables (e.g., `.env` file)."
)

#
# Embedding configs
#
EMBEDDING_LM = os.getenv("EMBEDDING_LM", "doubao-embedding-text-240715")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM") or 2560)
EMBEDDING_API_BASE_URL = os.getenv(
    "EMBEDDING_API_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3/embeddings"
)

#
# MCP Server configs
#
ECS_MCP_SERVER = os.getenv("ECS_MCP_SERVER", "")

#
# Vector database configs
#
# 1. OpenSearch
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "")
OPENSEARCH_PORT = os.getenv("OPENSEARCH_PORT", "9200")
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME", "")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD", "")
# 2. (TODO) Chromadb
# ...

#
# Knowledgebase configs
#
KB_SEARCH_TOPK = int(os.getenv("KB_SEARCH_TOPK") or 2)

#
# Long-term memory configs
#
LONGTERM_MEM_SEARCH_TOPK = int(os.getenv("LONGTERM_MEM_SEARCH_TOPK") or 2)
# Two modes: useronly, global
# - useronly: only store user's input
# - global: store user's input and model's response
LONGTERM_MEM_STORAGE_MODE = os.getenv("LONGTERM_MEM_STORAGE_MODE", "useronly")
