# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from langchain.text_splitter import RecursiveCharacterTextSplitter
from haiven_cli.services.embedding_service import EmbeddingService
from haiven_cli.services.token_service import TokenService
from haiven_cli.services.vector_store_service import VectorStoreService, FAISSVectorStore, QdrantVectorStore


class KnowledgeService:
    def __init__(
        self, 
        token_service: TokenService, 
        embedding_service: EmbeddingService,
        vector_store_service: VectorStoreService = None
    ):
        self.token_service = token_service
        self.embedding_service = embedding_service
        self.vector_store_service = vector_store_service or FAISSVectorStore()

    def index(self, texts, metadatas, embedding_model, output_dir):
        if texts is None or len(texts) == 0:
            raise ValueError("file content has no value")

        if embedding_model is None:
            raise ValueError("embedding model has no value")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            length_function=self.token_service.get_tokens_length,
            separators=["\n\n", "\n", " ", ""],
        )

        print("Creating documents out of", len(texts), "texts...")
        documents = text_splitter.create_documents(texts, metadatas)
        print("Loading embeddings model", embedding_model.name, "...")
        embeddings = self.embedding_service.load_embeddings(embedding_model)

        print("Creating DB...")
        db = self.vector_store_service.create_store(documents, embeddings)
        try:
            local_db = self.vector_store_service.load_store(output_dir, embeddings)
            local_db = self.vector_store_service.merge_stores(local_db, db)
        except ValueError:
            print("Indexing to new path")
            local_db = db

        print("Saving DB to", output_dir)
        self.vector_store_service.save_store(local_db, output_dir)
