# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["FunctionProviderRequestRetrieveParams"]


class FunctionProviderRequestRetrieveParams(TypedDict, total=False):
    function_provider_name: Required[str]

    openplugin_manifest_url: Required[str]
