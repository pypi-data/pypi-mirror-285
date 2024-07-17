# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openplugin import Openplugin, AsyncOpenplugin
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFunctionProviders:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Openplugin) -> None:
        function_provider = client.api.function_providers.list()
        assert_matches_type(object, function_provider, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Openplugin) -> None:
        function_provider = client.api.function_providers.list(
            anthropic_api_key="anthropic_api_key",
            cohere_api_key="cohere_api_key",
            fireworks_api_key="fireworks_api_key",
            gemini_api_key="gemini_api_key",
            groq_api_key="groq_api_key",
            mistral_api_key="mistral_api_key",
            openai_api_key="openai_api_key",
            openplugin_manifest_url="openplugin_manifest_url",
            together_api_key="together_api_key",
            type="type",
        )
        assert_matches_type(object, function_provider, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Openplugin) -> None:
        response = client.api.function_providers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        function_provider = response.parse()
        assert_matches_type(object, function_provider, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Openplugin) -> None:
        with client.api.function_providers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            function_provider = response.parse()
            assert_matches_type(object, function_provider, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncFunctionProviders:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenplugin) -> None:
        function_provider = await async_client.api.function_providers.list()
        assert_matches_type(object, function_provider, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenplugin) -> None:
        function_provider = await async_client.api.function_providers.list(
            anthropic_api_key="anthropic_api_key",
            cohere_api_key="cohere_api_key",
            fireworks_api_key="fireworks_api_key",
            gemini_api_key="gemini_api_key",
            groq_api_key="groq_api_key",
            mistral_api_key="mistral_api_key",
            openai_api_key="openai_api_key",
            openplugin_manifest_url="openplugin_manifest_url",
            together_api_key="together_api_key",
            type="type",
        )
        assert_matches_type(object, function_provider, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenplugin) -> None:
        response = await async_client.api.function_providers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        function_provider = await response.parse()
        assert_matches_type(object, function_provider, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenplugin) -> None:
        async with async_client.api.function_providers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            function_provider = await response.parse()
            assert_matches_type(object, function_provider, path=["response"])

        assert cast(Any, response.is_closed) is True
