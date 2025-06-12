from abc import ABC, abstractmethod
from typing import Any

import requests

from src.config import settings


class VectorType:
    OPENSEARCH = "opensearch"
    LOCAL = "local"

    @classmethod
    def get_attr(cls) -> set[str]:
        return {
            value
            for attr, value in cls.__dict__.items()
            if not attr.startswith("__") and attr != "get_attr"
        }


class Embeddings:
    def __init__(
        self,
        model: str = settings.embedding_model,
        api_base: str = settings.embedding_model_api_base_url,
        api_key: str = settings.embedding_model_api_key,
    ):
        self.model = model
        self.url = api_base
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        MAX_CHARS = 4000
        data = {"model": self.model, "input": [text[:MAX_CHARS] for text in texts]}
        response = requests.post(self.url, headers=self.headers, json=data)
        response.raise_for_status()
        result = response.json()
        return [item["embedding"] for item in result["data"]]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class BaseVectorDatabase(ABC):
    def __init__(self, collection_name: str):
        self._collection_name = collection_name.lower()

    @abstractmethod
    def add_texts(self, texts: list[str]):
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, **kwargs: Any) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def is_empty(self):
        raise NotImplementedError


class VectorDatabaseFactory:
    @staticmethod
    def create_vector_database(
        vector_type: str, collection_name: str
    ) -> BaseVectorDatabase:
        if vector_type == VectorType.OPENSEARCH:
            from .opensearch_vector_database import OpenSearchVectorDatabase

            return OpenSearchVectorDatabase(collection_name)
        if vector_type == VectorType.LOCAL:
            from .local_database import LocalDataBase

            return LocalDataBase(collection_name)
        else:
            raise ValueError(f"Unsupported vector type: {vector_type}")
