# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import function_provider_list_params
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
from ..types.function_provider_list_response import FunctionProviderListResponse

__all__ = ["FunctionProvidersResource", "AsyncFunctionProvidersResource"]


class FunctionProvidersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FunctionProvidersResourceWithRawResponse:
        return FunctionProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FunctionProvidersResourceWithStreamingResponse:
        return FunctionProvidersResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        anthropic_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        cohere_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        fireworks_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        gemini_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        groq_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        mistral_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        openai_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        openplugin_manifest_url: Optional[str] | NotGiven = NOT_GIVEN,
        together_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FunctionProviderListResponse:
        """
        Enpoint to retrieve list of available function providers

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/function-providers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "anthropic_api_key": anthropic_api_key,
                        "cohere_api_key": cohere_api_key,
                        "fireworks_api_key": fireworks_api_key,
                        "gemini_api_key": gemini_api_key,
                        "groq_api_key": groq_api_key,
                        "mistral_api_key": mistral_api_key,
                        "openai_api_key": openai_api_key,
                        "openplugin_manifest_url": openplugin_manifest_url,
                        "together_api_key": together_api_key,
                        "type": type,
                    },
                    function_provider_list_params.FunctionProviderListParams,
                ),
            ),
            cast_to=FunctionProviderListResponse,
        )


class AsyncFunctionProvidersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFunctionProvidersResourceWithRawResponse:
        return AsyncFunctionProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFunctionProvidersResourceWithStreamingResponse:
        return AsyncFunctionProvidersResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        anthropic_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        cohere_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        fireworks_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        gemini_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        groq_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        mistral_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        openai_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        openplugin_manifest_url: Optional[str] | NotGiven = NOT_GIVEN,
        together_api_key: Optional[str] | NotGiven = NOT_GIVEN,
        type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FunctionProviderListResponse:
        """
        Enpoint to retrieve list of available function providers

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/function-providers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "anthropic_api_key": anthropic_api_key,
                        "cohere_api_key": cohere_api_key,
                        "fireworks_api_key": fireworks_api_key,
                        "gemini_api_key": gemini_api_key,
                        "groq_api_key": groq_api_key,
                        "mistral_api_key": mistral_api_key,
                        "openai_api_key": openai_api_key,
                        "openplugin_manifest_url": openplugin_manifest_url,
                        "together_api_key": together_api_key,
                        "type": type,
                    },
                    function_provider_list_params.FunctionProviderListParams,
                ),
            ),
            cast_to=FunctionProviderListResponse,
        )


class FunctionProvidersResourceWithRawResponse:
    def __init__(self, function_providers: FunctionProvidersResource) -> None:
        self._function_providers = function_providers

        self.list = to_raw_response_wrapper(
            function_providers.list,
        )


class AsyncFunctionProvidersResourceWithRawResponse:
    def __init__(self, function_providers: AsyncFunctionProvidersResource) -> None:
        self._function_providers = function_providers

        self.list = async_to_raw_response_wrapper(
            function_providers.list,
        )


class FunctionProvidersResourceWithStreamingResponse:
    def __init__(self, function_providers: FunctionProvidersResource) -> None:
        self._function_providers = function_providers

        self.list = to_streamed_response_wrapper(
            function_providers.list,
        )


class AsyncFunctionProvidersResourceWithStreamingResponse:
    def __init__(self, function_providers: AsyncFunctionProvidersResource) -> None:
        self._function_providers = function_providers

        self.list = async_to_streamed_response_wrapper(
            function_providers.list,
        )
