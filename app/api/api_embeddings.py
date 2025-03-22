 # © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger

from api.models import EmbeddingsRequest
from config_service import ConfigService
from embeddings.client import EmbeddingsClient
from logger import HaivenLogger


class ApiEmbeddings:
    def __init__(self, app: FastAPI, config_service: ConfigService):
        self.config_service = config_service

        @app.post("/api/embeddings")
        @logger.catch(reraise=True)
        async def create_embeddings(request: Request, data: EmbeddingsRequest):
            try:
                # Get the configured embedding model
                embedding_model = config_service.load_embedding_model()
                embeddings_client = EmbeddingsClient(embedding_model)

                # Generate embeddings with metadata
                embeddings = embeddings_client.generate_from_documents(
                    text=data.text,
                    metadata=[data.metadata] if data.metadata else [{}]
                )

                # If output path is provided, save the embeddings
                if data.output_path:
                    embeddings.save_local(data.output_path)
                    return JSONResponse({"status": "success", "path": data.output_path})
                
                # If no output path, return success without path
                return JSONResponse({"status": "success"})

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )