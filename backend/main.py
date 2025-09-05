from typing import Annotated

from dotenv import load_dotenv
import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

# 添加系统目录
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.api.deps import SessionDep, userDeps
from backend.app.crud.user import UserCRUD
from backend.agent.tools import image_edit
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from backend.app.core.config import settings
from PIL import Image

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import timezone, timedelta
from backend.logger import logger

beijing_tz = timezone(timedelta(hours=8))


# Import auth modules
from app.api.routes.auth import router as auth_router

# 1. 加载环境变量
load_dotenv(".env")
# 创建调度器实例
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        UserCRUD.reset_users_score,
        trigger=CronTrigger.from_crontab("0 0 * * *", timezone=beijing_tz),
        id="reset_users_score",
        name="Reset Users score",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


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
    db: SessionDep,
    user: userDeps,
    prompt: str = Form(...),
    file: UploadFile = File(...),
):
    """
    接收图片和指令，通过 Agent 处理，并返回图片base64。
    """
    logger.info(f"当前用户信息{user}")
    if user.score < 10:
        raise HTTPException(status_code=400, detail="积分不足")

    image_bytes = await file.read()
    # 保存到本地的临时文件
    image_path = f"temp_{file.filename}"
    file_path = os.path.join(UPLOAD_DIRECTORY, image_path)
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    img = Image.open(file_path)
    width, height = img.size
    img.close()

    image_url = f"{settings.HOST}/images/{image_path}"
    # 将width、height按比例缩放到小于等于1024
    max_size = 1664
    if width > max_size or height > max_size:
        ratio = min(max_size / width, max_size / height)
        width = int(width * ratio)
        height = int(height * ratio)

    image_data = await image_edit(image_url, prompt, f"{width}x{height}")
    os.remove(file_path)
    UserCRUD.update_user_score(db, user.id, -10)
    return {"image": image_data}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
