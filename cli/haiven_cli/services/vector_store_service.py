# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.embeddings.base import Embeddings
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

class VectorStoreService(ABC):
    """Abstract base class for vector store implementations."""

    @abstractmethod
    def create_store(self, documents: List[Document], embeddings: Embeddings) -> Any:
        """Create a new vector store from documents.
        
        Args:
            documents: List of documents to store
            embeddings: Embeddings model to use
            
        Returns:
            The created vector store instance
        """
        pass

    @abstractmethod
    def load_store(self, store_path: str, embeddings: Embeddings) -> Any:
        """Load an existing vector store.
        
        Args:
            store_path: Path to the store
            embeddings: Embeddings model to use
            
        Returns:
            The loaded vector store instance
        """
        pass

    @abstractmethod
    def merge_stores(self, base_store: Any, new_store: Any) -> Any:
        """Merge two vector stores.
        
        Args:
            base_store: Base store to merge into
            new_store: Store to merge from
            
        Returns:
            The merged vector store instance
        """
        pass

    @abstractmethod
    def save_store(self, store: Any, store_path: str) -> None:
        """Save vector store to disk.
        
        Args:
            store: Store to save
            store_path: Path to save to
        """
        pass

class FAISSVectorStore(VectorStoreService):
    """FAISS implementation of vector store service."""

    def create_store(self, documents: List[Document], embeddings: Embeddings) -> Any:
        from langchain_community.vectorstores import FAISS
        return FAISS.from_documents(documents, embeddings)

    def load_store(self, store_path: str, embeddings: Embeddings) -> Any:
        from langchain_community.vectorstores import FAISS
        return FAISS.load_local(store_path, embeddings)

    def merge_stores(self, base_store: Any, new_store: Any) -> Any:
        base_store.merge_from(new_store)
        return base_store

    def save_store(self, store: Any, store_path: str) -> None:
        store.save_local(store_path)

class QdrantVectorStore(VectorStoreService):
    """Qdrant implementation of vector store service."""

    def __init__(self, url: str = "http://localhost:6333", collection_name: str = "haiven"):
        """Initialize Qdrant vector store.
        
        Args:
            url: Qdrant server URL
            collection_name: Name of the collection to use
        """
        self.url = url
        self.collection_name = collection_name
        self._client = None

    @property
    def client(self) -> QdrantClient:
        """Get or create Qdrant client instance."""
        if self._client is None:
            self._client = QdrantClient(url=self.url)
            # Test connection
            try:
                self._client.get_collections()
            except Exception as e:
                raise ConnectionError(f"Failed to connect to Qdrant server at {self.url}: {str(e)}")
        return self._client

    def _get_embedding_dimension(self, embeddings: Embeddings) -> int:
        """Get embedding dimension by creating a test embedding."""
        try:
            # Create a test embedding to get the dimension
            test_embedding = embeddings.embed_query("test")
            return len(test_embedding)
        except Exception as e:
            raise ValueError(f"Failed to determine embedding dimension: {str(e)}")

    def _setup_collection(self, embeddings: Embeddings) -> None:
        """Setup Qdrant collection with proper configuration."""
        dim = self._get_embedding_dimension(embeddings)
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if exists:
                # Get collection info to check dimension
                collection_info = self.client.get_collection(self.collection_name)
                if collection_info.config.params.vectors.size != dim:
                    # Recreate if dimension mismatch
                    self.client.recreate_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
                    )
            else:
                # Create new collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
                )
        except UnexpectedResponse as e:
            raise ValueError(f"Failed to setup Qdrant collection: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error setting up Qdrant collection: {str(e)}")

    def create_store(self, documents: List[Document], embeddings: Embeddings) -> Any:
        """Create a new Qdrant store from documents."""
        from langchain_community.vectorstores import Qdrant
        
        self._setup_collection(embeddings)
        
        try:
            return Qdrant.from_documents(
                documents,
                embeddings,
                url=self.url,
                collection_name=self.collection_name,
                force_recreate=False
            )
        except Exception as e:
            raise ValueError(f"Failed to create Qdrant store: {str(e)}")

    def load_store(self, store_path: str, embeddings: Embeddings) -> Any:
        """Load an existing Qdrant store."""
        from langchain_community.vectorstores import Qdrant
        
        self._setup_collection(embeddings)
        
        try:
            return Qdrant(
                client=self.client,
                collection_name=self.collection_name,
                embeddings=embeddings
            )
        except Exception as e:
            raise ValueError(f"Failed to load Qdrant store: {str(e)}")

    def merge_stores(self, base_store: Any, new_store: Any) -> Any:
        """Merge is handled automatically in Qdrant when adding documents."""
        return new_store

    def save_store(self, store: Any, store_path: str) -> None:
        """Qdrant persists automatically, no explicit save needed."""
        pass 