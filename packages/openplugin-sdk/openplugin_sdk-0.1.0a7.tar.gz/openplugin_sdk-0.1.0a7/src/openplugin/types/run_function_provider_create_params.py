# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["RunFunctionProviderCreateParams", "Config"]


class RunFunctionProviderCreateParams(TypedDict, total=False):
    config: Required[Config]
    """Represents the API configuration for a plugin."""

    function_provider_name: Required[str]

    openplugin_manifest_url: Required[str]

    prompt: Required[str]

    function_json: Optional[object]


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
