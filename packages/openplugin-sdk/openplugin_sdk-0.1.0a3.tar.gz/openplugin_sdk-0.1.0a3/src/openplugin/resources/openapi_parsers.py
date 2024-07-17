# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options

__all__ = ["OpenAPIParsersResource", "AsyncOpenAPIParsersResource"]


class OpenAPIParsersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OpenAPIParsersResourceWithRawResponse:
        return OpenAPIParsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpenAPIParsersResourceWithStreamingResponse:
        return OpenAPIParsersResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Openapi Parser"""
        return self._get(
            "/api/openapi-parser",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncOpenAPIParsersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOpenAPIParsersResourceWithRawResponse:
        return AsyncOpenAPIParsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpenAPIParsersResourceWithStreamingResponse:
        return AsyncOpenAPIParsersResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Openapi Parser"""
        return await self._get(
            "/api/openapi-parser",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class OpenAPIParsersResourceWithRawResponse:
    def __init__(self, openapi_parsers: OpenAPIParsersResource) -> None:
        self._openapi_parsers = openapi_parsers

        self.retrieve = to_raw_response_wrapper(
            openapi_parsers.retrieve,
        )


class AsyncOpenAPIParsersResourceWithRawResponse:
    def __init__(self, openapi_parsers: AsyncOpenAPIParsersResource) -> None:
        self._openapi_parsers = openapi_parsers

        self.retrieve = async_to_raw_response_wrapper(
            openapi_parsers.retrieve,
        )


class OpenAPIParsersResourceWithStreamingResponse:
    def __init__(self, openapi_parsers: OpenAPIParsersResource) -> None:
        self._openapi_parsers = openapi_parsers

        self.retrieve = to_streamed_response_wrapper(
            openapi_parsers.retrieve,
        )


class AsyncOpenAPIParsersResourceWithStreamingResponse:
    def __init__(self, openapi_parsers: AsyncOpenAPIParsersResource) -> None:
        self._openapi_parsers = openapi_parsers

        self.retrieve = async_to_streamed_response_wrapper(
            openapi_parsers.retrieve,
        )
