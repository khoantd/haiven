# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from llms.clients import ChatClientFactory, HaivenHumanMessage, HaivenSystemMessage
from config_service import ConfigService

class LLMService:
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self.chat_client_factory = ChatClientFactory(config_service)
        self.model_config = config_service.get_chat_model()
        self.chat_client = self.chat_client_factory.new_chat_client(self.model_config)

    async def generate_response(self, prompt: str):
        """
        Generate a response from the LLM using the provided prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The generated response as a string
        """
        system_message = HaivenSystemMessage(content="You are a helpful AI assistant that provides detailed, accurate, and well-structured responses.")
        human_message = HaivenHumanMessage(content=prompt)
        
        response = ""
        for chunk in self.chat_client.stream([system_message, human_message]):
            if "content" in chunk:
                response += chunk["content"]
        
        return response 