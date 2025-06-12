from src.config import settings
from src.utils.logger import get_logger
from src.vector_database.vector_database_factory import (
    VectorDatabaseFactory,
    VectorType,
)

logger = get_logger(__name__)


class KnowledgeBase:
    def __init__(
        self,
        name: str = "default_knowledgebase",
        backend: str = settings.kb_backend,
        top_k: int = settings.kb_search_topk,
        data: list[str] = None,
    ):
        self.name = name
        self.top_k = top_k
        if backend not in VectorType.get_attr():
            logger.warning(
                f"Failed to create {name} knowledgebase, as the backend `{backend}` is not supported, changing type to `local`"
            )
            backend = "local"

        try:
            self.vdb_client = VectorDatabaseFactory.create_vector_database(
                vector_type=backend, collection_name=self.name
            )
            logger.debug(f"Create knowledgebase, name is {name}, backend is {backend}")
        except Exception as e:
            logger.error(
                f"Failed to create {name} knowledgebase: {e}, changing type to `local`"
            )
            backend = "local"
            self.vdb_client = VectorDatabaseFactory.create_vector_database(
                vector_type=backend, collection_name=self.name
            )

        if data is not None and self.vdb_client.is_empty():
            self.vdb_client.add_texts(data)

    def search(self, query: str, top_k: int = None) -> list[str]:
        """Retrieve documents similar to the query text in the vector database.

        Args:
            query (str): The query text to be retrieved (e.g., "Who proposed the Turing machine model?")

        Returns:
            list[str]: A list of the top most similar document contents retrieved (sorted by vector similarity)
        """
        top_k = self.top_k if top_k is None else top_k

        result = self.vdb_client.search(query=query, top_k=top_k)
        if len(result) == 0:
            logger.warning(f"No documents found in knowledgebase. Query: {query}")
        return result
