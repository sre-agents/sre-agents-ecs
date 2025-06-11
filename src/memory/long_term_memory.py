from typing import Literal
from google.adk.sessions import Session
from src.config import LONGTERM_MEM_SEARCH_TOPK, LONGTERM_MEM_STORAGE_MODE, LONGTERM_MEM_TYPE
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
        top_k: int = LONGTERM_MEM_SEARCH_TOPK,
        longterm_mem_type: str = LONGTERM_MEM_TYPE,
    ):
        if longterm_mem_type not in VectorType.get_attr():
            logger.warning(
                f"Failed to create long term memory, name is {name}, because longterm_mem_type `{longterm_mem_type}` not set, modify type to `local`"
            )
            longterm_mem_type = "local"

        self.top_k = top_k
        self.collection_name = name
        try:
            self.vector_client = VectorDatabaseFactory.create_vector_database(
                vector_type=longterm_mem_type,
                collection_name=self.collection_name,
            )
            logger.debug(f"Create long-term memory: {name}, type is {longterm_mem_type}")
        except Exception as e:
            logger.error(f"Failed to create long-term memory: {name}, type is {longterm_mem_type}, the error is {e}, modify type to `local`")
            longterm_mem_type = "local"
            self.vector_client = VectorDatabaseFactory.create_vector_database(
                vector_type=longterm_mem_type,
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
        top_k = self.top_k if top_k is None else top_k

        chunks = self.vector_client.search(
            query=query,
            top_k=top_k,
        )

        if len(chunks) == 0:
            logger.warning(f"No documents found in long-term memory. Query: {query}")
        return chunks
