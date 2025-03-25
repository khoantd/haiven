from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class VectorStoreConfig:
    type: str  # "faiss" or "qdrant"
    settings: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'VectorStoreConfig':
        return VectorStoreConfig(
            type=data.get("type", "faiss"),
            settings=data.get("settings", {})
        ) 