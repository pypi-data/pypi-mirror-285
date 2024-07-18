# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["PluginExecutionPipelineCreateParams", "Config", "FunctionProviderInput"]


class PluginExecutionPipelineCreateParams(TypedDict, total=False):
    conversation: Required[Iterable[object]]

    header: Required[object]

    prompt: Required[str]

    auth_query_param: Optional[object]

    config: Optional[Config]
    """Represents the API configuration for a plugin."""

    enable_ui_form_controls: bool

    function_provider_input: Optional[FunctionProviderInput]

    openplugin_manifest_obj: Optional[object]

    openplugin_manifest_url: Optional[str]

    output_module_names: Optional[List[str]]

    run_all_output_modules: bool

    selected_operation: Optional[str]

    session_variables: Optional[str]


class Config(TypedDict, total=False):
    anthropic_api_key: Optional[str]

    aws_access_key_id: Optional[str]

    aws_region_name: Optional[str]

    aws_secret_access_key: Optional[str]

    azure_api_key: Optional[str]

    cohere_api_key: Optional[str]

    fireworks_api_key: Optional[str]

    gemini_api_key: Optional[str]

    google_palm_key: Optional[str]

    groq_api_key: Optional[str]

    mistral_api_key: Optional[str]

    openai_api_key: Optional[str]

    provider: str

    together_api_key: Optional[str]


class FunctionProviderInput(TypedDict, total=False):
    name: Required[str]
