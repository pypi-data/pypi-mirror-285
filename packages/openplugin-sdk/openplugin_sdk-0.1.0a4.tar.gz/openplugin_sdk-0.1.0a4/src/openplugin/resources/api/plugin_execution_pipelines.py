# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional

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
from ...types.api import plugin_execution_pipeline_create_params
from ..._base_client import make_request_options

__all__ = ["PluginExecutionPipelinesResource", "AsyncPluginExecutionPipelinesResource"]


class PluginExecutionPipelinesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PluginExecutionPipelinesResourceWithRawResponse:
        return PluginExecutionPipelinesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PluginExecutionPipelinesResourceWithStreamingResponse:
        return PluginExecutionPipelinesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        conversation: Iterable[object],
        header: object,
        prompt: str,
        auth_query_param: Optional[object] | NotGiven = NOT_GIVEN,
        config: Optional[plugin_execution_pipeline_create_params.Config] | NotGiven = NOT_GIVEN,
        enable_ui_form_controls: bool | NotGiven = NOT_GIVEN,
        function_provider_input: Optional[plugin_execution_pipeline_create_params.FunctionProviderInput]
        | NotGiven = NOT_GIVEN,
        openplugin_manifest_obj: Optional[object] | NotGiven = NOT_GIVEN,
        openplugin_manifest_url: Optional[str] | NotGiven = NOT_GIVEN,
        output_module_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        run_all_output_modules: bool | NotGiven = NOT_GIVEN,
        selected_operation: Optional[str] | NotGiven = NOT_GIVEN,
        session_variables: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Plugin Execution Pipeline

        Args:
          config: Represents the API configuration for a plugin.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/plugin-execution-pipeline",
            body=maybe_transform(
                {
                    "conversation": conversation,
                    "header": header,
                    "prompt": prompt,
                    "auth_query_param": auth_query_param,
                    "config": config,
                    "enable_ui_form_controls": enable_ui_form_controls,
                    "function_provider_input": function_provider_input,
                    "openplugin_manifest_obj": openplugin_manifest_obj,
                    "openplugin_manifest_url": openplugin_manifest_url,
                    "output_module_names": output_module_names,
                    "run_all_output_modules": run_all_output_modules,
                    "selected_operation": selected_operation,
                    "session_variables": session_variables,
                },
                plugin_execution_pipeline_create_params.PluginExecutionPipelineCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncPluginExecutionPipelinesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPluginExecutionPipelinesResourceWithRawResponse:
        return AsyncPluginExecutionPipelinesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPluginExecutionPipelinesResourceWithStreamingResponse:
        return AsyncPluginExecutionPipelinesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        conversation: Iterable[object],
        header: object,
        prompt: str,
        auth_query_param: Optional[object] | NotGiven = NOT_GIVEN,
        config: Optional[plugin_execution_pipeline_create_params.Config] | NotGiven = NOT_GIVEN,
        enable_ui_form_controls: bool | NotGiven = NOT_GIVEN,
        function_provider_input: Optional[plugin_execution_pipeline_create_params.FunctionProviderInput]
        | NotGiven = NOT_GIVEN,
        openplugin_manifest_obj: Optional[object] | NotGiven = NOT_GIVEN,
        openplugin_manifest_url: Optional[str] | NotGiven = NOT_GIVEN,
        output_module_names: Optional[List[str]] | NotGiven = NOT_GIVEN,
        run_all_output_modules: bool | NotGiven = NOT_GIVEN,
        selected_operation: Optional[str] | NotGiven = NOT_GIVEN,
        session_variables: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Plugin Execution Pipeline

        Args:
          config: Represents the API configuration for a plugin.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/plugin-execution-pipeline",
            body=await async_maybe_transform(
                {
                    "conversation": conversation,
                    "header": header,
                    "prompt": prompt,
                    "auth_query_param": auth_query_param,
                    "config": config,
                    "enable_ui_form_controls": enable_ui_form_controls,
                    "function_provider_input": function_provider_input,
                    "openplugin_manifest_obj": openplugin_manifest_obj,
                    "openplugin_manifest_url": openplugin_manifest_url,
                    "output_module_names": output_module_names,
                    "run_all_output_modules": run_all_output_modules,
                    "selected_operation": selected_operation,
                    "session_variables": session_variables,
                },
                plugin_execution_pipeline_create_params.PluginExecutionPipelineCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class PluginExecutionPipelinesResourceWithRawResponse:
    def __init__(self, plugin_execution_pipelines: PluginExecutionPipelinesResource) -> None:
        self._plugin_execution_pipelines = plugin_execution_pipelines

        self.create = to_raw_response_wrapper(
            plugin_execution_pipelines.create,
        )


class AsyncPluginExecutionPipelinesResourceWithRawResponse:
    def __init__(self, plugin_execution_pipelines: AsyncPluginExecutionPipelinesResource) -> None:
        self._plugin_execution_pipelines = plugin_execution_pipelines

        self.create = async_to_raw_response_wrapper(
            plugin_execution_pipelines.create,
        )


class PluginExecutionPipelinesResourceWithStreamingResponse:
    def __init__(self, plugin_execution_pipelines: PluginExecutionPipelinesResource) -> None:
        self._plugin_execution_pipelines = plugin_execution_pipelines

        self.create = to_streamed_response_wrapper(
            plugin_execution_pipelines.create,
        )


class AsyncPluginExecutionPipelinesResourceWithStreamingResponse:
    def __init__(self, plugin_execution_pipelines: AsyncPluginExecutionPipelinesResource) -> None:
        self._plugin_execution_pipelines = plugin_execution_pipelines

        self.create = async_to_streamed_response_wrapper(
            plugin_execution_pipelines.create,
        )
