import os
from typing import Any, Literal, Optional

from opensearchpy import OpenSearch, Urllib3HttpConnection, helpers
from pydantic import BaseModel

from src.config import (
    EMBEDDING_DIM,
    OPENSEARCH_HOST,
    OPENSEARCH_PASSWORD,
    OPENSEARCH_PORT,
    OPENSEARCH_USERNAME,
)
from src.utils.logger import get_logger
from src.vector_database.vector_database_factory import BaseVectorDatabase, Embeddings

logger = get_logger(__name__)

assert OPENSEARCH_HOST != "", "OPENSEARCH_HOST is not set"
assert OPENSEARCH_PORT != "", "OPENSEARCH_PORT is not set"
assert OPENSEARCH_USERNAME != "", "OPENSEARCH_USERNAME is not set"
assert OPENSEARCH_PASSWORD != "", "OPENSEARCH_PASSWORD is not set"


class OpenSearchConfig(BaseModel):
    host: str = OPENSEARCH_HOST
    port: int = int(OPENSEARCH_PORT)
    secure: bool = True  # use_ssl
    verify_certs: bool = False
    auth_method: Literal["basic", "aws_managed_iam"] = "basic"
    user: Optional[str] = OPENSEARCH_USERNAME
    password: Optional[str] = OPENSEARCH_PASSWORD

    def to_opensearch_params(self) -> dict[str, Any]:
        params = {
            "hosts": [{"host": self.host, "port": self.port}],
            "use_ssl": self.secure,
            "verify_certs": self.verify_certs,
            "connection_class": Urllib3HttpConnection,
            "pool_maxsize": 20,
        }
        ca_cert_path = os.getenv("OPENSEARCH_CA_CERT")
        if self.verify_certs and ca_cert_path:
            params["ca_certs"] = ca_cert_path

        params["http_auth"] = (self.user, self.password)

        return params


class OpenSearchVectorDatabase(BaseVectorDatabase):
    def __init__(self, collection_name: str):
        super().__init__(collection_name)
        self.embedding_client = Embeddings()
        self._client_config = OpenSearchConfig()
        self._client = self._init_client(self._client_config)
        self.create_collection()

    def _init_client(self, config: OpenSearchConfig) -> OpenSearch:
        return OpenSearch(**config.to_opensearch_params())

    def _get_settings(self) -> dict:
        settings = {"index": {"knn": True}}
        return settings

    def _get_mappings(self, dim: int = 2560) -> dict:
        mappings = {
            "properties": {
                "page_content": {
                    "type": "text",
                },
                "vector": {
                    "type": "knn_vector",
                    "dimension": dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "faiss",
                        "parameters": {"ef_construction": 64, "m": 8},
                    },
                },
            }
        }
        return mappings

    def create_collection(
        self,
        embedding_dim: int = int(EMBEDDING_DIM),
    ):
        if not self._client.indices.exists(index=self._collection_name):
            self._client.indices.create(
                index=self._collection_name,
                body={
                    "mappings": self._get_mappings(dim=embedding_dim),
                    "settings": self._get_settings(),
                },
            )
        else:
            logger.warning(f"Collection {self._collection_name} already exists.")

        return

    def add_texts(self, texts: list[str]):
        actions = []
        embeddings = self.embedding_client.embed_documents(texts)
        for i in range(len(texts)):
            action = {
                "_op_type": "index",
                "_index": self._collection_name,
                "_source": {
                    "page_content": texts[i],
                    "vector": embeddings[i],
                },
            }
            actions.append(action)
            pass

        helpers.bulk(
            client=self._client,
            actions=actions,
            timeout=30,
            max_retries=3,
        )
        return

    def collection_exist(self) -> bool:
        try:
            return self._client.indices.exists(index=self._collection_name)
        except Exception as e:
            logger.error(f"BadRequestError: {e}")
            if hasattr(e, "body") and e.body:
                logger.error(f"Error details: {e.body}")
            return False

    def _search_by_vector(self, query_vector: list[float], **kwargs: Any) -> list[str]:
        top_k = kwargs.get("top_k", 5)
        query = {
            "size": top_k,
            "query": {"knn": {"vector": {"vector": query_vector, "k": top_k}}},
        }
        response = self._client.search(index=self._collection_name, body=query)

        result_list = []
        for hit in response["hits"]["hits"]:
            result_list.append(hit["_source"]["page_content"])

        return result_list

    def search(self, query: str, **kwargs: Any) -> list[str]:
        query_vector = self.embedding_client.embed_query(query)
        return self._search_by_vector(query_vector)

    def get_health(self):
        response = self._client.cat.health()
        logger.info(response)
