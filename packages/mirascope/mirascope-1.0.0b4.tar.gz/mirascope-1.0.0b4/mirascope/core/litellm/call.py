"""The `litellm_call` decorator for functions as LLM calls."""

from ..base import call_factory
from ._utils import (
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from .call_params import LiteLLMCallParams
from .call_response import LiteLLMCallResponse
from .call_response_chunk import LiteLLMCallResponseChunk
from .dynamic_config import LiteLLMDynamicConfig
from .stream import LiteLLMStream
from .tool import LiteLLMTool

litellm_call = call_factory(
    TCallResponse=LiteLLMCallResponse,
    TCallResponseChunk=LiteLLMCallResponseChunk,
    TDynamicConfig=LiteLLMDynamicConfig,
    TToolType=LiteLLMTool,
    TStream=LiteLLMStream,
    TCallParams=LiteLLMCallParams,
    default_call_params=LiteLLMCallParams(),
    setup_call=setup_call,  # type: ignore
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
)
'''A decorator for calling the LiteLLM API with a typed function.

This decorator is used to wrap a typed function that calls the LiteLLM API. It parses
the docstring of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
@litellm_call(model="gpt-4o")
def recommend_book(genre: str):
    """Recommend a {genre} book."""

response = recommend_book("fantasy")
```

Args:
    model: The LiteLLM model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the LiteLLM API call.
    **call_params: The `LiteLLMCallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an LiteLLM API call.
'''
