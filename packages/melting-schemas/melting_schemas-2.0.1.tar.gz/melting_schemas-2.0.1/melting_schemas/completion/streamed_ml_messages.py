from typing import Any, Literal

from pydantic import BaseModel


class ChatMLMessageChunk(BaseModel):
    id: Any
    delta: str


class ToolCallFunctionChunk(BaseModel):
    delta: str
    name: str | None = None


class ToolCallChunk(BaseModel):
    id: str
    tool_id: str
    type: Literal["function"]
    function: ToolCallFunctionChunk


class ToolMLMessageChunk(BaseModel):
    tool_id: str
    delta: str
    name: str
    role: Literal["tool"]
