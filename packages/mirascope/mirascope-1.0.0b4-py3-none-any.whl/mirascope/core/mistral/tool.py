"""The `MistralTool` class for easy tool usage with Mistral LLM calls."""

from __future__ import annotations

from typing import Any

import jiter
from mistralai.models.chat_completion import ToolCall

from ..base import BaseTool


class MistralTool(BaseTool):
    """A class for defining tools for Mistral LLM calls."""

    tool_call: ToolCall

    @classmethod
    def tool_schema(cls) -> dict[str, Any]:
        """Constructs a JSON Schema tool schema from the `BaseModel` schema defined."""
        model_schema = cls.model_json_schema()
        model_schema.pop("title", None)
        model_schema.pop("description", None)

        fn: dict[str, Any] = {"name": cls._name(), "description": cls._description()}
        if model_schema["properties"]:
            fn["parameters"] = model_schema

        return {"function": fn, "type": "function"}

    @classmethod
    def from_tool_call(cls, tool_call: ToolCall) -> MistralTool:
        """Constructs an `MistralTool` instance from a `tool_call`."""
        model_json = jiter.from_json(tool_call.function.arguments.encode())
        model_json["tool_call"] = tool_call.model_dump()
        return cls.model_validate(model_json)
