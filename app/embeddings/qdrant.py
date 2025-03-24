# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_community.vectorstores import FAISS

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
            vector=document.retriever.docstore._index_to_docstore_id[0],  # Get the first embedding vector
            payload={
                "key": key,
                "title": document.title,
                "source": document.source,
                "sample_question": document.sample_question,
                "description": document.description,
                "context": document.context,
                "provider": document.provider,
                # Store the embeddings and texts for recreating the retriever
                "embeddings": document.retriever.docstore._index_to_docstore_id,
                "texts": document.retriever.docstore._docstore
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
        
        # Recreate the FAISS retriever from stored embeddings
        embeddings = point.payload.get("embeddings", [])
        texts = point.payload.get("texts", {})
        if not embeddings or not texts:
            return None
            
        faiss = FAISS.from_embeddings(embeddings, list(texts.values()))
        
        return KnowledgeDocument(
            key=point.payload["key"],
            retriever=faiss,
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
