import pytest
from unittest.mock import MagicMock
from llms.clients import ChatClient
from llms.model_config import ModelConfig

@pytest.fixture
def cohere_config():
    return ModelConfig(
        id="cohere-command",
        name="Command on Cohere",
        provider="Cohere",
        features=["text-generation"],
        config={
            "model": "command",
            "api_key": "test-key"
        }
    )

@pytest.fixture
def mock_litellm(mocker):
    return mocker.patch("llms.clients.llmCompletion")

def test_cohere_chat_completion(cohere_config, mock_litellm):
    # Arrange
    client = ChatClient(cohere_config)
    mock_litellm.return_value = MagicMock(choices=[
        MagicMock(message=MagicMock(content="Test response"))
    ])
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"}
    ]

    # Act
    response = client.completion(messages)

    # Assert
    mock_litellm.assert_called_once()
    assert "Test response" in response
    
    # Verify correct provider and model were used
    call_args = mock_litellm.call_args[1]
    assert call_args["model"] == "command"
    assert call_args["api_key"] == "test-key"
