# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .info import (
    InfoResource,
    AsyncInfoResource,
    InfoResourceWithRawResponse,
    AsyncInfoResourceWithRawResponse,
    InfoResourceWithStreamingResponse,
    AsyncInfoResourceWithStreamingResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from .processors import (
    ProcessorsResource,
    AsyncProcessorsResource,
    ProcessorsResourceWithRawResponse,
    AsyncProcessorsResourceWithRawResponse,
    ProcessorsResourceWithStreamingResponse,
    AsyncProcessorsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from .plugin_selectors import (
    PluginSelectorsResource,
    AsyncPluginSelectorsResource,
    PluginSelectorsResourceWithRawResponse,
    AsyncPluginSelectorsResourceWithRawResponse,
    PluginSelectorsResourceWithStreamingResponse,
    AsyncPluginSelectorsResourceWithStreamingResponse,
)
from .function_providers import (
    FunctionProvidersResource,
    AsyncFunctionProvidersResource,
    FunctionProvidersResourceWithRawResponse,
    AsyncFunctionProvidersResourceWithRawResponse,
    FunctionProvidersResourceWithStreamingResponse,
    AsyncFunctionProvidersResourceWithStreamingResponse,
)
from .operation_executions import (
    OperationExecutionsResource,
    AsyncOperationExecutionsResource,
    OperationExecutionsResourceWithRawResponse,
    AsyncOperationExecutionsResourceWithRawResponse,
    OperationExecutionsResourceWithStreamingResponse,
    AsyncOperationExecutionsResourceWithStreamingResponse,
)
from .run_function_providers import (
    RunFunctionProvidersResource,
    AsyncRunFunctionProvidersResource,
    RunFunctionProvidersResourceWithRawResponse,
    AsyncRunFunctionProvidersResourceWithRawResponse,
    RunFunctionProvidersResourceWithStreamingResponse,
    AsyncRunFunctionProvidersResourceWithStreamingResponse,
)
from .function_provider_requests import (
    FunctionProviderRequestsResource,
    AsyncFunctionProviderRequestsResource,
    FunctionProviderRequestsResourceWithRawResponse,
    AsyncFunctionProviderRequestsResourceWithRawResponse,
    FunctionProviderRequestsResourceWithStreamingResponse,
    AsyncFunctionProviderRequestsResourceWithStreamingResponse,
)
from .plugin_execution_pipelines import (
    PluginExecutionPipelinesResource,
    AsyncPluginExecutionPipelinesResource,
    PluginExecutionPipelinesResourceWithRawResponse,
    AsyncPluginExecutionPipelinesResourceWithRawResponse,
    PluginExecutionPipelinesResourceWithStreamingResponse,
    AsyncPluginExecutionPipelinesResourceWithStreamingResponse,
)
from .operation_signature_builders import (
    OperationSignatureBuildersResource,
    AsyncOperationSignatureBuildersResource,
    OperationSignatureBuildersResourceWithRawResponse,
    AsyncOperationSignatureBuildersResourceWithRawResponse,
    OperationSignatureBuildersResourceWithStreamingResponse,
    AsyncOperationSignatureBuildersResourceWithStreamingResponse,
)

__all__ = ["APIResource", "AsyncAPIResource"]


class APIResource(SyncAPIResource):
    @cached_property
    def plugin_selectors(self) -> PluginSelectorsResource:
        return PluginSelectorsResource(self._client)

    @cached_property
    def operation_signature_builders(self) -> OperationSignatureBuildersResource:
        return OperationSignatureBuildersResource(self._client)

    @cached_property
    def operation_executions(self) -> OperationExecutionsResource:
        return OperationExecutionsResource(self._client)

    @cached_property
    def info(self) -> InfoResource:
        return InfoResource(self._client)

    @cached_property
    def plugin_execution_pipelines(self) -> PluginExecutionPipelinesResource:
        return PluginExecutionPipelinesResource(self._client)

    @cached_property
    def processors(self) -> ProcessorsResource:
        return ProcessorsResource(self._client)

    @cached_property
    def function_providers(self) -> FunctionProvidersResource:
        return FunctionProvidersResource(self._client)

    @cached_property
    def function_provider_requests(self) -> FunctionProviderRequestsResource:
        return FunctionProviderRequestsResource(self._client)

    @cached_property
    def run_function_providers(self) -> RunFunctionProvidersResource:
        return RunFunctionProvidersResource(self._client)

    @cached_property
    def with_raw_response(self) -> APIResourceWithRawResponse:
        return APIResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> APIResourceWithStreamingResponse:
        return APIResourceWithStreamingResponse(self)

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
        """Version"""
        return self._get(
            "/api/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncAPIResource(AsyncAPIResource):
    @cached_property
    def plugin_selectors(self) -> AsyncPluginSelectorsResource:
        return AsyncPluginSelectorsResource(self._client)

    @cached_property
    def operation_signature_builders(self) -> AsyncOperationSignatureBuildersResource:
        return AsyncOperationSignatureBuildersResource(self._client)

    @cached_property
    def operation_executions(self) -> AsyncOperationExecutionsResource:
        return AsyncOperationExecutionsResource(self._client)

    @cached_property
    def info(self) -> AsyncInfoResource:
        return AsyncInfoResource(self._client)

    @cached_property
    def plugin_execution_pipelines(self) -> AsyncPluginExecutionPipelinesResource:
        return AsyncPluginExecutionPipelinesResource(self._client)

    @cached_property
    def processors(self) -> AsyncProcessorsResource:
        return AsyncProcessorsResource(self._client)

    @cached_property
    def function_providers(self) -> AsyncFunctionProvidersResource:
        return AsyncFunctionProvidersResource(self._client)

    @cached_property
    def function_provider_requests(self) -> AsyncFunctionProviderRequestsResource:
        return AsyncFunctionProviderRequestsResource(self._client)

    @cached_property
    def run_function_providers(self) -> AsyncRunFunctionProvidersResource:
        return AsyncRunFunctionProvidersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAPIResourceWithRawResponse:
        return AsyncAPIResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAPIResourceWithStreamingResponse:
        return AsyncAPIResourceWithStreamingResponse(self)

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
        """Version"""
        return await self._get(
            "/api/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class APIResourceWithRawResponse:
    def __init__(self, api: APIResource) -> None:
        self._api = api

        self.list = to_raw_response_wrapper(
            api.list,
        )

    @cached_property
    def plugin_selectors(self) -> PluginSelectorsResourceWithRawResponse:
        return PluginSelectorsResourceWithRawResponse(self._api.plugin_selectors)

    @cached_property
    def operation_signature_builders(self) -> OperationSignatureBuildersResourceWithRawResponse:
        return OperationSignatureBuildersResourceWithRawResponse(self._api.operation_signature_builders)

    @cached_property
    def operation_executions(self) -> OperationExecutionsResourceWithRawResponse:
        return OperationExecutionsResourceWithRawResponse(self._api.operation_executions)

    @cached_property
    def info(self) -> InfoResourceWithRawResponse:
        return InfoResourceWithRawResponse(self._api.info)

    @cached_property
    def plugin_execution_pipelines(self) -> PluginExecutionPipelinesResourceWithRawResponse:
        return PluginExecutionPipelinesResourceWithRawResponse(self._api.plugin_execution_pipelines)

    @cached_property
    def processors(self) -> ProcessorsResourceWithRawResponse:
        return ProcessorsResourceWithRawResponse(self._api.processors)

    @cached_property
    def function_providers(self) -> FunctionProvidersResourceWithRawResponse:
        return FunctionProvidersResourceWithRawResponse(self._api.function_providers)

    @cached_property
    def function_provider_requests(self) -> FunctionProviderRequestsResourceWithRawResponse:
        return FunctionProviderRequestsResourceWithRawResponse(self._api.function_provider_requests)

    @cached_property
    def run_function_providers(self) -> RunFunctionProvidersResourceWithRawResponse:
        return RunFunctionProvidersResourceWithRawResponse(self._api.run_function_providers)


class AsyncAPIResourceWithRawResponse:
    def __init__(self, api: AsyncAPIResource) -> None:
        self._api = api

        self.list = async_to_raw_response_wrapper(
            api.list,
        )

    @cached_property
    def plugin_selectors(self) -> AsyncPluginSelectorsResourceWithRawResponse:
        return AsyncPluginSelectorsResourceWithRawResponse(self._api.plugin_selectors)

    @cached_property
    def operation_signature_builders(self) -> AsyncOperationSignatureBuildersResourceWithRawResponse:
        return AsyncOperationSignatureBuildersResourceWithRawResponse(self._api.operation_signature_builders)

    @cached_property
    def operation_executions(self) -> AsyncOperationExecutionsResourceWithRawResponse:
        return AsyncOperationExecutionsResourceWithRawResponse(self._api.operation_executions)

    @cached_property
    def info(self) -> AsyncInfoResourceWithRawResponse:
        return AsyncInfoResourceWithRawResponse(self._api.info)

    @cached_property
    def plugin_execution_pipelines(self) -> AsyncPluginExecutionPipelinesResourceWithRawResponse:
        return AsyncPluginExecutionPipelinesResourceWithRawResponse(self._api.plugin_execution_pipelines)

    @cached_property
    def processors(self) -> AsyncProcessorsResourceWithRawResponse:
        return AsyncProcessorsResourceWithRawResponse(self._api.processors)

    @cached_property
    def function_providers(self) -> AsyncFunctionProvidersResourceWithRawResponse:
        return AsyncFunctionProvidersResourceWithRawResponse(self._api.function_providers)

    @cached_property
    def function_provider_requests(self) -> AsyncFunctionProviderRequestsResourceWithRawResponse:
        return AsyncFunctionProviderRequestsResourceWithRawResponse(self._api.function_provider_requests)

    @cached_property
    def run_function_providers(self) -> AsyncRunFunctionProvidersResourceWithRawResponse:
        return AsyncRunFunctionProvidersResourceWithRawResponse(self._api.run_function_providers)


class APIResourceWithStreamingResponse:
    def __init__(self, api: APIResource) -> None:
        self._api = api

        self.list = to_streamed_response_wrapper(
            api.list,
        )

    @cached_property
    def plugin_selectors(self) -> PluginSelectorsResourceWithStreamingResponse:
        return PluginSelectorsResourceWithStreamingResponse(self._api.plugin_selectors)

    @cached_property
    def operation_signature_builders(self) -> OperationSignatureBuildersResourceWithStreamingResponse:
        return OperationSignatureBuildersResourceWithStreamingResponse(self._api.operation_signature_builders)

    @cached_property
    def operation_executions(self) -> OperationExecutionsResourceWithStreamingResponse:
        return OperationExecutionsResourceWithStreamingResponse(self._api.operation_executions)

    @cached_property
    def info(self) -> InfoResourceWithStreamingResponse:
        return InfoResourceWithStreamingResponse(self._api.info)

    @cached_property
    def plugin_execution_pipelines(self) -> PluginExecutionPipelinesResourceWithStreamingResponse:
        return PluginExecutionPipelinesResourceWithStreamingResponse(self._api.plugin_execution_pipelines)

    @cached_property
    def processors(self) -> ProcessorsResourceWithStreamingResponse:
        return ProcessorsResourceWithStreamingResponse(self._api.processors)

    @cached_property
    def function_providers(self) -> FunctionProvidersResourceWithStreamingResponse:
        return FunctionProvidersResourceWithStreamingResponse(self._api.function_providers)

    @cached_property
    def function_provider_requests(self) -> FunctionProviderRequestsResourceWithStreamingResponse:
        return FunctionProviderRequestsResourceWithStreamingResponse(self._api.function_provider_requests)

    @cached_property
    def run_function_providers(self) -> RunFunctionProvidersResourceWithStreamingResponse:
        return RunFunctionProvidersResourceWithStreamingResponse(self._api.run_function_providers)


class AsyncAPIResourceWithStreamingResponse:
    def __init__(self, api: AsyncAPIResource) -> None:
        self._api = api

        self.list = async_to_streamed_response_wrapper(
            api.list,
        )

    @cached_property
    def plugin_selectors(self) -> AsyncPluginSelectorsResourceWithStreamingResponse:
        return AsyncPluginSelectorsResourceWithStreamingResponse(self._api.plugin_selectors)

    @cached_property
    def operation_signature_builders(self) -> AsyncOperationSignatureBuildersResourceWithStreamingResponse:
        return AsyncOperationSignatureBuildersResourceWithStreamingResponse(self._api.operation_signature_builders)

    @cached_property
    def operation_executions(self) -> AsyncOperationExecutionsResourceWithStreamingResponse:
        return AsyncOperationExecutionsResourceWithStreamingResponse(self._api.operation_executions)

    @cached_property
    def info(self) -> AsyncInfoResourceWithStreamingResponse:
        return AsyncInfoResourceWithStreamingResponse(self._api.info)

    @cached_property
    def plugin_execution_pipelines(self) -> AsyncPluginExecutionPipelinesResourceWithStreamingResponse:
        return AsyncPluginExecutionPipelinesResourceWithStreamingResponse(self._api.plugin_execution_pipelines)

    @cached_property
    def processors(self) -> AsyncProcessorsResourceWithStreamingResponse:
        return AsyncProcessorsResourceWithStreamingResponse(self._api.processors)

    @cached_property
    def function_providers(self) -> AsyncFunctionProvidersResourceWithStreamingResponse:
        return AsyncFunctionProvidersResourceWithStreamingResponse(self._api.function_providers)

    @cached_property
    def function_provider_requests(self) -> AsyncFunctionProviderRequestsResourceWithStreamingResponse:
        return AsyncFunctionProviderRequestsResourceWithStreamingResponse(self._api.function_provider_requests)

    @cached_property
    def run_function_providers(self) -> AsyncRunFunctionProvidersResourceWithStreamingResponse:
        return AsyncRunFunctionProvidersResourceWithStreamingResponse(self._api.run_function_providers)
