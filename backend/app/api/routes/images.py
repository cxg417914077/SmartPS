import os
from typing import Optional
from pydantic import BaseModel
from backend.app.core.config import settings

from fastapi import HTTPException, APIRouter, BackgroundTasks
from fastapi.responses import  FileResponse

from backend.app.crud.history import crud_history
from backend.app.crud.user import crud_user
from backend.app.models.user import History
from backend.app.utils.image_tools import save_image_from_base64, scale_image_dimensions
from backend.main import UPLOAD_DIRECTORY
from backend.app.api.deps import SessionDep, userDeps
from backend.logger import logger
from backend.app.utils.qwen_image import qwen_client


router = APIRouter()


class ImageProcessRequest(BaseModel):
    prompt: str
    image_base64: Optional[str]


class ImageProcessResponse(BaseModel):
    task_id: str


@router.get("/images/{filename}")
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
@router.post("/agent/image_process_wx", response_model=ImageProcessResponse)
async def image_process_agent(
    user: userDeps,
    session: SessionDep,
    image_request: ImageProcessRequest,
    background_tasks: BackgroundTasks,
):
    user = await crud_user.get(session, user.id)
    logger.info(f"当前用户信息{user}")
    if user.score < 10:
        raise HTTPException(status_code=400, detail="积分不足")

    image_info = save_image_from_base64(image_request.image_base64, UPLOAD_DIRECTORY)
    image_url = f"{settings.HOST}/images/{os.path.basename(image_info.file_name)}"
    image_size = scale_image_dimensions(image_info.width, image_info.height)

    task_id = await qwen_client.generate(image_request.prompt, image_url, image_size)
    # 写入历史记录
    history = await crud_history.create(
        session,
        user_id=user.id,
        task_id=task_id,
        prompt=image_request.prompt,
        upload_image=image_request.image_base64,
    )
    # 后台任务更新结果
    background_tasks.add_task(qwen_client.result, task_id, history.id)
    return {"task_id": task_id}


class ImageResult(BaseModel):
    data: History


@router.get("/agent/image_process_wx/{task_id}", response_model=ImageResult)
async def get_image_process_result(
        task_id: str,
        session: SessionDep
):
    history = await crud_history.get_by(session, task_id=task_id)
    return {"data": history}


# 历史记录接口
@router.get("/agent/history", response_model=list[History])
async def get_history(
        user: userDeps,
        session: SessionDep,
):
    """
    获取历史记录
    """
    return await crud_history.get_multi_by(session, user_id=user.id)
