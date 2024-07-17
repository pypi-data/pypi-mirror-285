# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import openapi_param_parser_retrieve_params
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

__all__ = ["OpenAPIParamParsersResource", "AsyncOpenAPIParamParsersResource"]


class OpenAPIParamParsersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OpenAPIParamParsersResourceWithRawResponse:
        return OpenAPIParamParsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpenAPIParamParsersResourceWithStreamingResponse:
        return OpenAPIParamParsersResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        openapi_doc_url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Openapi Param Parser

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/openapi-param-parser",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"openapi_doc_url": openapi_doc_url},
                    openapi_param_parser_retrieve_params.OpenAPIParamParserRetrieveParams,
                ),
            ),
            cast_to=object,
        )


class AsyncOpenAPIParamParsersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOpenAPIParamParsersResourceWithRawResponse:
        return AsyncOpenAPIParamParsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpenAPIParamParsersResourceWithStreamingResponse:
        return AsyncOpenAPIParamParsersResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        openapi_doc_url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Openapi Param Parser

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/openapi-param-parser",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"openapi_doc_url": openapi_doc_url},
                    openapi_param_parser_retrieve_params.OpenAPIParamParserRetrieveParams,
                ),
            ),
            cast_to=object,
        )


class OpenAPIParamParsersResourceWithRawResponse:
    def __init__(self, openapi_param_parsers: OpenAPIParamParsersResource) -> None:
        self._openapi_param_parsers = openapi_param_parsers

        self.retrieve = to_raw_response_wrapper(
            openapi_param_parsers.retrieve,
        )


class AsyncOpenAPIParamParsersResourceWithRawResponse:
    def __init__(self, openapi_param_parsers: AsyncOpenAPIParamParsersResource) -> None:
        self._openapi_param_parsers = openapi_param_parsers

        self.retrieve = async_to_raw_response_wrapper(
            openapi_param_parsers.retrieve,
        )


class OpenAPIParamParsersResourceWithStreamingResponse:
    def __init__(self, openapi_param_parsers: OpenAPIParamParsersResource) -> None:
        self._openapi_param_parsers = openapi_param_parsers

        self.retrieve = to_streamed_response_wrapper(
            openapi_param_parsers.retrieve,
        )


class AsyncOpenAPIParamParsersResourceWithStreamingResponse:
    def __init__(self, openapi_param_parsers: AsyncOpenAPIParamParsersResource) -> None:
        self._openapi_param_parsers = openapi_param_parsers

        self.retrieve = async_to_streamed_response_wrapper(
            openapi_param_parsers.retrieve,
        )
