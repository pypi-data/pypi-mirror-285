# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options

__all__ = ["ProcessorsResource", "AsyncProcessorsResource"]


class ProcessorsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProcessorsResourceWithRawResponse:
        return ProcessorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProcessorsResourceWithStreamingResponse:
        return ProcessorsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Processors"""
        return self._get(
            "/api/processors",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncProcessorsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProcessorsResourceWithRawResponse:
        return AsyncProcessorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProcessorsResourceWithStreamingResponse:
        return AsyncProcessorsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Processors"""
        return await self._get(
            "/api/processors",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ProcessorsResourceWithRawResponse:
    def __init__(self, processors: ProcessorsResource) -> None:
        self._processors = processors

        self.list = to_raw_response_wrapper(
            processors.list,
        )


class AsyncProcessorsResourceWithRawResponse:
    def __init__(self, processors: AsyncProcessorsResource) -> None:
        self._processors = processors

        self.list = async_to_raw_response_wrapper(
            processors.list,
        )


class ProcessorsResourceWithStreamingResponse:
    def __init__(self, processors: ProcessorsResource) -> None:
        self._processors = processors

        self.list = to_streamed_response_wrapper(
            processors.list,
        )


class AsyncProcessorsResourceWithStreamingResponse:
    def __init__(self, processors: AsyncProcessorsResource) -> None:
        self._processors = processors

        self.list = async_to_streamed_response_wrapper(
            processors.list,
        )
