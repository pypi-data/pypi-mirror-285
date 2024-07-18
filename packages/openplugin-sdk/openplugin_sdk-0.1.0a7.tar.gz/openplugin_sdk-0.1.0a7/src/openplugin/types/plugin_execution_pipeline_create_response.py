# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["PluginExecutionPipelineCreateResponse", "Metadata"]


class Metadata(BaseModel):
    function_provider_name: str

    output_module_names: str

    total_time_taken_ms: int

    total_time_taken_seconds: float

    cost: Optional[float] = None

    end_time: Optional[datetime] = None

    start_time: Optional[datetime] = None

    total_tokens_used: Optional[int] = None


class PluginExecutionPipelineCreateResponse(BaseModel):
    error: object

    metadata: Metadata

    trace: object

    response: Optional[object] = None
