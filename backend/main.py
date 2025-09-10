import sys
import os
import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 添加系统目录
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.core.worker import image_processing_worker
from backend.app.crud.user import crud_user
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import timezone, timedelta

from backend.logger import logger

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
    # 启动后台任务
    worker_task = asyncio.create_task(image_processing_worker())

    scheduler.add_job(
        crud_user.reset_users_score,
        trigger=CronTrigger.from_crontab("0 0 * * *", timezone=beijing_tz),
        id="reset_users_score",
        name="Reset Users score",
        replace_existing=True,
    )
    scheduler.start()
    yield
    # 应用关闭时取消后台任务
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        logger.info("Worker task cancelled successfully.")
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(
        f'{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s'
    )
    return response


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
