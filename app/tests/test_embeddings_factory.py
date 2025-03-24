# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import pytest
from unittest.mock import patch, MagicMock
from embeddings.factory import EmbeddingsDBFactory
from embeddings.in_memory import InMemoryEmbeddingsDB
from embeddings.qdrant import QdrantEmbeddingsDB


def test_create_in_memory_db():
    """Test creating an in-memory database."""
    db = EmbeddingsDBFactory.create("in_memory", type="in_memory")
    assert isinstance(db, InMemoryEmbeddingsDB)
    assert db._config["type"] == "in_memory"
    assert db._config["config"] == {"type": "in_memory"}


@patch('embeddings.qdrant.QdrantClient')
def test_create_qdrant_db(mock_qdrant):
    """Test creating a Qdrant database with configuration."""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.get_collections.return_value = MagicMock(collections=[])
    mock_qdrant.return_value = mock_instance

    config = {
        "url": "http://localhost:6333",
        "api_key": "test-key",
        "collection_name": "test-collection",
        "type": "qdrant"
    }
    db = EmbeddingsDBFactory.create("qdrant", **config)
    assert isinstance(db, QdrantEmbeddingsDB)
    assert db._config["type"] == "qdrant"
    assert db._config["config"] == config


def test_create_invalid_db():
    """Test creating an invalid database type raises error."""
    with pytest.raises(ValueError) as exc:
        EmbeddingsDBFactory.create("invalid")
    assert "Unsupported database type: invalid" in str(exc.value)
