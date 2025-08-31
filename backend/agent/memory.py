from typing import List
from backend.agent.schema import ChatMessage

class ShortTermMemory:
    """管理对话的短期记忆（聊天历史）。"""
    def __init__(self):
        self.history: List[ChatMessage] = []

    def add_message(self, role: str, content: str):
        self.history.append(ChatMessage(role=role, content=content))

    def get_history_str(self) -> str:
        if not self.history:
            return "没有对话历史。"
        return "\n".join([f"{msg.role}: {msg.content}" for msg in self.history])


class LongTermMemory_RAG:
    """
    长期记忆组件，通过RAG从外部知识库检索信息。
    引用指南章节: 3.1 检索增强生成（RAG）
    """
    def retrieve(self, query: str) -> str:
        """
        在生产环境中，这里会连接到一个向量数据库（如ChromaDB, Pinecone）
        并执行语义搜索来检索相关文档。
        """
        print(f"--- 正在从长期记忆中检索'{query}'的相关信息... ---")
        # 这是一个模拟的RAG检索结果
        return "根据知识库：上下文工程超越了提示词工程，它系统化地管理所有输入信息，包括指令、记忆和工具。"

