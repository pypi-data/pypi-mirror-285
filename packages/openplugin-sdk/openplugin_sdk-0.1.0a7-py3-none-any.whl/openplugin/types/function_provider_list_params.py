# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["FunctionProviderListParams"]


class FunctionProviderListParams(TypedDict, total=False):
    anthropic_api_key: Optional[str]

    cohere_api_key: Optional[str]

    fireworks_api_key: Optional[str]

    gemini_api_key: Optional[str]

    groq_api_key: Optional[str]

    mistral_api_key: Optional[str]

    openai_api_key: Optional[str]

    openplugin_manifest_url: Optional[str]

    together_api_key: Optional[str]

    type: str
