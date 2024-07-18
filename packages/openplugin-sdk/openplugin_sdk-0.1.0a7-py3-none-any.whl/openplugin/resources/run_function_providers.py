# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import run_function_provider_create_params
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
from ..types.run_function_provider_create_response import RunFunctionProviderCreateResponse

__all__ = ["RunFunctionProvidersResource", "AsyncRunFunctionProvidersResource"]


class RunFunctionProvidersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RunFunctionProvidersResourceWithRawResponse:
        return RunFunctionProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunFunctionProvidersResourceWithStreamingResponse:
        return RunFunctionProvidersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        config: run_function_provider_create_params.Config,
        function_provider_name: str,
        openplugin_manifest_url: str,
        prompt: str,
        function_json: Optional[object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunFunctionProviderCreateResponse:
        """
        Enpoint to run a function provider

        Args:
          config: Represents the API configuration for a plugin.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/run-function-provider",
            body=maybe_transform(
                {
                    "config": config,
                    "function_provider_name": function_provider_name,
                    "openplugin_manifest_url": openplugin_manifest_url,
                    "prompt": prompt,
                    "function_json": function_json,
                },
                run_function_provider_create_params.RunFunctionProviderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunFunctionProviderCreateResponse,
        )


class AsyncRunFunctionProvidersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRunFunctionProvidersResourceWithRawResponse:
        return AsyncRunFunctionProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunFunctionProvidersResourceWithStreamingResponse:
        return AsyncRunFunctionProvidersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        config: run_function_provider_create_params.Config,
        function_provider_name: str,
        openplugin_manifest_url: str,
        prompt: str,
        function_json: Optional[object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunFunctionProviderCreateResponse:
        """
        Enpoint to run a function provider

        Args:
          config: Represents the API configuration for a plugin.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/run-function-provider",
            body=await async_maybe_transform(
                {
                    "config": config,
                    "function_provider_name": function_provider_name,
                    "openplugin_manifest_url": openplugin_manifest_url,
                    "prompt": prompt,
                    "function_json": function_json,
                },
                run_function_provider_create_params.RunFunctionProviderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunFunctionProviderCreateResponse,
        )


class RunFunctionProvidersResourceWithRawResponse:
    def __init__(self, run_function_providers: RunFunctionProvidersResource) -> None:
        self._run_function_providers = run_function_providers

        self.create = to_raw_response_wrapper(
            run_function_providers.create,
        )


class AsyncRunFunctionProvidersResourceWithRawResponse:
    def __init__(self, run_function_providers: AsyncRunFunctionProvidersResource) -> None:
        self._run_function_providers = run_function_providers

        self.create = async_to_raw_response_wrapper(
            run_function_providers.create,
        )


class RunFunctionProvidersResourceWithStreamingResponse:
    def __init__(self, run_function_providers: RunFunctionProvidersResource) -> None:
        self._run_function_providers = run_function_providers

        self.create = to_streamed_response_wrapper(
            run_function_providers.create,
        )


class AsyncRunFunctionProvidersResourceWithStreamingResponse:
    def __init__(self, run_function_providers: AsyncRunFunctionProvidersResource) -> None:
        self._run_function_providers = run_function_providers

        self.create = async_to_streamed_response_wrapper(
            run_function_providers.create,
        )
