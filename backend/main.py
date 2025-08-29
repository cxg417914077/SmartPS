from contextlib import asynccontextmanager
import json
import base64
from io import BytesIO
from dotenv import load_dotenv
import sys
import os
# 添加系统目录
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from PIL import Image

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_mcp_tools.langchain_mcp_tools import convert_mcp_to_langchain_tools

# Import auth modules
from app.api.routes.auth import router as auth_router

# 1. 加载环境变量
load_dotenv(".env")


mcp_configs = {
    "imagetool": {
        "url": "http://localhost:8000/mcp",
        "trabsport": "http",
    }
}


@asynccontextmanager
async def make_agent():
    tools, cleanup = await convert_mcp_to_langchain_tools(
            mcp_configs,
        )

    # --- LangChain Agent 设置 ---
    llm = ChatOllama(model="modelscope.cn/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF:UD-TQ1_0", temperature=0)
    system_prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, system_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    yield agent_executor
    await cleanup()




@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_instance
    # 应用启动时执行
    async with make_agent() as agent:
        agent_instance = agent
        yield
    # 应用关闭时执行清理工作
    agent_instance = None

# 使用 lifespan 初始化 FastAPI 应用
app = FastAPI(lifespan=lifespan)

# Include auth routes
app.include_router(auth_router)

# --- 图片处理工具定义 ---
# 使用 @tool 装饰器可以非常方便地将一个函数变成 LangChain 工具
@tool
def convert_image_to_grayscale(image_bytes: bytes) -> bytes:
    """
    Receives an image as bytes, converts it to grayscale, and returns the processed image as bytes.
    Use this tool when the user asks to make an image grayscale or black and white.
    """
    image = Image.open(BytesIO(image_bytes))
    grayscale_image = image.convert("L")
    output_buffer = BytesIO()
    grayscale_image.save(output_buffer, format=image.format or "PNG")
    return output_buffer.getvalue()

# 3. CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API 路由 ---
# 修改接口以接收文件和表单数据
@app.post("/agent/image_process")
async def image_process_agent(
    prompt: str = Form(...),
    file: UploadFile = File(...)
):
    """
    接收图片和指令，通过 Agent 处理，并流式返回结果。
    """
    image_bytes = await file.read()
    # 保存到本地的临时文件
    image_path = f"temp_{file.filename}"
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    # Agent 的输入现在包含文本和图片
    agent_input = {
        "input": f"{prompt},image_path:{image_path}",
    }

    async def event_generator():
        try:
            # astream_log 仍然是我们的核心
            async for chunk in agent_instance.astream_log(agent_input):
                for op in chunk.ops:
                    path = op["path"]
                    # 同样，流式返回思考过程
                    if path.endswith("/logs/action/streamed_output_str"):
                        yield json.dumps({"type": "thought", "content": op["value"]})
                    
                    # 当工具执行完成后，它的输出在这里
                    elif path.endswith("/logs/observation/streamed_output_str"):
                        # 工具的输出可能是字符串，也可能是我们返回的图片字节
                        # 这里我们只流式传输文本观察结果
                         yield json.dumps({"type": "observation", "content": op["value"]})

                    # 当最终答案生成时
                    elif path.endswith("/logs/final_output"):
                        # 最终输出对象里包含了我们的图片字节
                        final_output = op.get("value", {}).get("output")
                        
                        # 检查最终输出是否是我们的图片工具返回的结果
                        # 这里我们假设如果 Agent 成功调用工具，最终输出就是图片字节
                        # 在更复杂的场景中，您可能需要更精细的逻辑来区分文本和图片输出
                        if isinstance(final_output, bytes):
                            # 如果是图片字节，进行Base64编码后发送
                            encoded_image = base64.b64encode(final_output).decode('utf-8')
                            yield json.dumps({
                                "type": "final_image", 
                                "content": encoded_image,
                                "format": file.content_type
                            })
                        else:
                            # 如果是文本，则正常发送
                            yield json.dumps({"type": "final_output", "content": final_output})

        except Exception as e:
            print(f"An error occurred: {e}")
            yield json.dumps({"type": "error", "content": str(e)})
        finally:
            yield json.dumps({"type": "end"})

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
