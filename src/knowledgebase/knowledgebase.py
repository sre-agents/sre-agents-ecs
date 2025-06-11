from src.config import KB_SEARCH_TOPK, KB_TYPE
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
        top_k: int = KB_SEARCH_TOPK,
        data: list[str] = None,
        kb_type: str = KB_TYPE,
    ):
        self.name = name
        self.top_k = top_k
        if kb_type not in VectorType.get_attr():
            logger.warning(
                f"Failed to create knowledgebase, name is {name}, because kb_type `{kb_type}` not set, modify type to `local`"
            )
            kb_type = "local"

        try:
            self.vdb_client = VectorDatabaseFactory.create_vector_database(
                vector_type=kb_type, collection_name=self.name
            )
            logger.debug(f"Create knowledgebase, name is {name}, type is {kb_type}")
        except Exception as e:
            logger.error(f"Failed to create knowledgebase, name is {name}, type is {kb_type}, the error is {e}, modify type to `local`")
            kb_type = "local"
            self.vdb_client = VectorDatabaseFactory.create_vector_database(
                vector_type=kb_type, collection_name=self.name
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
