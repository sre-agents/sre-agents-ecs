from src.config import KB_SEARCH_TOPK
from src.utils.logger import get_logger
from src.vector_database.vector_database_factory import (
    VectorDatabaseFactory,
    VectorType,
)

logger = get_logger(__name__)


class KnowledgeBase:
    def __init__(
        self,
        name: str = "knowledgebase_",
        top_k: int = KB_SEARCH_TOPK,
        data: list[str] = None,
    ):
        logger.debug(f"Create knowledgebase with {name} collection")

        self.collection_name = name
        self.top_k = top_k

        self.vdb_client = VectorDatabaseFactory.create_vector_database(
            vector_type=VectorType.OPENSEARCH, collection_name=name
        )

        if data is not None and not self.vdb_client.collection_exist():
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
