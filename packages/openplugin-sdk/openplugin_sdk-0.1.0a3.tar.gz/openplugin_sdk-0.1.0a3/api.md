# API

Types:

```python
from openplugin.types import APIListResponse
```

Methods:

- <code title="get /api/">client.api.<a href="./src/openplugin/resources/api/api.py">list</a>() -> <a href="./src/openplugin/types/api_list_response.py">object</a></code>

## Info

Types:

```python
from openplugin.types.api import InfoRetrieveResponse
```

Methods:

- <code title="get /api/info">client.api.info.<a href="./src/openplugin/resources/api/info.py">retrieve</a>() -> <a href="./src/openplugin/types/api/info_retrieve_response.py">object</a></code>

## PluginExecutionPipelines

Types:

```python
from openplugin.types.api import PluginExecutionPipelineCreateResponse
```

Methods:

- <code title="post /api/plugin-execution-pipeline">client.api.plugin_execution_pipelines.<a href="./src/openplugin/resources/api/plugin_execution_pipelines.py">create</a>(\*\*<a href="src/openplugin/types/api/plugin_execution_pipeline_create_params.py">params</a>) -> <a href="./src/openplugin/types/api/plugin_execution_pipeline_create_response.py">object</a></code>

## Processors

Types:

```python
from openplugin.types.api import ProcessorListResponse
```

Methods:

- <code title="get /api/processors">client.api.processors.<a href="./src/openplugin/resources/api/processors.py">list</a>() -> <a href="./src/openplugin/types/api/processor_list_response.py">object</a></code>

## FunctionProviders

Types:

```python
from openplugin.types.api import FunctionProviderListResponse
```

Methods:

- <code title="get /api/function-providers">client.api.function_providers.<a href="./src/openplugin/resources/api/function_providers.py">list</a>(\*\*<a href="src/openplugin/types/api/function_provider_list_params.py">params</a>) -> <a href="./src/openplugin/types/api/function_provider_list_response.py">object</a></code>

## FunctionProviderRequests

Types:

```python
from openplugin.types.api import FunctionProviderRequestRetrieveResponse
```

Methods:

- <code title="get /api/function-provider-request">client.api.function_provider_requests.<a href="./src/openplugin/resources/api/function_provider_requests.py">retrieve</a>(\*\*<a href="src/openplugin/types/api/function_provider_request_retrieve_params.py">params</a>) -> <a href="./src/openplugin/types/api/function_provider_request_retrieve_response.py">object</a></code>

## RunFunctionProviders

Types:

```python
from openplugin.types.api import RunFunctionProviderCreateResponse
```

Methods:

- <code title="post /api/run-function-provider">client.api.run_function_providers.<a href="./src/openplugin/resources/api/run_function_providers.py">create</a>(\*\*<a href="src/openplugin/types/api/run_function_provider_create_params.py">params</a>) -> <a href="./src/openplugin/types/api/run_function_provider_create_response.py">object</a></code>

# PluginValidators

Types:

```python
from openplugin.types import PluginValidatorCreateResponse
```

Methods:

- <code title="post /api/plugin-validator">client.plugin_validators.<a href="./src/openplugin/resources/plugin_validators.py">create</a>(\*\*<a href="src/openplugin/types/plugin_validator_create_params.py">params</a>) -> <a href="./src/openplugin/types/plugin_validator_create_response.py">object</a></code>

# OpenAPIParsers

Types:

```python
from openplugin.types import OpenAPIParserRetrieveResponse
```

Methods:

- <code title="get /api/openapi-parser">client.openapi_parsers.<a href="./src/openplugin/resources/openapi_parsers.py">retrieve</a>() -> <a href="./src/openplugin/types/openapi_parser_retrieve_response.py">object</a></code>

# OpenAPIParamParsers

Types:

```python
from openplugin.types import OpenAPIParamParserRetrieveResponse
```

Methods:

- <code title="get /api/openapi-param-parser">client.openapi_param_parsers.<a href="./src/openplugin/resources/openapi_param_parsers.py">retrieve</a>(\*\*<a href="src/openplugin/types/openapi_param_parser_retrieve_params.py">params</a>) -> <a href="./src/openplugin/types/openapi_param_parser_retrieve_response.py">object</a></code>
