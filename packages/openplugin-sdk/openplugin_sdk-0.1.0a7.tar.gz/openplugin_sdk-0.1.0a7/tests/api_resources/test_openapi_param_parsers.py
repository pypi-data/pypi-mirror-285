# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openplugin import Openplugin, AsyncOpenplugin
from tests.utils import assert_matches_type
from openplugin.types import OpenAPIParamParserRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOpenAPIParamParsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Openplugin) -> None:
        openapi_param_parser = client.openapi_param_parsers.retrieve(
            openapi_doc_url="openapi_doc_url",
        )
        assert_matches_type(OpenAPIParamParserRetrieveResponse, openapi_param_parser, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Openplugin) -> None:
        response = client.openapi_param_parsers.with_raw_response.retrieve(
            openapi_doc_url="openapi_doc_url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        openapi_param_parser = response.parse()
        assert_matches_type(OpenAPIParamParserRetrieveResponse, openapi_param_parser, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Openplugin) -> None:
        with client.openapi_param_parsers.with_streaming_response.retrieve(
            openapi_doc_url="openapi_doc_url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            openapi_param_parser = response.parse()
            assert_matches_type(OpenAPIParamParserRetrieveResponse, openapi_param_parser, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOpenAPIParamParsers:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenplugin) -> None:
        openapi_param_parser = await async_client.openapi_param_parsers.retrieve(
            openapi_doc_url="openapi_doc_url",
        )
        assert_matches_type(OpenAPIParamParserRetrieveResponse, openapi_param_parser, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenplugin) -> None:
        response = await async_client.openapi_param_parsers.with_raw_response.retrieve(
            openapi_doc_url="openapi_doc_url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        openapi_param_parser = await response.parse()
        assert_matches_type(OpenAPIParamParserRetrieveResponse, openapi_param_parser, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenplugin) -> None:
        async with async_client.openapi_param_parsers.with_streaming_response.retrieve(
            openapi_doc_url="openapi_doc_url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            openapi_param_parser = await response.parse()
            assert_matches_type(OpenAPIParamParserRetrieveResponse, openapi_param_parser, path=["response"])

        assert cast(Any, response.is_closed) is True
