# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from abc import ABC, abstractmethod
from typing import List
from embeddings.documents import KnowledgeDocument


class EmbeddingsDB(ABC):
    """Abstract base class for embeddings databases."""
    
    def __init__(self, **kwargs):
        """Initialize the database with configuration.
        
        Args:
            **kwargs: Configuration parameters
        """
        self._config = {
            "type": kwargs.get("type") or self.__class__.__name__.lower().replace("embeddingsdb", ""),
            "config": kwargs
        }
    
    @abstractmethod
    def add_embedding(self, key: str, embedding: KnowledgeDocument) -> None:
        """Add a document embedding to the database."""
        pass

    @abstractmethod
    def get_document(self, key: str) -> KnowledgeDocument:
        """Retrieve a document by its key."""
        pass

    @abstractmethod
    def get_documents(self) -> List[KnowledgeDocument]:
        """Retrieve all documents."""
        pass

    @abstractmethod
    def get_keys(self) -> List[str]:
        """Get all document keys."""
        pass
