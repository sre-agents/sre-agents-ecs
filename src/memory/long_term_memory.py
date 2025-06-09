from typing import Literal

from google.adk.sessions import Session

from src.config import LONGTERM_MEM_SEARCH_TOPK, LONGTERM_MEM_STORAGE_MODE
from src.utils.logger import get_logger
from src.vector_database.vector_database_factory import (
    VectorDatabaseFactory,
    VectorType,
)

logger = get_logger(__name__)


def _user_key(app_name: str, user_id: str):
    return f"{app_name}-{user_id}"


class LongTermMemory:
    def __init__(
        self,
        name: str,
        top_k: int = LONGTERM_MEM_SEARCH_TOPK,
    ):
        logger.debug(f"Create long-term memory: {name}")

        self.top_k = top_k

        self.collection_name = name
        self.vector_client = VectorDatabaseFactory.create_vector_database(
            vector_type=VectorType.OPENSEARCH,
            collection_name=self.collection_name,
        )

    def _add_to_memory(self, event_text: str):
        self.vector_client.add_texts([event_text])

    def add_session_to_memory(
        self,
        session: Session,
        mode: Literal["useronly", "global"] = LONGTERM_MEM_STORAGE_MODE,
    ):
        event_text = ""
        for event in session.events:
            if mode == "useronly":
                if event.author == "user":
                    event_text += f"{event.author}: {event.content.parts[0].text}\n"
            else:
                if event.author == "user":
                    event_text += f"{event.author}: {event.content.parts[0].text}\n"
                elif event.content.parts[0] is not None and event.content.parts[0].text:
                    event_text += f"{event.author}: {event.content.parts[0].text}\n"

        self._add_to_memory(event_text)

    def search(self, query: str, top_k: int = None) -> list[str]:
        if not self.vector_client.collection_exist():
            logger.warning(
                f"Collection {self.collection_name} not found in long-term memory, please creating collection first. Skip search long-term memory."
            )
            return []

        top_k = self.top_k if top_k is None else top_k

        chunks = self.vector_client.search(
            query=query,
            top_k=top_k,
        )

        if len(chunks) == 0:
            logger.warning(f"No documents found in long-term memory. Query: {query}")
        return chunks
