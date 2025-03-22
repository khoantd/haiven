# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger

from api.models import DocumentRequest, LoadDocumentsRequest
from config_service import ConfigService
from knowledge_manager import KnowledgeManager
from logger import HaivenLogger


class ApiDocuments:
    def __init__(self, app: FastAPI, knowledge_manager: KnowledgeManager):
        self.knowledge_manager = knowledge_manager

        @app.get("/api/documents")
        @logger.catch(reraise=True)
        async def get_documents(request: Request, context: str = None, include_base_context: bool = True):
            """Get all documents from a specific context"""
            try:
                documents = self.knowledge_manager.knowledge_base_documents.get_documents(
                    context=context,
                    include_base_context=include_base_context
                )
                
                response_data = [
                    {
                        "key": doc.key,
                        "title": doc.title,
                        "description": doc.description,
                        "source": doc.get_source_title_link(),
                    }
                    for doc in documents
                ]
                
                return JSONResponse(response_data)

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.post("/api/documents/load")
        @logger.catch(reraise=True)
        async def load_documents(request: Request, data: LoadDocumentsRequest):
            """Load documents from a specified path into a context"""
            try:
                if data.context == "base":
                    self.knowledge_manager.knowledge_base_documents.load_documents_for_base(data.path)
                else:
                    # Create or get the embeddings DB for the context
                    store = self.knowledge_manager.knowledge_base_documents._get_or_create_embeddings_db_for_context(data.context)
                    
                    # Load documents into the context
                    retriever = self.knowledge_manager.knowledge_base_documents._get_retriever_from_file(data.path)
                    for doc in retriever.docstore._dict.values():
                        store.add_embedding(doc.metadata.get("key"), doc)

                return JSONResponse({"status": "success", "context": data.context})

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/documents/{document_key}")
        @logger.catch(reraise=True)
        async def get_document(request: Request, document_key: str):
            """Get a specific document by its key"""
            try:
                document = self.knowledge_manager.knowledge_base_documents.get_document(document_key)
                
                if document is None:
                    raise HTTPException(
                        status_code=404, detail=f"Document not found: {document_key}"
                    )
                
                return JSONResponse({
                    "key": document.key,
                    "title": document.title,
                    "description": document.description,
                    "source": document.get_source_title_link(),
                })

            except HTTPException:
                raise
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                ) 