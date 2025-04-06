# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from knowledge_manager import KnowledgeManager
from api.api_basics import HaivenBaseApi
from fastapi import FastAPI
from llms.chats import ChatManager
from llms.model_config import ModelConfig
from config_service import ConfigService
from .strategy import router as strategy_router

class ApiBusinessStrategy(HaivenBaseApi):
    def __init__(self, app, chat_session_memory, model_key, prompt_list, config_service: ConfigService):
        super().__init__(app, chat_session_memory, model_key, prompt_list)
        self.config_service = config_service
        # Include the strategy router
        app.include_router(strategy_router, prefix="/api", tags=["strategy"]) 