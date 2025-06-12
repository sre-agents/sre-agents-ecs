from typing import Literal

from google.adk.sessions import Session

from src.config import settings
from src.utils.logger import get_logger
from src.vector_database.vector_database_factory import (
    VectorDatabaseFactory,
    VectorType,
)

logger = get_logger(__name__)


class LongTermMemory:
    def __init__(
        self,
        name: str,
        backend: str = settings.longterm_mem_backend,
        top_k: int = settings.longterm_mem_search_topk,
    ):
        if backend not in VectorType.get_attr():
            logger.warning(
                f"Failed to create long term memory (name: {name}, backend: {backend}), change backend to `local`"
            )
            backend = "local"

        self.top_k = top_k
        self.collection_name = name
        try:
            self.vector_client = VectorDatabaseFactory.create_vector_database(
                vector_type=backend,
                collection_name=self.collection_name,
            )
            logger.debug(f"Create long-term memory: {name}, backend is {backend}")
        except Exception as e:
            logger.error(
                f"Failed to create long-term memory: {name}, backend is {backend}, the error is {e}, modify backend to `local`"
            )
            longterm_mem_backend = "local"
            self.vector_client = VectorDatabaseFactory.create_vector_database(
                vector_type=longterm_mem_backend,
                collection_name=self.collection_name,
            )

    def _add_to_memory(self, event_text: str):
        self.vector_client.add_texts([event_text])

    def add_session_to_memory(
        self,
        session: Session,
        mode: Literal["useronly", "global"] = settings.longterm_mem_storage_mode,
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
        top_k = self.top_k if top_k is None else top_k

        chunks = self.vector_client.search(
            query=query,
            top_k=top_k,
        )

        if len(chunks) == 0:
            logger.warning(f"No documents found in long-term memory. Query: {query}")
        return chunks
