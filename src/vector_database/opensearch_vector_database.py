import os
from typing import Any, Literal, Optional

from opensearchpy import OpenSearch, Urllib3HttpConnection, helpers
from pydantic import BaseModel
from src.config import settings
from src.utils.logger import get_logger
from src.vector_database.vector_database_factory import BaseVectorDatabase, Embeddings

logger = get_logger(__name__)


class OpenSearchConfig(BaseModel):
    host: str
    port: str
    username: Optional[str]
    password: Optional[str]
    secure: bool = True  # ssl by default
    verify_certs: bool = False
    auth_method: Literal["basic", "aws_managed_iam"] = "basic"

    def to_opensearch_params(self) -> dict[str, Any]:
        params = {
            "hosts": [{"host": self.host, "port": int(self.port)}],
            "use_ssl": self.secure,
            "verify_certs": self.verify_certs,
            "connection_class": Urllib3HttpConnection,
            "pool_maxsize": 20,
        }
        ca_cert_path = os.getenv("OPENSEARCH_CA_CERT")
        if self.verify_certs and ca_cert_path:
            params["ca_certs"] = ca_cert_path

        params["http_auth"] = (self.username, self.password)

        return params


class OpenSearchVectorDatabase(BaseVectorDatabase):
    def __init__(self, collection_name: str):
        super().__init__(collection_name)
        self.embedding_client = Embeddings()

        # Currently, we use environment variables to configure the OpenSearch client, so we should check the envs first.
        opensearch_host = settings.opensearch_host
        opensearch_port = settings.opensearch_port
        opensearch_username = settings.opensearch_username
        opensearch_password = settings.opensearch_password
        assert opensearch_host != "", "OPENSEARCH_HOST cannot be empty."
        assert opensearch_port != "", "OPENSEARCH_PORT cannot be empty."
        assert opensearch_username != "", "OPENSEARCH_USERNAME cannot be empty."
        assert opensearch_password != "", "OPENSEARCH_PASSWORD cannot be empty."
        self._client_config = OpenSearchConfig(
            host=opensearch_host,
            port=opensearch_port,
            username=opensearch_username,
            password=opensearch_password,
        )

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
        embedding_dim: int = settings.embedding_dim,
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
        self._client.indices.refresh(index=self._collection_name)
        return

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

    def is_empty(self):
        response = self._client.count(index=self._collection_name)
        return response["count"] == 0
