# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openplugin import Openplugin, AsyncOpenplugin
from tests.utils import assert_matches_type
from openplugin.types import FunctionProviderRequestRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFunctionProviderRequests:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Openplugin) -> None:
        function_provider_request = client.function_provider_requests.retrieve(
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
        )
        assert_matches_type(FunctionProviderRequestRetrieveResponse, function_provider_request, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Openplugin) -> None:
        response = client.function_provider_requests.with_raw_response.retrieve(
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        function_provider_request = response.parse()
        assert_matches_type(FunctionProviderRequestRetrieveResponse, function_provider_request, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Openplugin) -> None:
        with client.function_provider_requests.with_streaming_response.retrieve(
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            function_provider_request = response.parse()
            assert_matches_type(FunctionProviderRequestRetrieveResponse, function_provider_request, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncFunctionProviderRequests:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenplugin) -> None:
        function_provider_request = await async_client.function_provider_requests.retrieve(
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
        )
        assert_matches_type(FunctionProviderRequestRetrieveResponse, function_provider_request, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenplugin) -> None:
        response = await async_client.function_provider_requests.with_raw_response.retrieve(
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        function_provider_request = await response.parse()
        assert_matches_type(FunctionProviderRequestRetrieveResponse, function_provider_request, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenplugin) -> None:
        async with async_client.function_provider_requests.with_streaming_response.retrieve(
            function_provider_name="function_provider_name",
            openplugin_manifest_url="openplugin_manifest_url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            function_provider_request = await response.parse()
            assert_matches_type(FunctionProviderRequestRetrieveResponse, function_provider_request, path=["response"])

        assert cast(Any, response.is_closed) is True
