# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.embeddings import FakeEmbeddings

from embeddings.base import EmbeddingsDB
from embeddings.documents import KnowledgeDocument


class QdrantEmbeddingsDB(EmbeddingsDB):
    """Qdrant vector database implementation for storing embeddings.
    
    This class implements the EmbeddingsDB interface using Qdrant as the backend.
    It handles dynamic embedding dimensions and collection management.
    """
    
    def __init__(self, url: str = "http://localhost:6333", api_key: Optional[str] = None, 
                 collection_name: str = "knowledge", **kwargs):
        """Initialize Qdrant client with connection details.
        
        Args:
            url: URL to Qdrant instance, defaults to http://localhost:6333
            api_key: Optional API key for authentication
            collection_name: Name of the collection to store embeddings
            **kwargs: Additional configuration parameters
        """
        # Initialize base class with all kwargs including url, api_key, and collection_name
        all_kwargs = {
            "url": url,
            "api_key": api_key,
            "collection_name": collection_name,
            **kwargs
        }
        super().__init__(**all_kwargs)
        
        # Initialize Qdrant client
        self._client = QdrantClient(url=url, api_key=api_key)
        self._collection_name = collection_name
        self._embedding_size = None  # Will be set when first document is added

    def _get_embedding_dimension(self, document: KnowledgeDocument) -> int:
        """Get embedding dimension from a document's retriever.
        
        Args:
            document: KnowledgeDocument with FAISS retriever
            
        Returns:
            int: Dimension of embeddings
            
        Raises:
            ValueError: If cannot determine embedding dimension
        """
        if document.retriever is None:
            raise ValueError("Document must have a retriever with embeddings")
        
        try:
            # Get first vector from FAISS index
            vector = document.retriever.index.reconstruct(0)
            return len(vector)
        except Exception as e:
            raise ValueError(f"Failed to determine embedding dimension: {str(e)}")

    def _ensure_collection_exists(self, dimension: Optional[int] = None) -> None:
        """Ensure collection exists with correct configuration.
        
        Args:
            dimension: Vector dimension for new collection
            
        Raises:
            ValueError: If collection setup fails
        """
        try:
            collections = self._client.get_collections().collections
            exists = any(c.name == self._collection_name for c in collections)
            
            if exists:
                # Get collection info
                collection_info = self._client.get_collection(self._collection_name)
                current_dim = collection_info.config.params.vectors.size
                
                # If dimension is provided and doesn't match, recreate collection
                if dimension is not None and current_dim != dimension:
                    self._client.recreate_collection(
                        collection_name=self._collection_name,
                        vectors_config=models.VectorParams(
                            size=dimension,
                            distance=models.Distance.COSINE
                        )
                    )
            elif dimension is not None:
                # Create new collection with specified dimension
                self._client.create_collection(
                    collection_name=self._collection_name,
                    vectors_config=models.VectorParams(
                        size=dimension,
                        distance=models.Distance.COSINE
                    )
                )
        except UnexpectedResponse as e:
            raise ValueError(f"Failed to setup Qdrant collection: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error setting up Qdrant collection: {str(e)}")

    def add_embedding(self, key: str, document: KnowledgeDocument) -> None:
        """Add a document embedding to Qdrant.
        
        Args:
            key: Unique identifier for the document
            document: KnowledgeDocument instance to store
            
        Raises:
            ValueError: If document is invalid or operation fails
        """
        if document.retriever is None:
            raise ValueError("Document must have a retriever with embeddings")
        
        try:
            # Get embedding dimension
            dimension = self._get_embedding_dimension(document)
            
            # Ensure collection exists with correct dimension
            self._ensure_collection_exists(dimension)
            
            # Convert document to point
            point = models.PointStruct(
                id=abs(hash(key)),  # Use absolute value of hash as point ID
                vector=document.retriever.index.reconstruct(0).tolist(),
                payload={
                    "key": key,
                    "title": document.title,
                    "source": document.source,
                    "sample_question": document.sample_question,
                    "description": document.description,
                    "context": document.context,
                    "provider": document.provider,
                    "text": next(iter(document.retriever.docstore._dict.values())).page_content if document.retriever.docstore._dict else ""
                }
            )
            
            # Add point to collection
            self._client.upsert(
                collection_name=self._collection_name,
                points=[point]
            )
            
        except Exception as e:
            raise ValueError(f"Failed to add embedding to Qdrant: {str(e)}")

    def get_document(self, key: str) -> Optional[KnowledgeDocument]:
        """Retrieve a document by its key.
        
        Args:
            key: Key of the document to retrieve
            
        Returns:
            KnowledgeDocument if found, None otherwise
        """
        try:
            points = self._client.scroll(
                collection_name=self._collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="key",
                            match=models.MatchValue(value=key)
                        )
                    ]
                ),
                limit=1
            )[0]

            if not points:
                return None

            point = points[0]
            
            # Create a minimal FAISS retriever with the stored text
            text = point.payload.get("text", "")
            if not text:
                return None
                
            # Create a simple retriever with the text
            doc = Document(page_content=text)
            fake_embeddings = FakeEmbeddings(size=len(point.vector))  # Use actual vector size
            index = FAISS.from_texts([text], fake_embeddings)
            
            return KnowledgeDocument(
                key=point.payload["key"],
                retriever=index,
                title=point.payload["title"],
                source=point.payload["source"],
                sample_question=point.payload["sample_question"],
                description=point.payload["description"],
                context=point.payload["context"],
                provider=point.payload["provider"]
            )
            
        except Exception as e:
            raise ValueError(f"Failed to get document from Qdrant: {str(e)}")

    def get_documents(self) -> List[KnowledgeDocument]:
        """Retrieve all documents.
        
        Returns:
            List of all KnowledgeDocument instances
        """
        try:
            points = self._client.scroll(
                collection_name=self._collection_name,
                limit=100  # Consider implementing pagination for large collections
            )[0]

            documents = []
            for point in points:
                # Create a minimal FAISS retriever with the stored text
                text = point.payload.get("text", "")
                if text:
                    doc = Document(page_content=text)
                    fake_embeddings = FakeEmbeddings(size=len(point.vector))
                    index = FAISS.from_texts([text], fake_embeddings)
                    
                    documents.append(KnowledgeDocument(
                        key=point.payload["key"],
                        retriever=index,
                        title=point.payload["title"],
                        source=point.payload["source"],
                        sample_question=point.payload["sample_question"],
                        description=point.payload["description"],
                        context=point.payload["context"],
                        provider=point.payload["provider"]
                    ))
            
            return documents
            
        except Exception as e:
            raise ValueError(f"Failed to get documents from Qdrant: {str(e)}")

    def get_keys(self) -> List[str]:
        """Get all document keys.
        
        Returns:
            List of all document keys
        """
        try:
            points = self._client.scroll(
                collection_name=self._collection_name,
                with_payload=["key"],
                limit=100  # Consider implementing pagination for large collections
            )[0]
            
            return [point.payload["key"] for point in points]
            
        except Exception as e:
            raise ValueError(f"Failed to get keys from Qdrant: {str(e)}")
