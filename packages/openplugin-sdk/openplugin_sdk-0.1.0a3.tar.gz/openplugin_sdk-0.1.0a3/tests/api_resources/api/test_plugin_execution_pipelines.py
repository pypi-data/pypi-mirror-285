# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openplugin import Openplugin, AsyncOpenplugin
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPluginExecutionPipelines:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Openplugin) -> None:
        plugin_execution_pipeline = client.api.plugin_execution_pipelines.create(
            conversation=[{}, {}, {}],
            header={},
            prompt="prompt",
        )
        assert_matches_type(object, plugin_execution_pipeline, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Openplugin) -> None:
        plugin_execution_pipeline = client.api.plugin_execution_pipelines.create(
            conversation=[{}, {}, {}],
            header={},
            prompt="prompt",
            auth_query_param={},
            config={
                "provider": "provider",
                "openai_api_key": "openai_api_key",
                "cohere_api_key": "cohere_api_key",
                "mistral_api_key": "mistral_api_key",
                "fireworks_api_key": "fireworks_api_key",
                "google_palm_key": "google_palm_key",
                "gemini_api_key": "gemini_api_key",
                "anthropic_api_key": "anthropic_api_key",
                "together_api_key": "together_api_key",
                "aws_access_key_id": "aws_access_key_id",
                "aws_secret_access_key": "aws_secret_access_key",
                "aws_region_name": "aws_region_name",
                "azure_api_key": "azure_api_key",
                "groq_api_key": "groq_api_key",
            },
            enable_ui_form_controls=True,
            function_provider_input={"name": "name"},
            openplugin_manifest_obj={},
            openplugin_manifest_url="openplugin_manifest_url",
            output_module_names=["string", "string", "string"],
            run_all_output_modules=True,
            selected_operation="selected_operation",
            session_variables="session_variables",
        )
        assert_matches_type(object, plugin_execution_pipeline, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Openplugin) -> None:
        response = client.api.plugin_execution_pipelines.with_raw_response.create(
            conversation=[{}, {}, {}],
            header={},
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plugin_execution_pipeline = response.parse()
        assert_matches_type(object, plugin_execution_pipeline, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Openplugin) -> None:
        with client.api.plugin_execution_pipelines.with_streaming_response.create(
            conversation=[{}, {}, {}],
            header={},
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plugin_execution_pipeline = response.parse()
            assert_matches_type(object, plugin_execution_pipeline, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPluginExecutionPipelines:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenplugin) -> None:
        plugin_execution_pipeline = await async_client.api.plugin_execution_pipelines.create(
            conversation=[{}, {}, {}],
            header={},
            prompt="prompt",
        )
        assert_matches_type(object, plugin_execution_pipeline, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenplugin) -> None:
        plugin_execution_pipeline = await async_client.api.plugin_execution_pipelines.create(
            conversation=[{}, {}, {}],
            header={},
            prompt="prompt",
            auth_query_param={},
            config={
                "provider": "provider",
                "openai_api_key": "openai_api_key",
                "cohere_api_key": "cohere_api_key",
                "mistral_api_key": "mistral_api_key",
                "fireworks_api_key": "fireworks_api_key",
                "google_palm_key": "google_palm_key",
                "gemini_api_key": "gemini_api_key",
                "anthropic_api_key": "anthropic_api_key",
                "together_api_key": "together_api_key",
                "aws_access_key_id": "aws_access_key_id",
                "aws_secret_access_key": "aws_secret_access_key",
                "aws_region_name": "aws_region_name",
                "azure_api_key": "azure_api_key",
                "groq_api_key": "groq_api_key",
            },
            enable_ui_form_controls=True,
            function_provider_input={"name": "name"},
            openplugin_manifest_obj={},
            openplugin_manifest_url="openplugin_manifest_url",
            output_module_names=["string", "string", "string"],
            run_all_output_modules=True,
            selected_operation="selected_operation",
            session_variables="session_variables",
        )
        assert_matches_type(object, plugin_execution_pipeline, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenplugin) -> None:
        response = await async_client.api.plugin_execution_pipelines.with_raw_response.create(
            conversation=[{}, {}, {}],
            header={},
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plugin_execution_pipeline = await response.parse()
        assert_matches_type(object, plugin_execution_pipeline, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenplugin) -> None:
        async with async_client.api.plugin_execution_pipelines.with_streaming_response.create(
            conversation=[{}, {}, {}],
            header={},
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plugin_execution_pipeline = await response.parse()
            assert_matches_type(object, plugin_execution_pipeline, path=["response"])

        assert cast(Any, response.is_closed) is True
