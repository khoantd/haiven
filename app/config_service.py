# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import copy
import os
from typing import List

import yaml
from dotenv import load_dotenv
from knowledge.pack import KnowledgePackError
from llms.model_config import ModelConfig
from llms.default_models import DefaultModels
from embeddings.model import EmbeddingModel
import re


class ConfigService:
    def __init__(self, path: str = "config.yaml"):
        self.data = self._load_yaml(path)
        # Resolve config values for embeddings_db
        embeddings_db = self.data.get("embeddings_db", {})
        print("Initial embeddings_db:", embeddings_db)
        if "type" in embeddings_db:
            embeddings_db["type"] = self._replace_by_env_var(embeddings_db["type"])
            print("Resolved embeddings_db type:", embeddings_db["type"])
        self._resolve_config_values(embeddings_db.get("config", {}))

    def load_embedding_model(self) -> EmbeddingModel:
        """
        Load an embedding model from a YAML config file.

        Args:
            path (str): The path to the YAML file.

        Returns:
            EmbeddingModel: The loaded embedding model for the given provider
        """

        default_embedding = self.load_default_models().embeddings

        embeddings_data_list = self.data["embeddings"]
        embedding_model_data = next(
            (item for item in embeddings_data_list if item["id"] == default_embedding),
            None,
        )

        if embedding_model_data is None:
            raise ValueError(f"Embeddings provider {default_embedding} not supported")

        embedding_model = EmbeddingModel.from_dict(embedding_model_data)
        return embedding_model

    def load_enabled_models(self, features: List[str] = []) -> List[ModelConfig]:
        """
        Load a list of models for the enabled providers from a YAML config file.

        Args:
            path (str): The path to the YAML file.
            features (List[str]): A list of features to filter the models by.

        Returns:
            List[ModelConfig]: The loaded models.
        """
        print("Loading enabled models with features:", features)
        model_data_list = self.data["models"]
        print("All models in config:", model_data_list)
        models = []

        for model_data in model_data_list:
            model = ModelConfig.from_dict(model_data)
            models.append(model)

        filtered_models = copy.deepcopy(models)
        providers = self.load_enabled_providers()
        print("Enabled providers:", providers)

        # Only filter by providers if there are enabled providers
        if providers and len(providers) > 0:
            filtered_models = [
                model
                for model in filtered_models
                if any(
                    model.provider.lower() == model_provider.lower()
                    for model_provider in providers
                )
            ]
            print("Models after provider filtering:", [model.id for model in filtered_models])

        # Filter by features if specified
        if features and len(features) > 0:
            filtered_models = [
                model
                for model in filtered_models
                if all(
                    feature.lower()
                    in [model_feature.lower() for model_feature in model.features]
                    for feature in features
                )
            ]
            print("Models after feature filtering:", [model.id for model in filtered_models])

        return filtered_models

    def get_model(self, model_id: str) -> ModelConfig:
        """
        Get a model by its ID.

        Args:
            model_id (str): The model ID.

        Returns:
            ModelConfig: The model.
        """
        print("Loading model with ID:", model_id)
        print("Available models in config:", self.data["models"])
        
        # First try to find the model in all available models
        all_models = [ModelConfig.from_dict(model_data) for model_data in self.data["models"]]
        model = next((model for model in all_models if model.id == model_id), None)
        
        if model is not None:
            print(f"Found model {model_id} in all available models")
            return model
            
        # If not found, try in enabled models
        print("Model not found in all models, checking enabled models...")
        models = self.load_enabled_models()
        print("Enabled models:", [model.id for model in models])
        model = next((model for model in models if model.id == model_id), None)
        
        if model is None:
            raise ValueError(f"Model with ID {model_id} not found in available or enabled models")

        return model

    def get_image_model(self) -> ModelConfig:
        available_vision_models = [
            (available_model.name, available_model.id)
            for available_model in self.load_enabled_models(
                features=["image-to-text"],
            )
        ]

        image_model_id = (
            self.load_default_models().vision or available_vision_models[0][1]
            if len(available_vision_models) > 0
            else None
        )

        return self.get_model(image_model_id)

    def get_chat_model(self) -> ModelConfig:
        available_chat_models = [
            (available_model.name, available_model.id)
            for available_model in self.load_enabled_models(
                features=["text-generation"],
            )
        ]

        chat_model_id = (
            self.load_default_models().chat or self.get_default_chat_model()
            if len(available_chat_models) > 0
            else None
        )

        return self.get_model(chat_model_id)

    def load_knowledge_pack_path(self) -> str:
        """
        Load the knowledge pack path from a YAML config file.

        Args:
            config_file_path (str): The path to the YAML file.

        Returns:
            str: The knowledge pack path.
        """
        knowledge_pack_path = self.data["knowledge_pack_path"]

        if not os.path.exists(knowledge_pack_path):
            raise KnowledgePackError(
                f"Cannot find path to Knowledge Pack: `{knowledge_pack_path}`. Please check the `knowledge_pack_path` in your config file."
            )

        return knowledge_pack_path

    def load_enabled_providers(self) -> List[str]:
        """
        Load the enabled providers from the specified YAML configuration file.

        Args:
            path (str, optional): The path to the YAML configuration file. Defaults to "config.yaml".

        Returns:
            List[str]: The list of enabled providers.
        """
        enabled_providers = self.data["enabled_providers"]
        print("Raw enabled providers:", enabled_providers)

        if isinstance(enabled_providers, str):
            # Handle environment variable format ${VAR_NAME}
            if enabled_providers.startswith("${") and enabled_providers.endswith("}"):
                env_var = enabled_providers[2:-1]
                enabled_providers = os.getenv(env_var, "")
                print("Resolved from env var:", env_var, "=", enabled_providers)
            
            # Split into list
            enabled_providers = [p.strip() for p in enabled_providers.split(",") if p.strip()]
            print("Final enabled providers:", enabled_providers)

        return enabled_providers

    def load_default_models(self) -> DefaultModels:
        """
        Load the default models from a YAML file.

        Args:
            path (str): The path to the YAML file. Defaults to "config.yaml".

        Returns:
            DefaultModels: An instance of the DefaultModels config class containing the default model set for llm, vision and embeddings.

        """
        default_models = DefaultModels.from_dict(self.data["default_models"])

        return default_models

    def get_embeddings_db_config(self) -> dict:
        """
        Get the embeddings database configuration.
        
        Returns:
            dict: Configuration for the embeddings database with type and config parameters
        """
        db_config = self.data.get("embeddings_db", {})
        config = {
            "type": db_config.get("type", "in_memory"),
        }
        
        # If there's additional configuration, add it to the kwargs
        if "config" in db_config:
            config.update(db_config["config"])
            
        return config
        
    def get_default_chat_model(self) -> str:
        """
        Get the default chat model from the config file.

        Args:
            path (str): The path to the YAML file.

        Returns:
            str: The default chat model.
        """
        default_chat_model = self.load_default_models().chat
        if default_chat_model is None or default_chat_model == "":
            enabled_provider = self.load_enabled_providers()[0]
            match enabled_provider:
                case "azure":
                    default_chat_model = "azure-gpt-4o"
                case "openai":
                    default_chat_model = "openai-gpt-4o"
                case "perplexity":
                    default_chat_model = "perplexity-sonar-pro"
                case "gcp":
                    default_chat_model = "google-gemini"
                case "aws":
                    default_chat_model = "aws-claude-v3"
                case "anthropic":
                    default_chat_model = "anthropic-claude-3.7"
                case "ollama":
                    default_chat_model = "ollama-local-llama3"
        return default_chat_model

    def _load_yaml(self, path: str) -> dict:
        """
        Load YAML data from a config file.

        Args:
            path (str): The path to the YAML file.

        Returns:
            dict: The loaded YAML data.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path {path} is not valid")

        data = None

        yaml.SafeLoader.add_constructor(
            "tag:yaml.org,2002:timestamp", ConfigService._string_constructor
        )

        with open(path, "r") as file:
            try:
                data = yaml.load(file, Loader=yaml.SafeLoader)
            except yaml.YAMLError as exc:
                print(exc)

        return self._resolve_config_values(data)

    @staticmethod
    def _string_constructor(loader, node):
        """
        Custom constructor for handling YAML strings.

        Args:
            loader: The YAML loader.
            node: The YAML node.

        Returns:
            str: The constructed string.
        """
        return loader.construct_scalar(node)

    def _resolve_config_values(self, config: dict[str, str]):
        load_dotenv()
        for key, value in config.items():
            if isinstance(value, dict):
                self._resolve_config_values(value)
            elif isinstance(value, list):
                self._resolve_config_list_values(config, key, value)
            else:
                config[key] = self._replace_by_env_var(config[key])
                if self._is_comma_separated_list(config[key]):
                    config[key] = config[key].split(",")

        return config

    def _is_comma_separated_list(self, value: str) -> bool:
        return isinstance(value, str) and "," in value

    def _resolve_config_list_values(self, config, key, value):
        list = []
        for i, item in enumerate(value):
            if isinstance(item, dict):
                list.append(self._resolve_config_values(item))
            else:
                list.append(self._replace_by_env_var(item))

        config[key] = list

    def _replace_by_env_var(self, value):
        if value is None:
            return value

        print("Replacing env vars in:", value)
        # Use regex to find all ${ENV_VAR:-default} patterns and replace them with their values
        def replace_env_var(match):
            env_variable = match.group(1)
            default_value = ""
            if ":-" in env_variable:
                env_variable, default_value = env_variable.split(":-", 1)
            env_value = os.environ.get(env_variable, default_value)
            print(f"Env var {env_variable} = {env_value} (default: {default_value})")
            return env_value

        # Replace all occurrences of ${ENV_VAR} or ${ENV_VAR:-default} with their values
        return re.sub(r"\${([^}]+)}", replace_env_var, value)
