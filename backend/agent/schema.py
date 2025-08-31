from pydantic import BaseModel, Field
from typing import Dict, Any


class ToolCall(BaseModel):
    """
    一个模型，用于表示LLM决定进行的工具调用。
    引用指南章节: 4.2 因素4：工具即结构化输出
    """
    tool_name: str = Field(..., description="要调用的工具的名称。")
    parameters: Dict[str, Any] = Field(..., description="调用工具所需的参数。")


class ChatMessage(BaseModel):
    """表示对话历史中的一条消息。"""
    role: str  # "user", "assistant", "system", "tool"
    content: str