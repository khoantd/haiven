# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import pytest
from unittest.mock import MagicMock, patch
from langchain.schema import Document
from haiven_cli.services.vector_store_service import FAISSVectorStore, QdrantVectorStore

class TestFAISSVectorStore:
    def test_create_store(self):
        store = FAISSVectorStore()
        documents = [Document(page_content="test", metadata={})]
        embeddings = MagicMock()
        
        with patch("langchain_community.vectorstores.FAISS") as mock_faiss:
            mock_faiss.from_documents.return_value = "test_store"
            result = store.create_store(documents, embeddings)
            
            mock_faiss.from_documents.assert_called_once_with(documents, embeddings)
            assert result == "test_store"
            
    def test_load_store(self):
        store = FAISSVectorStore()
        embeddings = MagicMock()
        
        with patch("langchain_community.vectorstores.FAISS") as mock_faiss:
            mock_faiss.load_local.return_value = "loaded_store"
            result = store.load_store("test_path", embeddings)
            
            mock_faiss.load_local.assert_called_once_with("test_path", embeddings)
            assert result == "loaded_store"
            
    def test_merge_stores(self):
        store = FAISSVectorStore()
        base_store = MagicMock()
        new_store = "new_store"
        
        result = store.merge_stores(base_store, new_store)
        
        base_store.merge_from.assert_called_once_with(new_store)
        assert result == base_store
        
    def test_save_store(self):
        store = FAISSVectorStore()
        vector_store = MagicMock()
        
        store.save_store(vector_store, "test_path")
        
        vector_store.save_local.assert_called_once_with("test_path")

class TestQdrantVectorStore:
    def test_init_validates_connection(self):
        with patch("qdrant_client.QdrantClient") as mock_client:
            client_instance = MagicMock()
            mock_client.return_value = client_instance
            
            QdrantVectorStore()
            
            client_instance.get_collections.assert_called_once()
            
    def test_create_store(self):
        store = QdrantVectorStore()
        documents = [Document(page_content="test", metadata={})]
        embeddings = MagicMock()
        embeddings.client.get_embedding_dimension.return_value = 1536
        
        with patch("qdrant_client.QdrantClient") as mock_client, \
             patch("langchain_community.vectorstores.Qdrant") as mock_qdrant:
            client_instance = MagicMock()
            mock_client.return_value = client_instance
            mock_qdrant.from_documents.return_value = "test_store"
            
            result = store.create_store(documents, embeddings)
            
            client_instance.recreate_collection.assert_called_once_with(
                collection_name="haiven",
                vectors_config={
                    "size": 1536,
                    "distance": "Cosine"
                }
            )
            mock_qdrant.from_documents.assert_called_once_with(
                documents,
                embeddings,
                url="http://localhost:6333",
                collection_name="haiven",
                force_recreate=False
            )
            assert result == "test_store"
            
    def test_load_store_creates_collection_if_not_exists(self):
        store = QdrantVectorStore()
        embeddings = MagicMock()
        embeddings.client.get_embedding_dimension.return_value = 1536
        
        with patch("qdrant_client.QdrantClient") as mock_client, \
             patch("langchain_community.vectorstores.Qdrant") as mock_qdrant:
            client_instance = MagicMock()
            collections_response = MagicMock()
            collections_response.collections = []
            client_instance.get_collections.return_value = collections_response
            mock_client.return_value = client_instance
            mock_qdrant.return_value = "loaded_store"
            
            result = store.load_store("test_path", embeddings)
            
            client_instance.create_collection.assert_called_once_with(
                collection_name="haiven",
                vectors_config={
                    "size": 1536,
                    "distance": "Cosine"
                }
            )
            mock_qdrant.assert_called_once_with(
                client=client_instance,
                collection_name="haiven",
                embeddings=embeddings
            )
            assert result == "loaded_store"
            
    def test_merge_stores_returns_new_store(self):
        store = QdrantVectorStore()
        base_store = MagicMock()
        new_store = "new_store"
        
        result = store.merge_stores(base_store, new_store)
        
        assert result == new_store
        
    def test_save_store_does_nothing(self):
        store = QdrantVectorStore()
        vector_store = MagicMock()
        
        store.save_store(vector_store, "test_path")
        # No assertions needed as this method does nothing 