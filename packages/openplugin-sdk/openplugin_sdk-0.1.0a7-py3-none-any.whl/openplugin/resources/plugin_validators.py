# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import plugin_validator_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.plugin_validator_create_response import PluginValidatorCreateResponse

__all__ = ["PluginValidatorsResource", "AsyncPluginValidatorsResource"]


class PluginValidatorsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PluginValidatorsResourceWithRawResponse:
        return PluginValidatorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PluginValidatorsResourceWithStreamingResponse:
        return PluginValidatorsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PluginValidatorCreateResponse:
        """
        Enpoint to validate a plugin manifest

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/plugin-validator",
            body=maybe_transform(body, plugin_validator_create_params.PluginValidatorCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PluginValidatorCreateResponse,
        )


class AsyncPluginValidatorsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPluginValidatorsResourceWithRawResponse:
        return AsyncPluginValidatorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPluginValidatorsResourceWithStreamingResponse:
        return AsyncPluginValidatorsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PluginValidatorCreateResponse:
        """
        Enpoint to validate a plugin manifest

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/plugin-validator",
            body=await async_maybe_transform(body, plugin_validator_create_params.PluginValidatorCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PluginValidatorCreateResponse,
        )


class PluginValidatorsResourceWithRawResponse:
    def __init__(self, plugin_validators: PluginValidatorsResource) -> None:
        self._plugin_validators = plugin_validators

        self.create = to_raw_response_wrapper(
            plugin_validators.create,
        )


class AsyncPluginValidatorsResourceWithRawResponse:
    def __init__(self, plugin_validators: AsyncPluginValidatorsResource) -> None:
        self._plugin_validators = plugin_validators

        self.create = async_to_raw_response_wrapper(
            plugin_validators.create,
        )


class PluginValidatorsResourceWithStreamingResponse:
    def __init__(self, plugin_validators: PluginValidatorsResource) -> None:
        self._plugin_validators = plugin_validators

        self.create = to_streamed_response_wrapper(
            plugin_validators.create,
        )


class AsyncPluginValidatorsResourceWithStreamingResponse:
    def __init__(self, plugin_validators: AsyncPluginValidatorsResource) -> None:
        self._plugin_validators = plugin_validators

        self.create = async_to_streamed_response_wrapper(
            plugin_validators.create,
        )
