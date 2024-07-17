# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.api import function_provider_request_retrieve_params
from ..._base_client import make_request_options

__all__ = ["FunctionProviderRequestsResource", "AsyncFunctionProviderRequestsResource"]


class FunctionProviderRequestsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FunctionProviderRequestsResourceWithRawResponse:
        return FunctionProviderRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FunctionProviderRequestsResourceWithStreamingResponse:
        return FunctionProviderRequestsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        function_provider_name: str,
        openplugin_manifest_url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Get Function Provider Request

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/function-provider-request",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "function_provider_name": function_provider_name,
                        "openplugin_manifest_url": openplugin_manifest_url,
                    },
                    function_provider_request_retrieve_params.FunctionProviderRequestRetrieveParams,
                ),
            ),
            cast_to=object,
        )


class AsyncFunctionProviderRequestsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFunctionProviderRequestsResourceWithRawResponse:
        return AsyncFunctionProviderRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFunctionProviderRequestsResourceWithStreamingResponse:
        return AsyncFunctionProviderRequestsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        function_provider_name: str,
        openplugin_manifest_url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Get Function Provider Request

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/function-provider-request",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "function_provider_name": function_provider_name,
                        "openplugin_manifest_url": openplugin_manifest_url,
                    },
                    function_provider_request_retrieve_params.FunctionProviderRequestRetrieveParams,
                ),
            ),
            cast_to=object,
        )


class FunctionProviderRequestsResourceWithRawResponse:
    def __init__(self, function_provider_requests: FunctionProviderRequestsResource) -> None:
        self._function_provider_requests = function_provider_requests

        self.retrieve = to_raw_response_wrapper(
            function_provider_requests.retrieve,
        )


class AsyncFunctionProviderRequestsResourceWithRawResponse:
    def __init__(self, function_provider_requests: AsyncFunctionProviderRequestsResource) -> None:
        self._function_provider_requests = function_provider_requests

        self.retrieve = async_to_raw_response_wrapper(
            function_provider_requests.retrieve,
        )


class FunctionProviderRequestsResourceWithStreamingResponse:
    def __init__(self, function_provider_requests: FunctionProviderRequestsResource) -> None:
        self._function_provider_requests = function_provider_requests

        self.retrieve = to_streamed_response_wrapper(
            function_provider_requests.retrieve,
        )


class AsyncFunctionProviderRequestsResourceWithStreamingResponse:
    def __init__(self, function_provider_requests: AsyncFunctionProviderRequestsResource) -> None:
        self._function_provider_requests = function_provider_requests

        self.retrieve = async_to_streamed_response_wrapper(
            function_provider_requests.retrieve,
        )
