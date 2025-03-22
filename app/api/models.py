from pydantic import BaseModel
from typing import Dict, List, Optional

class EmbeddingsRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, str]] = None
    output_path: Optional[str] = None

class DocumentRequest(BaseModel):
    context: Optional[str] = None
    include_base_context: Optional[bool] = True

class LoadDocumentsRequest(BaseModel):
    path: str
    context: Optional[str] = "base" 