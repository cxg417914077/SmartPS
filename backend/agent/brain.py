import asyncio
import ollama
from fastmcp import Client


async def get_tools():
    mcp_configs = {
        "imagetool": {
            "command": "python",
            "args": ["mcp/server.py"]
        },
    }

    tools, cleanup = await convert_mcp_to_langchain_tools(
        mcp_configs,
    )
    return tools


class Brain:
    """
    大脑组件，负责所有与LLM的交互和推理。
    """
    def __init__(self):
        self.model = ChatOllama(
            model="modelscope.cn/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF:UD-TQ1_0",
            temperature=0
        )

    async def think(self, context: str) -> str:
        """
        接收完整的上下文，并让LLM进行思考和推理。
        """
        print("\n--- 大脑正在思考... ---\n")
        response = await self.model.ainvoke(context)
        try:
            return response.content
        except Exception as e:
            print(f"LLM响应解析失败: {e}")
            print(f"原始响应: {response.prompt_feedback}")
            return "无法生成有效响应。"