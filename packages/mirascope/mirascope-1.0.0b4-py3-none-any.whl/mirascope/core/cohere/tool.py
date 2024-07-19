"""The `CohereTool` class for easy tool usage with Cohere LLM calls."""

from __future__ import annotations

from cohere.types import Tool, ToolCall, ToolParameterDefinitionsValue
from pydantic import SkipValidation
from pydantic.json_schema import SkipJsonSchema

from ..base import BaseTool


class CohereTool(BaseTool):
    """A class for defining tools for Cohere LLM calls."""

    tool_call: SkipJsonSchema[SkipValidation[ToolCall]]

    @classmethod
    def tool_schema(cls) -> Tool:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined."""
        model_schema = cls.model_json_schema()
        model_schema.pop("title", None)
        model_schema.pop("description", None)
        parameter_definitions = None
        if "parameters" in model_schema:
            if "$defs" in model_schema["parameters"]:
                raise ValueError(
                    "Unfortunately Cohere's chat API cannot handle nested structures "
                    "with $defs."
                )
            parameter_definitions = {
                prop: ToolParameterDefinitionsValue(
                    description=prop_schema["description"]
                    if "description" in prop_schema
                    else None,
                    type=prop_schema["type"],
                    required="required" in model_schema["parameters"]
                    and prop in model_schema["parameters"]["required"],
                )
                for prop, prop_schema in model_schema["parameters"][
                    "properties"
                ].items()
            }
        return Tool(
            name=cls._name(),
            description=cls._description(),
            parameter_definitions=parameter_definitions,
        )

    @classmethod
    def from_tool_call(cls, tool_call: ToolCall) -> CohereTool:
        """Constructs an `CohereTool` instance from a `tool_call`."""
        model_json = tool_call.parameters
        model_json["tool_call"] = tool_call.model_dump()
        return cls.model_validate(model_json)
