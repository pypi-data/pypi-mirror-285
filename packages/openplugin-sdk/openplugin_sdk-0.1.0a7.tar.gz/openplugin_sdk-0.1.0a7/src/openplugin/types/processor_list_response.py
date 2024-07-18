# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = [
    "ProcessorListResponse",
    "ProcessorListResponseItem",
    "ProcessorListResponseItemImplementation",
    "ProcessorListResponseItemImplementationMetadata",
]


class ProcessorListResponseItemImplementationMetadata(BaseModel):
    key: str

    long_form: bool

    required: bool

    type: str

    default_value: Optional[str] = None

    is_user_provided: Optional[bool] = None


class ProcessorListResponseItemImplementation(BaseModel):
    metadata: List[ProcessorListResponseItemImplementationMetadata]

    name: str

    processor_implementation_type: str


class ProcessorListResponseItem(BaseModel):
    description: str

    implementations: List[ProcessorListResponseItemImplementation]

    input_port: str

    output_port: str

    processor_name: str

    processor_type: str


ProcessorListResponse = List[ProcessorListResponseItem]
