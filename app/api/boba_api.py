# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import FastAPI
from api.api_basics import ApiBasics
from api.api_multi_step import ApiMultiStep
from api.api_scenarios import ApiScenarios
from api.api_creative_matrix import ApiCreativeMatrix
from api.api_company_research import ApiCompanyResearch
from api.api_embeddings import ApiEmbeddings
from config_service import ConfigService
from disclaimer_and_guidelines import DisclaimerAndGuidelinesService
from knowledge_manager import KnowledgeManager
from llms.chats import ChatManager
from llms.image_description_service import ImageDescriptionService
from llms.model_config import ModelConfig
from prompts.prompts import PromptList
from prompts.inspirations import InspirationsManager
from api.api_documents import ApiDocuments


class BobaApi:
    def __init__(
        self,
        chat_manager: ChatManager,
        model_config: ModelConfig,
        prompts_guided: PromptList,
        knowledge_manager: KnowledgeManager,
        prompts_chat: PromptList,
        image_service: ImageDescriptionService,
        config_service: ConfigService,
        disclaimer_and_guidelines: DisclaimerAndGuidelinesService,
        inspirations_manager: InspirationsManager,
    ):
        self.chat_manager = chat_manager
        self.model_config = model_config
        self.prompts_guided = prompts_guided
        self.knowledge_manager = knowledge_manager
        self.prompts_chat = prompts_chat
        self.image_service = image_service
        self.config_service = config_service
        self.disclaimer_and_guidelines = disclaimer_and_guidelines
        self.inspirations_manager = inspirations_manager

    def add_endpoints(self, app: FastAPI):
        ApiBasics(
            app,
            self.chat_manager,
            self.model_config,
            self.prompts_guided,
            self.knowledge_manager,
            self.prompts_chat,
            self.image_service,
            self.config_service,
            self.disclaimer_and_guidelines,
            self.inspirations_manager,
        )
        ApiMultiStep(
            app,
            self.chat_manager,
            self.model_config,
            self.prompts_chat,
        )

        ApiScenarios(
            app,
            self.chat_manager,
            self.model_config,
            self.prompts_guided,
        )
        ApiCreativeMatrix(
            app,
            self.chat_manager,
            self.model_config,
            self.prompts_guided,
        )

        ApiCompanyResearch(
            app,
            self.chat_manager,
            self.model_config,
            self.prompts_guided,
        )

        ApiEmbeddings(
            app,
            self.config_service,
        )

        ApiDocuments(
            app,
            self.knowledge_manager,
        )
