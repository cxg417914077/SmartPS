import base64
from dotenv import load_dotenv
import sys
import os
from pathlib import Path

from backend.agent.tools import image_edit

# 添加系统目录
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


# Import auth modules
from app.api.routes.auth import router as auth_router
from backend.agent.agent import agent

# 1. 加载环境变量
load_dotenv(".env")

app = FastAPI()

# 定义存储上传图片的目录
UPLOAD_DIRECTORY = "uploaded_images"
Path(UPLOAD_DIRECTORY).mkdir(exist_ok=True)  # 如果目录不存在则创建

# Include auth routes
app.include_router(auth_router)

# 3. CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/images/{filename}")
async def get_image(filename: str):
    """
    通过文件名获取图片
    """
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="图片未找到")
    return FileResponse(file_path)


# --- API 路由 ---
# 修改接口以接收文件和表单数据
@app.post("/agent/image_process")
async def image_process_agent(
    prompt: str = Form(...),
    file: UploadFile = File(...)
):
    """
    接收图片和指令，通过 Agent 处理，并返回图片base64。
    """
    image_bytes = await file.read()
    # 保存到本地的临时文件
    image_path = f"temp_{file.filename}"
    file_path = os.path.join(UPLOAD_DIRECTORY, image_path)
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    image_data = image_edit(file_path, prompt)
    os.remove(file_path)

    return {"image": image_data}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
