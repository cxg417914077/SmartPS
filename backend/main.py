import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 添加系统目录
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.crud.user import crud_user
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import timezone, timedelta

beijing_tz = timezone(timedelta(hours=8))

# 1. 加载环境变量
load_dotenv(".env")
# 创建调度器实例
scheduler = AsyncIOScheduler()


def load_routes():
    from backend.app.api.routes import auth, images
    app.include_router(auth.router)
    app.include_router(images.router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_routes()
    scheduler.add_job(
        crud_user.reset_users_score,
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

# Include routes

# 3. CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
