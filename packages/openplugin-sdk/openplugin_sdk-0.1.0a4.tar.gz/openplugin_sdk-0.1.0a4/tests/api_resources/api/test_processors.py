# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openplugin import Openplugin, AsyncOpenplugin
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProcessors:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Openplugin) -> None:
        processor = client.api.processors.list()
        assert_matches_type(object, processor, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Openplugin) -> None:
        response = client.api.processors.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        processor = response.parse()
        assert_matches_type(object, processor, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Openplugin) -> None:
        with client.api.processors.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            processor = response.parse()
            assert_matches_type(object, processor, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncProcessors:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenplugin) -> None:
        processor = await async_client.api.processors.list()
        assert_matches_type(object, processor, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenplugin) -> None:
        response = await async_client.api.processors.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        processor = await response.parse()
        assert_matches_type(object, processor, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenplugin) -> None:
        async with async_client.api.processors.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            processor = await response.parse()
            assert_matches_type(object, processor, path=["response"])

        assert cast(Any, response.is_closed) is True
