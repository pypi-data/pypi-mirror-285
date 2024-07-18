# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["FunctionProviderListResponse", "FunctionProviderListResponseItem"]


class FunctionProviderListResponseItem(BaseModel):
    name: str

    required_auth_keys: List[object]

    type: str

    is_default: Optional[bool] = None

    is_supported: Optional[bool] = None


FunctionProviderListResponse = List[FunctionProviderListResponseItem]
