"""
AI Studio Agent 业务对象（BO）

定义 Agent 响应相关的类型。
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ResponseChunkType(Enum):
    """Agent 响应块类型枚举"""
    TEXT = "text"
    THINKING = "thinking"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    SYSTEM = "system"
    RESULT = "result"


@dataclass
class ResponseChunk:
    """Agent 响应块数据类"""
    type: ResponseChunkType
    content: Any
    metadata: Optional[Dict[str, Any]] = None


class ChatStreamChunkType(str, Enum):
    """流式响应块类型枚举（对外 API）"""
    TEXT = "text"
    THINKING = "thinking"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    SYSTEM = "system"
    RESULT = "result"
    ERROR = "error"


class ChatStreamChunk(BaseModel):
    """流式聊天响应块（对外 API）"""
    type: ChatStreamChunkType = Field(description="响应块类型")
    content: Any = Field(description="响应内容")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


# ResponseChunkType 到 ChatStreamChunkType 的映射
CHUNK_TYPE_MAP: Dict[ResponseChunkType, ChatStreamChunkType] = {
    ResponseChunkType.TEXT: ChatStreamChunkType.TEXT,
    ResponseChunkType.THINKING: ChatStreamChunkType.THINKING,
    ResponseChunkType.TOOL_USE: ChatStreamChunkType.TOOL_USE,
    ResponseChunkType.TOOL_RESULT: ChatStreamChunkType.TOOL_RESULT,
    ResponseChunkType.SYSTEM: ChatStreamChunkType.SYSTEM,
    ResponseChunkType.RESULT: ChatStreamChunkType.RESULT,
}
