# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.



from .._models import BaseModel

__all__ = ["InfoRetrieveResponse"]


class InfoRetrieveResponse(BaseModel):
    end_time: str

    message: str

    start_time: str

    time_taken_ms: int

    time_taken_seconds: int

    version: str
