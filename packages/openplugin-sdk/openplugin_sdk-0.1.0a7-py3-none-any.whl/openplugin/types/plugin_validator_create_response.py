# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.



from .._models import BaseModel

__all__ = ["PluginValidatorCreateResponse"]


class PluginValidatorCreateResponse(BaseModel):
    message: str

    plugin_name: str
