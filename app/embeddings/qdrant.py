# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.embeddings import FakeEmbeddings

from embeddings.base import EmbeddingsDB
from embeddings.documents import KnowledgeDocument


class QdrantEmbeddingsDB(EmbeddingsDB):
    def __init__(self, url: str, api_key: Optional[str] = None, collection_name: str = "knowledge", **kwargs):
        super().__init__(url=url, api_key=api_key, collection_name=collection_name, **kwargs)
        """Initialize Qdrant client with connection details.
        
        Args:
            url: URL to Qdrant instance
            api_key: Optional API key for authentication
            collection_name: Name of the collection to store embeddings
        """
        self._client = QdrantClient(url=url, api_key=api_key)
        self._collection_name = collection_name
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure the collection exists, create it if it doesn't."""
        collections = self._client.get_collections().collections
        exists = any(c.name == self._collection_name for c in collections)
        
        if not exists:
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # Default size for OpenAI embeddings
                    distance=models.Distance.COSINE
                )
            )

    def add_embedding(self, key: str, document: KnowledgeDocument):
        """Add a document embedding to Qdrant.
        
        Args:
            key: Unique identifier for the document
            document: KnowledgeDocument instance to store
        """
        # Get the embeddings from the document's retriever
        if document.retriever is None:
            raise ValueError("Document must have a retriever with embeddings")
        
        # Convert document to points
        point = models.PointStruct(
            id=abs(hash(key)),  # Use absolute value of hash as point ID
            vector=document.retriever.index.reconstruct(0).tolist(),  # Convert FAISS vector to list
            payload={
                "key": key,
                "title": document.title,
                "source": document.source,
                "sample_question": document.sample_question,
                "description": document.description,
                "context": document.context,
                "provider": document.provider,
                # Store only the first text for context
                "text": next(iter(document.retriever.docstore._dict.values())).page_content if document.retriever.docstore._dict else ""
            }
        )
        
        self._client.upsert(
            collection_name=self._collection_name,
            points=[point]
        )

    def get_document(self, key: str) -> Optional[KnowledgeDocument]:
        """Retrieve a document by its key.
        
        Args:
            key: Key of the document to retrieve
            
        Returns:
            KnowledgeDocument if found, None otherwise
        """
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
        fake_embeddings = FakeEmbeddings(size=1536)  # Standard embedding size
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

    def get_documents(self) -> List[KnowledgeDocument]:
        """Retrieve all documents.
        
        Returns:
            List of all KnowledgeDocument instances
        """
        points = self._client.scroll(
            collection_name=self._collection_name,
            limit=100  # Consider implementing pagination for large collections
        )[0]

        return [
            KnowledgeDocument(
                key=point.payload["key"],
                retriever=None,  # Note: Real implementation would need to handle retriever
                title=point.payload["title"],
                source=point.payload["source"],
                sample_question=point.payload["sample_question"],
                description=point.payload["description"],
                context=point.payload["context"],
                provider=point.payload["provider"]
            )
            for point in points
        ]

    def get_keys(self) -> List[str]:
        """Get all document keys.
        
        Returns:
            List of all document keys
        """
        points = self._client.scroll(
            collection_name=self._collection_name,
            with_payload=["key"],
            limit=100  # Consider implementing pagination for large collections
        )[0]
        
        return [point.payload["key"] for point in points]
