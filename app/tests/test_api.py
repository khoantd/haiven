# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
import unittest
from unittest.mock import MagicMock, patch, ANY
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_basics import ApiBasics
from api.api_multi_step import ApiMultiStep
from api.api_scenarios import ApiScenarios
from api.api_creative_matrix import ApiCreativeMatrix
from prompts.prompts_factory import PromptsFactory
from llms.model_config import ModelConfig
from tests.utils import get_test_data_path
from starlette.middleware.sessions import SessionMiddleware


class TestApi(unittest.TestCase):
    def check_token_usage_in_streamed_content(self, streamed_content):
        """Helper function to check for token usage in the new format"""
        import json

        # Try to find the usage JSON object in the streamed content
        usage_found = False

        # Look for the usage pattern in the content
        if '"usage"' in streamed_content:
            # Find the start of the usage object
            usage_start = streamed_content.find('{"usage"')
            if usage_start != -1:
                # Extract from the start of the usage object to the end
                usage_part = streamed_content[usage_start:]
                try:
                    data = json.loads(usage_part)
                    if "usage" in data:
                        usage_found = True
                        assert "prompt_tokens" in data["usage"]
                        assert "completion_tokens" in data["usage"]
                        assert "total_tokens" in data["usage"]
                except json.JSONDecodeError:
                    pass

        assert (
            usage_found
        ), f"Token usage not found in streamed content: {streamed_content}"

    def setUp(self):
        self.app = FastAPI()
        self.app.add_middleware(SessionMiddleware, secret_key="some-random-string")
        self.client = TestClient(self.app)

    def tearDown(self):
        # Clean up code to run after each test
        pass

    def test_get_prompts(self):
        mock_prompts = MagicMock()
        some_prompts = [{"identifier": "some-identifier", "title": "Some title"}]
        mock_prompts.get_prompts_with_follow_ups.return_value = some_prompts

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=mock_prompts,
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/prompts")
        expected_response = some_prompts

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

    def test_get_models(self):
        # Helper function to create MagicMock with id and name attributes
        def create_mock_model(id_value, name_value):
            mock_model = MagicMock()
            mock_model.id = id_value
            mock_model.name = name_value
            return mock_model

        # Mocking config_service methods to return specific MagicMock objects
        mock_config_service = MagicMock()
        mock_config_service.load_embedding_model.return_value = create_mock_model(
            "embed-model-id", "embed-model-name"
        )
        mock_config_service.get_image_model.return_value = create_mock_model(
            "image-model-id", "image-model-name"
        )
        mock_config_service.get_chat_model.return_value = create_mock_model(
            "chat-model-id", "chat-model-name"
        )

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=mock_config_service,
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/models")
        expected_response = {
            "chat": {
                "id": "chat-model-id",
                "name": "chat-model-name",
            },
            "vision": {
                "id": "image-model-id",
                "name": "image-model-name",
            },
            "embeddings": {
                "id": "embed-model-id",
                "name": "embed-model-name",
            },
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

    def test_get_documents(self):
        mock_knowledge_manager = MagicMock()

        mock_kb_documents = MagicMock()
        mock_doc_base = MagicMock(
            key="some-document-base",
            title="Some title base",
            description="Some description 1",
        )
        mock_doc_base.get_source_title_link.return_value = "some source title link"
        mock_doc_1 = MagicMock(
            key="some-document-1",
            title="Some title 1",
            description="Some description 2",
        )
        mock_doc_1.get_source_title_link.return_value = "some source title link"
        mock_doc_2 = MagicMock(
            key="some-document-2",
            title="Some title 2",
            description="Some description 3",
        )
        mock_doc_2.get_source_title_link.return_value = "some source title link"
        mock_kb_documents.get_documents.return_value = [
            mock_doc_base,
            mock_doc_1,
            mock_doc_2,
        ]
        mock_knowledge_manager.knowledge_base_documents = mock_kb_documents

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=mock_knowledge_manager,
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/knowledge/documents")

        # Assert the response
        assert response.status_code == 200

        assert mock_kb_documents.get_documents.call_count == 1

        response_data = json.loads(response.content)
        assert isinstance(response_data, list)
        assert len(response_data) == 3
        assert response_data[0]["key"] == mock_doc_base.key
        assert response_data[0]["title"] == mock_doc_base.title
        assert response_data[1]["key"] == mock_doc_1.key
        assert response_data[1]["title"] == mock_doc_1.title
        assert response_data[2]["key"] == mock_doc_2.key
        assert response_data[2]["title"] == mock_doc_2.title

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_prompting_text(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        mock_streaming_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", None
        mock_prompt_list.produces_json_output.return_value = False
        ApiBasics(
            self.app,
            chat_manager=mock_chat_manager,
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=mock_prompt_list,
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.post(
            "/api/prompt",
            json={
                "promptid": "some-prompt-id",
                "userinput": "some user input",
                "userContext": "some user defined context",
                "contexts": ["some context"],
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert "some response from the model" in streamed_content

        self.check_token_usage_in_streamed_content(streamed_content)
        mock_prompt_list.render_prompt.assert_called_with(
            prompt_choice="some-prompt-id",
            user_input="some user input",
        )

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_prompting_guided(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_json_chat,
    ):
        mock_json_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
        mock_chat_manager.json_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        mock_prompt_list.produces_json_output.return_value = True
        ApiBasics(
            self.app,
            chat_manager=mock_chat_manager,
            model_config=MagicMock(),
            prompts_guided=mock_prompt_list,
            knowledge_manager=MagicMock(),
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        # Make the request to the endpoint
        user_input = "some user input"
        response = self.client.post(
            "/api/prompt",
            json={
                "userinput": user_input,
                "contexts": ["some context"],
                "promptid": "guided-requirements",
                "userContext": "some user defined context",
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert "some response from the model" in streamed_content

        self.check_token_usage_in_streamed_content(streamed_content)
        mock_prompt_list.render_prompt.assert_called_with(
            prompt_choice="guided-requirements",
            user_input=user_input,
        )

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_scenarios(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_json_chat,
    ):
        mock_json_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
        mock_chat_manager.json_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiScenarios(self.app, mock_chat_manager, "some_model_key", mock_prompt_list)

        # Make the request to the endpoint
        input = "someinput"
        num_scenarios = "3"
        time_horizon = "5"
        optimism = "optimistic"
        realism = "futuristic sci-fi"
        response = self.client.get(
            f"/api/make-scenario?input={input}&num_scenarios={num_scenarios}&time_horizon={time_horizon}&optimism={optimism}&realism={realism}&detail=true"
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert "some response from the model" in streamed_content
        self.check_token_usage_in_streamed_content(streamed_content)
        mock_prompt_list.render_prompt.assert_called_with(
            prompt_choice="guided-scenarios-detailed",
            user_input=ANY,
            additional_vars={
                "input": input,
                "num_scenarios": num_scenarios,
                "time_horizon": time_horizon,
                "optimism": optimism,
                "realism": realism,
            },
        )

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_explore_with_static_framing(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        mock_streaming_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )

        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiMultiStep(self.app, mock_chat_manager, "some_model_key", mock_prompt_list)

        body_dict = {
            "userinput": "some user question",
            "item": "some scenario item",
            "first_step_input": "some original prompt",
            "chatSessionId": "",
            # # previous_promptid: str = None TODO, another test
            "previous_framing": "We did something before, here it is: ",
        }

        # Make the request to the endpoint
        response = self.client.post(
            "/api/prompt/explore",
            json=body_dict,
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert "some response from the model" in streamed_content
        self.check_token_usage_in_streamed_content(streamed_content)

        args, kwargs = mock_streaming_chat.run.call_args
        actual_composed_prompt = args[0]
        assert body_dict["userinput"] in actual_composed_prompt
        assert body_dict["previous_framing"] in actual_composed_prompt
        assert body_dict["first_step_input"] in actual_composed_prompt

        args, kwargs = mock_chat_manager.streaming_chat.call_args
        assert kwargs["options"].category == "explore"
        assert kwargs["session_id"] == ""

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_explore_with_previous_prompt(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        mock_streaming_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )

        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"

        ApiMultiStep(self.app, mock_chat_manager, "some_model_key", mock_prompt_list)

        body_dict = {
            "userinput": "some user question",
            "contexts": ["some context"],
            "item": "some scenario item",
            "first_step_input": "some original prompt",
            "chatSessionId": "",
            "previous_promptid": "some-previous-prompt-id",
        }

        # Make the request to the endpoint
        response = self.client.post(
            "/api/prompt/explore",
            json=body_dict,
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        # The response now includes both the model response and token usage data
        assert "some response from the model" in streamed_content
        self.check_token_usage_in_streamed_content(streamed_content)

        args, kwargs = mock_streaming_chat.run.call_args
        actual_composed_prompt = args[0]
        assert body_dict["userinput"] in actual_composed_prompt
        assert body_dict["first_step_input"] in actual_composed_prompt

        args, kwargs = mock_chat_manager.streaming_chat.call_args
        assert kwargs["options"].category == "explore"
        assert kwargs["session_id"] == ""

    @patch("llms.chats.ChatManager")
    @patch("llms.chats.StreamingChat")
    def test_post_multi_step(
        self,
        mock_streaming_chat,
        mock_chat_manager,
    ):
        mock_streaming_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
        mock_chat_manager.streaming_chat.return_value = (
            "some_session_key",
            mock_streaming_chat,
        )

        guided_prompts_path = (
            get_test_data_path() + "/test_knowledge_pack/prompts/guided"
        )
        prompts_factory_guided = PromptsFactory(guided_prompts_path)
        prompts_guided = prompts_factory_guided.create_guided_prompt_list(
            MagicMock(),  # knowledge_base_markdown
            MagicMock(),  # knowledge_manager,
        )

        ApiMultiStep(self.app, mock_chat_manager, "some_model_key", prompts_guided)

        # Make the request to the endpoint
        response = self.client.post(
            "/api/prompt/follow-up",
            json={
                # The usual
                "chat_session_id": None,
                "userinput": "some original requirement",
                "promptid": "follow-up-prompt-2345",
                "contexts": ["some-context"],
                # additional data for the follow-up
                "scenarios": [{"title": "some title", "content": "some content"}],
                "previous_promptid": "first-step-prompt-1234",
                "userContext": "some user context",
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert "some response from the model" in streamed_content
        self.check_token_usage_in_streamed_content(streamed_content)

        assert mock_streaming_chat.run.call_count == 1
        args, kwargs = mock_streaming_chat.run.call_args
        prompt_argument = args[0]
        assert "this is what I got from the first step" in prompt_argument
        assert "some title" in prompt_argument
        assert "some content" in prompt_argument
        assert "Follow up" in prompt_argument

        args, kwargs = mock_chat_manager.streaming_chat.call_args
        assert kwargs["session_id"] is None

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_creative_matrix(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_json_chat,
    ):
        mock_json_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
        mock_chat_manager.json_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiCreativeMatrix(
            self.app, mock_chat_manager, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        rows = "For A, For B"
        columns = "For C, For D"
        prompt = "give me use cases for the future of gardening"
        idea_qualifiers = "utopian"
        num_ideas = "3"
        response = self.client.get(
            f"/api/creative-matrix?rows={rows}&columns={columns}&prompt={prompt}&idea_qualifiers={idea_qualifiers}&num_ideas={num_ideas}"
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        # The response now includes both the model response and token usage data
        assert "some response from the model" in streamed_content
        self.check_token_usage_in_streamed_content(streamed_content)
        mock_prompt_list.render_prompt.assert_called_with(
            prompt_choice="guided-creative-matrix",
            user_input=ANY,
            additional_vars={
                "rows": rows,
                "columns": columns,
                "prompt": prompt,
                "idea_qualifiers": idea_qualifiers,
                "num_ideas": num_ideas,
            },
        )

    def test_get_inspirations(self):
        mock_inspirations = [{"title": "Test Title"}]
        mock_inspirations_manager = MagicMock()
        mock_inspirations_manager.get_inspirations.return_value = mock_inspirations

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=mock_inspirations_manager,
        )

        response = self.client.get("/api/inspirations")

        # Assert the response
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert isinstance(response_data, list)
        assert len(response_data) > 0

        # Verify the title field of the first inspiration item
        first_item = response_data[0]
        assert "title" in first_item

        # Verify the mock was called
        mock_inspirations_manager.get_inspirations.assert_called_once()

    def test_get_inspiration_by_id(self):
        mock_inspiration = {
            "id": "test-id",
            "title": "Test Title",
            "description": "Test Description",
            "category": "test",
            "prompt_template": "Test template",
        }
        mock_inspirations_manager = MagicMock()
        mock_inspirations_manager.get_inspiration_by_id.return_value = mock_inspiration

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=mock_inspirations_manager,
        )

        response = self.client.get("/api/inspirations/test-id")

        # Assert the response
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data == mock_inspiration
        mock_inspirations_manager.get_inspiration_by_id.assert_called_once_with(
            "test-id"
        )

    def test_get_inspiration_by_id_not_found(self):
        mock_inspirations_manager = MagicMock()
        mock_inspirations_manager.get_inspiration_by_id.return_value = None

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=mock_inspirations_manager,
        )

        response = self.client.get("/api/inspirations/non-existent")

        # Assert the response
        assert response.status_code == 404
        mock_inspirations_manager.get_inspiration_by_id.assert_called_once_with(
            "non-existent"
        )

    def test_get_prompt_with_follow_ups_should_return_prompt_for_the_given_id(self):
        mock_prompts_chat = MagicMock()

        mock_prompt = MagicMock()
        mock_prompt.content = "Content {user_input} {context}"
        mock_prompt.metadata = {
            "title": "Test Prompt",
            "identifier": "test-prompt-id",
            "categories": ["test"],
            "type": "chat",
            "editable": False,
            "show": True,
            "help_prompt_description": "Test description",
            "help_user_input": "Test user input help",
            "help_sample_input": "Test sample input",
        }

        mock_prompts_chat.get_a_prompt_with_follow_ups.return_value = {
            "content": "PromptContent {user_input}",
            "title": "Test Prompt",
            "identifier": "test-prompt-id",
            "categories": ["test"],
            "type": "chat",
            "editable": False,
            "show": True,
            "help_prompt_description": "Test description",
            "help_user_input": "Test user input help",
            "help_sample_input": "Test sample input",
            "follow_ups": [],
        }

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=mock_prompts_chat,
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt?prompt_id=test-prompt-id")

        assert response.status_code == 200
        mock_prompts_chat.get_a_prompt_with_follow_ups.assert_called_with(
            "test-prompt-id", download_prompt=True
        )

        response_data = json.loads(response.content)[0]
        assert response_data["content"] == "PromptContent {user_input}"
        assert response_data["title"] == "Test Prompt"
        assert response_data["identifier"] == "test-prompt-id"
        assert response_data["categories"] == ["test"]
        assert response_data["type"] == "chat"
        assert response_data["editable"] is False
        assert response_data["show"] is True
        assert response_data["help_prompt_description"] == "Test description"
        assert response_data["help_user_input"] == "Test user input help"
        assert response_data["help_sample_input"] == "Test sample input"
        assert len(response_data["follow_ups"]) == 0

    def test_get_prompt_with_follow_ups_should_throw_exception_if_prompt_not_found(
        self,
    ):
        mock_prompts_chat = MagicMock()
        mock_prompts_chat.get_a_prompt_with_follow_ups.return_value = None

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=mock_prompts_chat,
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt?prompt_id=non-existent-id")

        # Assert the response
        assert response.status_code == 500
        assert b"Prompt not found" in response.content
        assert mock_prompts_chat.get_a_prompt_with_follow_ups.call_count == 1
        mock_prompts_chat.get_a_prompt_with_follow_ups.assert_called_with(
            "non-existent-id", download_prompt=True
        )

    def test_get_prompts_with_category(self):
        mock_prompts = MagicMock()
        category_prompts = [
            {
                "identifier": "prompt-1",
                "title": "Prompt 1",
                "categories": ["architecture"],
                "content": "Content 1",
            },
            {
                "identifier": "prompt-2",
                "title": "Prompt 2",
                "categories": ["architecture"],
                "content": "Content 2",
            },
        ]

        mock_prompts.get_prompts_with_follow_ups.return_value = category_prompts

        # Mock the HaivenLogger
        with patch("api.api_basics.HaivenLogger") as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.get.return_value = mock_logger_instance

            ApiBasics(
                self.app,
                chat_manager=MagicMock(),
                model_config=MagicMock(),
                image_service=MagicMock(),
                prompts_chat=mock_prompts,
                prompts_guided=MagicMock(),
                knowledge_manager=MagicMock(),
                config_service=MagicMock(),
                disclaimer_and_guidelines=MagicMock(),
                inspirations_manager=MagicMock(),
            )

            # Test the endpoint with category parameter
            response = self.client.get("/api/download-prompt?category=architecture")

            # Assert response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), category_prompts)

            # Verify the method was called with the right parameters
            mock_prompts.get_prompts_with_follow_ups.assert_called_with(
                download_prompt=True, category="architecture"
            )

            # Check that analytics was logged for each prompt
            calls = mock_logger_instance.analytics.call_args_list
            self.assertEqual(len(calls), 2)

            for i, call in enumerate(calls):
                args, kwargs = call
                self.assertEqual(args[0], "Download prompt")
                self.assertEqual(
                    args[1]["prompt_id"], category_prompts[i]["identifier"]
                )
                self.assertEqual(args[1]["category"], "architecture")

    def test_get_all_prompts(self):
        mock_prompts = MagicMock()
        all_prompts = [
            {
                "identifier": "prompt-1",
                "title": "Prompt 1",
                "categories": ["architecture"],
                "content": "Content 1",
            },
            {
                "identifier": "prompt-2",
                "title": "Prompt 2",
                "categories": ["coding"],
                "content": "Content 2",
            },
        ]

        mock_prompts.get_prompts_with_follow_ups.return_value = all_prompts

        # Mock the HaivenLogger
        with patch("api.api_basics.HaivenLogger") as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.get.return_value = mock_logger_instance

            ApiBasics(
                self.app,
                chat_manager=MagicMock(),
                model_config=MagicMock(),
                image_service=MagicMock(),
                prompts_chat=mock_prompts,
                prompts_guided=MagicMock(),
                knowledge_manager=MagicMock(),
                config_service=MagicMock(),
                disclaimer_and_guidelines=MagicMock(),
                inspirations_manager=MagicMock(),
            )

            # Test the endpoint with category parameter
            response = self.client.get("/api/download-prompt")

            # Assert response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), all_prompts)

            # Verify the method was called with the right parameters
            mock_prompts.get_prompts_with_follow_ups.assert_called_with(
                download_prompt=True,
            )

            # Check that analytics was logged for each prompt
            calls = mock_logger_instance.analytics.call_args_list
            self.assertEqual(len(calls), 2)

            for i, call in enumerate(calls):
                args, kwargs = call
                self.assertEqual(args[0], "Download prompt")
                self.assertEqual(args[1]["prompt_id"], all_prompts[i]["identifier"])
                self.assertEqual(args[1]["category"], "all")

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_perplexity_used_for_grounded_prompts(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        # Setup mocks
        mock_streaming_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", None
        mock_prompt_list.produces_json_output.return_value = False

        # Create a mock prompt with grounded=True
        mock_prompt = MagicMock()
        mock_prompt.metadata = {"grounded": True}
        mock_prompt_list.get.return_value = mock_prompt

        # Setup the API with a default model config that we can recognize
        default_model_config = MagicMock()
        default_model_config.provider = "default-provider"

        perplexity_model_config = MagicMock()
        perplexity_model_config.provider = "perplexity"

        # Create the API with our mocks
        ApiBasics(
            self.app,
            chat_manager=mock_chat_manager,
            model_config=default_model_config,
            image_service=MagicMock(),
            prompts_chat=mock_prompt_list,
            prompts_guided=mock_prompt_list,
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        # Make the request
        response = self.client.post(
            "/api/prompt",
            json={
                "userinput": "some user input",
                "promptid": "grounded-prompt-id",
            },
        )

        # Assert the response
        self.assertEqual(response.status_code, 200)
        streamed_content = response.content.decode("utf-8")
        self.assertIn("some response from the model", streamed_content)
        self.check_token_usage_in_streamed_content(streamed_content)

        expected_model_config = ModelConfig("perplexity", "perplexity", "Perplexity")

        # Verify that streaming_chat was called with the Perplexity model config
        # and not the default config
        mock_chat_manager.streaming_chat.assert_called_once()
        actual_model_config = mock_chat_manager.streaming_chat.call_args[1][
            "model_config"
        ]
        self.assertEqual(actual_model_config.provider, expected_model_config.provider)

    def test_download_restricted_prompt_returns_403(self):
        """Test that downloading a restricted prompt returns 403 Forbidden"""
        # Mock the prompt with download_restricted=True
        mock_prompt = {
            "identifier": "restricted-prompt",
            "title": "Restricted Prompt",
            "download_restricted": True,
            "content": "Restricted content",
        }

        # Create mock prompts_chat
        mock_prompts_chat = MagicMock()
        mock_prompts_chat.get_a_prompt_with_follow_ups.return_value = mock_prompt

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=mock_prompts_chat,
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt?prompt_id=restricted-prompt")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"], "This prompt is not available for download"
        )

    def test_download_restricted_prompts_filtered_from_category(self):
        """Test that restricted prompts are filtered out when downloading by category"""
        # Mock prompts with some restricted
        mock_prompts = [
            {
                "identifier": "prompt-1",
                "download_restricted": False,
                "title": "Downloadable Prompt 1",
            },
            {
                "identifier": "prompt-2",
                "download_restricted": True,
                "title": "Restricted Prompt",
            },
            {
                "identifier": "prompt-3",
                "download_restricted": False,
                "title": "Downloadable Prompt 2",
            },
        ]

        # Create mock prompts_chat
        mock_prompts_chat = MagicMock()
        mock_prompts_chat.get_prompts_with_follow_ups.return_value = mock_prompts

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=mock_prompts_chat,
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt?category=test-category")

        self.assertEqual(response.status_code, 200)
        result = response.json()

        # Should only return non-restricted prompts
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["identifier"], "prompt-1")
        self.assertEqual(result[1]["identifier"], "prompt-3")

    def test_download_restricted_prompts_filtered_from_all_prompts(self):
        """Test that restricted prompts are filtered out when downloading all prompts"""
        # Mock prompts with some restricted
        mock_prompts = [
            {
                "identifier": "prompt-1",
                "download_restricted": False,
                "title": "Downloadable Prompt 1",
            },
            {
                "identifier": "prompt-2",
                "download_restricted": True,
                "title": "Restricted Prompt",
            },
            {
                "identifier": "prompt-3",
                "download_restricted": False,
                "title": "Downloadable Prompt 2",
            },
        ]

        # Create mock prompts_chat
        mock_prompts_chat = MagicMock()
        mock_prompts_chat.get_prompts_with_follow_ups.return_value = mock_prompts

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=mock_prompts_chat,
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt")

        self.assertEqual(response.status_code, 200)
        result = response.json()

        # Should only return non-restricted prompts
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["identifier"], "prompt-1")
        self.assertEqual(result[1]["identifier"], "prompt-3")

    def test_download_all_prompts_with_empty_category(self):
        """Test that empty category parameter correctly triggers 'download all prompts' logic"""
        # Mock prompts with some restricted
        mock_prompts = [
            {
                "identifier": "prompt-1",
                "download_restricted": False,
                "title": "Downloadable Prompt 1",
            },
            {
                "identifier": "prompt-2",
                "download_restricted": True,
                "title": "Restricted Prompt",
            },
            {
                "identifier": "prompt-3",
                "download_restricted": False,
                "title": "Downloadable Prompt 2",
            },
        ]

        # Create mock prompts_chat
        mock_prompts_chat = MagicMock()
        mock_prompts_chat.get_prompts_with_follow_ups.return_value = mock_prompts

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=mock_prompts_chat,
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt?category=")

        self.assertEqual(response.status_code, 200)
        result = response.json()

        # Should only return non-restricted prompts
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["identifier"], "prompt-1")
        self.assertEqual(result[1]["identifier"], "prompt-3")
