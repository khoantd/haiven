# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import Dict, Type

from embeddings.base import EmbeddingsDB
from embeddings.in_memory import InMemoryEmbeddingsDB
from embeddings.qdrant import QdrantEmbeddingsDB


class EmbeddingsDBFactory:
    """Factory for creating embeddings database instances."""
    
    _db_types: Dict[str, Type[EmbeddingsDB]] = {
        "in_memory": InMemoryEmbeddingsDB,
        "qdrant": QdrantEmbeddingsDB
    }
    
    @classmethod
    def create(cls, db_type: str, **kwargs) -> EmbeddingsDB:
        """Create a new embeddings database instance.
        
        Args:
            db_type: Type of database to create ("in_memory" or "qdrant")
            **kwargs: Additional arguments to pass to the database constructor
            
        Returns:
            An instance of the requested database type
            
        Raises:
            ValueError: If db_type is not supported
        """
        print(f"Creating embeddings database of type: {db_type}")
        if db_type not in cls._db_types:
            raise ValueError(f"Unsupported database type: {db_type}. "
                           f"Supported types are: {list(cls._db_types.keys())}")
            
        db_class = cls._db_types[db_type]
        
        # For Qdrant, ensure required config is present
        if db_type == "qdrant":
            if "url" not in kwargs:
                kwargs["url"] = "http://localhost:6333"  # Default URL
            if "collection_name" not in kwargs:
                kwargs["collection_name"] = "knowledge"  # Default collection
        
        return db_class(**kwargs)
