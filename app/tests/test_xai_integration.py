import pytest
from unittest.mock import MagicMock
from llms.clients import ChatClient, HaivenSystemMessage, HaivenHumanMessage
from llms.model_config import ModelConfig

@pytest.fixture
def xai_config():
    return ModelConfig(
        id="xai-grok-2",
        name="Grok-2 on xAI",
        provider="XAI",
        features=["text-generation", "image-to-text", "stop-sequence"],
        config={
            "model": "grok-2-latest",
            "api_key": "test-key"
        }
    )

@pytest.fixture
def mock_litellm(mocker):
    return mocker.patch("llms.clients.llmCompletion")

def test_xai_chat_completion(xai_config, mock_litellm):
    # Arrange
    client = ChatClient(xai_config)
    # Create a mock that yields the expected response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(delta=MagicMock(content="Test response"))]
    mock_litellm.return_value = iter([mock_response])
    
    messages = [
        HaivenSystemMessage(content="You are a helpful assistant"),
        HaivenHumanMessage(content="Hello")
    ]

    # Act
    response_chunks = list(client.stream(messages))

    # Assert
    mock_litellm.assert_called_once()
    assert any("Test response" in chunk.get('content', '') for chunk in response_chunks)
    
    # Verify correct provider and model were used
    call_args = mock_litellm.call_args[1]
    assert call_args["model"] == "xai/grok-2-latest"
    assert call_args["api_key"] == "test-key"

def test_xai_vision_completion(xai_config, mock_litellm):
    # Arrange
    client = ChatClient(xai_config)
    # Create a mock that yields the expected response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(delta=MagicMock(content="Image description"))]
    mock_litellm.return_value = iter([mock_response])
    
    messages = [
        HaivenHumanMessage(content=[
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://example.com/image.jpg",
                    "detail": "high"
                }
            },
            {
                "type": "text",
                "text": "What's in this image?"
            }
        ])
    ]

    # Act
    response_chunks = list(client.stream(messages))

    # Assert
    mock_litellm.assert_called_once()
    assert any("Image description" in chunk.get('content', '') for chunk in response_chunks)
    
    # Verify correct provider and model were used
    call_args = mock_litellm.call_args[1]
    assert call_args["model"] == "xai/grok-2-latest"
    assert call_args["api_key"] == "test-key"
