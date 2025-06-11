from typing import Any

from .vector_database_factory import BaseVectorDatabase



class LocalDataBase(BaseVectorDatabase):
    """
    This database is only used for basic demonstration.
    It does not support the vector search function, and each search process returns all data.
    """
    def __init__(self, collection_name: str):
        super().__init__(collection_name)
        self.data = []

    def add_texts(self, texts: list[str]):
        self.data.extend(texts)

    def search(self, query: str, **kwargs: Any) -> list[str]:
        return self.data

    def is_empty(self):
        return len(self.data) == 0