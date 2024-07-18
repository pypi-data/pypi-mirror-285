# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openplugin import Openplugin, AsyncOpenplugin
from tests.utils import assert_matches_type
from openplugin.types import PluginValidatorCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPluginValidators:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Openplugin) -> None:
        plugin_validator = client.plugin_validators.create(
            body={},
        )
        assert_matches_type(PluginValidatorCreateResponse, plugin_validator, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Openplugin) -> None:
        response = client.plugin_validators.with_raw_response.create(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plugin_validator = response.parse()
        assert_matches_type(PluginValidatorCreateResponse, plugin_validator, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Openplugin) -> None:
        with client.plugin_validators.with_streaming_response.create(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plugin_validator = response.parse()
            assert_matches_type(PluginValidatorCreateResponse, plugin_validator, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPluginValidators:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenplugin) -> None:
        plugin_validator = await async_client.plugin_validators.create(
            body={},
        )
        assert_matches_type(PluginValidatorCreateResponse, plugin_validator, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenplugin) -> None:
        response = await async_client.plugin_validators.with_raw_response.create(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plugin_validator = await response.parse()
        assert_matches_type(PluginValidatorCreateResponse, plugin_validator, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenplugin) -> None:
        async with async_client.plugin_validators.with_streaming_response.create(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plugin_validator = await response.parse()
            assert_matches_type(PluginValidatorCreateResponse, plugin_validator, path=["response"])

        assert cast(Any, response.is_closed) is True
