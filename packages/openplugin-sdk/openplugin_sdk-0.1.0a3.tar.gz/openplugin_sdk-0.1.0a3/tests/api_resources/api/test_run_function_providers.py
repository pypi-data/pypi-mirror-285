# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openplugin import Openplugin, AsyncOpenplugin
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRunFunctionProviders:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Openplugin) -> None:
        run_function_provider = client.api.run_function_providers.create(
            config={},
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
            prompt="prompt",
        )
        assert_matches_type(object, run_function_provider, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Openplugin) -> None:
        run_function_provider = client.api.run_function_providers.create(
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
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
            prompt="prompt",
            function_json={},
        )
        assert_matches_type(object, run_function_provider, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Openplugin) -> None:
        response = client.api.run_function_providers.with_raw_response.create(
            config={},
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run_function_provider = response.parse()
        assert_matches_type(object, run_function_provider, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Openplugin) -> None:
        with client.api.run_function_providers.with_streaming_response.create(
            config={},
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run_function_provider = response.parse()
            assert_matches_type(object, run_function_provider, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRunFunctionProviders:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenplugin) -> None:
        run_function_provider = await async_client.api.run_function_providers.create(
            config={},
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
            prompt="prompt",
        )
        assert_matches_type(object, run_function_provider, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenplugin) -> None:
        run_function_provider = await async_client.api.run_function_providers.create(
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
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
            prompt="prompt",
            function_json={},
        )
        assert_matches_type(object, run_function_provider, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenplugin) -> None:
        response = await async_client.api.run_function_providers.with_raw_response.create(
            config={},
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run_function_provider = await response.parse()
        assert_matches_type(object, run_function_provider, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenplugin) -> None:
        async with async_client.api.run_function_providers.with_streaming_response.create(
            config={},
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run_function_provider = await response.parse()
            assert_matches_type(object, run_function_provider, path=["response"])

        assert cast(Any, response.is_closed) is True
