# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import typer

from haiven_cli.app.app import App
from haiven_cli.services.config_service import ConfigService
from haiven_cli.services.cli_config_service import CliConfigService
from haiven_cli.services.embedding_service import EmbeddingService
from haiven_cli.services.file_service import FileService
from haiven_cli.services.knowledge_service import KnowledgeService
from haiven_cli.services.token_service import TokenService
from haiven_cli.services.metadata_service import MetadataService

ENCODING = "cl100k_base"

cli = typer.Typer(no_args_is_help=True)


"""
Parameters:
    source_path: The path to the source file to index (PDF or CSV file)
    embedding_model (optional): The name of the embedding model to use ("text-embedding-ada-002" by default). Model must be present under that name in the config
    config_path (optional): The path to the configuration file for custom settings.
    description (optional): A brief description of the knowledge base being generated, for the markdown file
    output_dir (optional): The directory where the generated knowledge base files will be saved ("new_knowledge_base" by default).
    pdf_source_link (optional): An optional link to the source PDF file, that you want used when a page is shown to the user as source in the application. 
        Default is "/kp-static/name-of-pdf-file.pdf", served from the "/static" folder of the knowledge pack.
"""


@cli.command(no_args_is_help=True)
def index_file(
    source_path: str,
    embedding_model="text-embedding-ada-002",
    config_path: str = "",
    description: str = "",
    output_dir: str = "new_knowledge_base",
    pdf_source_link: str = None,
):
    """Index single file to a given destination directory."""

    cli_config_service = CliConfigService()
    if cli_config_service.get_config_path() and config_path == "":
        config_path = cli_config_service.get_config_path()

    env_path_file = cli_config_service.get_env_path()

    config_service = ConfigService(env_file_path=env_path_file)

    app = create_app(config_service)
    app.index_individual_file(
        source_path,
        embedding_model,
        config_path,
        output_dir,
        description,
        pdf_source_link,
    )


@cli.command(no_args_is_help=True)
def index_all_files(
    source_dir: str,
    output_dir="new_knowledge_base",
    embedding_model="openai",
    description: str = "",
    config_path: str = "",
):
    """Index all files in a directory to a given destination directory."""
    cli_config_service = CliConfigService()
    if cli_config_service.get_config_path() and config_path == "":
        config_path = cli_config_service.get_config_path()

    env_path_file = cli_config_service.get_env_path()

    config_service = ConfigService(env_file_path=env_path_file)
    app = create_app(config_service)
    print("Indexing all files")
    app.index_all_files(
        source_dir, embedding_model, config_path, output_dir, description
    )


@cli.command(no_args_is_help=True)
def index_txt_files(
    source_dir: str,
    output_dir="new_knowledge_base",
    embedding_model="openai",
    description: str = "",
    config_path: str = "",
    authors: str = "Unknown",
):
    """Index all TXT files in a directory into one knowledge base in a given destination directory."""
    cli_config_service = CliConfigService()
    if cli_config_service.get_config_path() and config_path == "":
        config_path = cli_config_service.get_config_path()

    env_path_file = cli_config_service.get_env_path()

    config_service = ConfigService(env_file_path=env_path_file)
    app = create_app(config_service)
    print("Indexing all files in " + source_dir)

    app.index_txts_directory(
        source_dir, embedding_model, config_path, output_dir, description, authors
    )


@cli.command(no_args_is_help=True)
def init(
    config_path: str = "",
    env_path: str = "",
):
    """Initialize the config file with the given config and env paths."""
    config_service = CliConfigService()
    config_service.initialize_config(config_path=config_path, env_path=env_path)
    print(f"Config file initialized at {config_service.cli_config_path}")


@cli.command(no_args_is_help=True)
def set_config_path(
    config_path: str = "",
):
    """Set the config path in the config file."""
    config_service = CliConfigService()
    config_service.set_config_path(config_path)
    print(f"Config path set to {config_path}")


@cli.command(no_args_is_help=True)
def set_env_path(
    env_path: str = "",
):
    """Set the env path in the config file."""
    config_service = CliConfigService()
    config_service.set_env_path(env_path)
    print(f"Env path set to {env_path}")


def create_app(config_service: ConfigService):
    token_service = TokenService(ENCODING)
    knowledge_service = KnowledgeService(token_service, EmbeddingService)
    app = App(
        config_service,
        FileService(),
        knowledge_service,
        MetadataService,
    )
    return app


if __name__ == "__main__":
    cli()
