# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_embeddings import ApiEmbeddings
from starlette.middleware.sessions import SessionMiddleware


class TestApiEmbeddings(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.add_middleware(SessionMiddleware, secret_key="some-random-string")
        self.client = TestClient(self.app)

    def test_create_embeddings_success(self):
        # Mock the config service and embeddings client
        mock_config_service = MagicMock()
        mock_embedding_model = MagicMock()
        mock_config_service.load_embedding_model.return_value = mock_embedding_model

        # Mock the embeddings result
        mock_embeddings = MagicMock()
        with patch('embeddings.client.EmbeddingsClient') as mock_client:
            mock_client_instance = MagicMock()
            mock_client.return_value = mock_client_instance
            mock_client_instance.generate_from_documents.return_value = mock_embeddings

            # Initialize the API
            ApiEmbeddings(self.app, mock_config_service)

            # Test without output path
            response = self.client.post(
                "/api/embeddings",
                json={"text": "test text"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"status": "success"})

            # Test with output path
            response = self.client.post(
                "/api/embeddings",
                json={
                    "text": "test text",
                    "metadata": {"key": "value"},
                    "output_path": "/test/path"
                }
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {"status": "success", "path": "/test/path"}
            )

            # Verify embeddings were generated with correct parameters
            mock_client_instance.generate_from_documents.assert_called_with(
                text="test text",
                metadata=[{"key": "value"}]
            )
            mock_embeddings.save_local.assert_called_with("/test/path")

    def test_create_embeddings_failure(self):
        # Mock the config service to raise an exception
        mock_config_service = MagicMock()
        mock_config_service.load_embedding_model.side_effect = Exception("Test error")

        # Initialize the API
        ApiEmbeddings(self.app, mock_config_service)

        # Test the error case
        response = self.client.post(
            "/api/embeddings",
            json={"text": "test text"}
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "Server error: Test error"}) 