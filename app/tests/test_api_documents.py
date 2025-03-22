# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_documents import ApiDocuments
from embeddings.documents import KnowledgeDocument
from starlette.middleware.sessions import SessionMiddleware


class TestApiDocuments(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.add_middleware(SessionMiddleware, secret_key="some-random-string")
        self.client = TestClient(self.app)

    def test_get_documents(self):
        # Mock the knowledge manager
        mock_knowledge_manager = MagicMock()
        mock_document = MagicMock(spec=KnowledgeDocument)
        mock_document.key = "test-key"
        mock_document.title = "Test Title"
        mock_document.description = "Test Description"
        mock_document.get_source_title_link.return_value = "http://test.com"
        
        mock_knowledge_manager.knowledge_base_documents.get_documents.return_value = [mock_document]

        # Initialize the API
        ApiDocuments(self.app, mock_knowledge_manager)

        # Test getting documents
        response = self.client.get("/api/documents")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{
            "key": "test-key",
            "title": "Test Title",
            "description": "Test Description",
            "source": "http://test.com"
        }])

        # Verify the correct parameters were used
        mock_knowledge_manager.knowledge_base_documents.get_documents.assert_called_with(
            context=None,
            include_base_context=True
        )

    def test_load_documents(self):
        # Mock the knowledge manager
        mock_knowledge_manager = MagicMock()

        # Initialize the API
        ApiDocuments(self.app, mock_knowledge_manager)

        # Test loading documents into base context
        response = self.client.post(
            "/api/documents/load",
            json={"path": "/test/path", "context": "base"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success", "context": "base"})

        # Verify the correct method was called
        mock_knowledge_manager.knowledge_base_documents.load_documents_for_base.assert_called_with(
            "/test/path"
        )

    def test_get_document(self):
        # Mock the knowledge manager
        mock_knowledge_manager = MagicMock()
        mock_document = MagicMock(spec=KnowledgeDocument)
        mock_document.key = "test-key"
        mock_document.title = "Test Title"
        mock_document.description = "Test Description"
        mock_document.get_source_title_link.return_value = "http://test.com"
        
        mock_knowledge_manager.knowledge_base_documents.get_document.return_value = mock_document

        # Initialize the API
        ApiDocuments(self.app, mock_knowledge_manager)

        # Test getting a specific document
        response = self.client.get("/api/documents/test-key")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "key": "test-key",
            "title": "Test Title",
            "description": "Test Description",
            "source": "http://test.com"
        })

        # Test getting a non-existent document
        mock_knowledge_manager.knowledge_base_documents.get_document.return_value = None
        response = self.client.get("/api/documents/non-existent")
        self.assertEqual(response.status_code, 404) 