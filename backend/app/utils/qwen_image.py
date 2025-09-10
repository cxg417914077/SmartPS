import asyncio
import base64
from io import BytesIO

import aiohttp
from PIL import Image

from backend.app.core.config import settings
from backend.app.crud.history import crud_history
from backend.app.utils.image_tools import ImageSize
from backend.app.core.db import AsyncSessionLocal
from backend.logger import logger


class QwenClient:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.headers = {
        "Authorization": f"Bearer {settings.MODELSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }

    async def generate(self, prompt: str, image_url: str, image_size: ImageSize) -> str:
        image_size = ImageSize.model_validate(image_size)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{settings.MODELSCOPE_API_URL}v1/images/generations",
                    headers={**self.headers, "X-ModelScope-Async-Mode": "true"},
                    json={
                        "model": "Qwen/Qwen-Image-Edit",
                        "prompt": prompt,
                        "image_url": image_url,
                        "size": f"{image_size.width}x{image_size.height}"
                    }
            ) as response:
                # 检查响应状态码并处理错误
                if response.status == 401:
                    raise ValueError("Unauthorized: Invalid ModelScope API key.")
                response.raise_for_status()

                response_data = await response.json()
                task_id = response_data["task_id"]
                return task_id

    async def result(self, task_id: str, _id: int) -> str:
        async with AsyncSessionLocal() as db:
            async with aiohttp.ClientSession() as session:
                while True:
                    async with session.get(
                            f"{settings.MODELSCOPE_API_URL}v1/tasks/{task_id}",
                            headers={**self.headers, "X-ModelScope-Task-Type": "image_generation"},
                    ) as result:
                        result.raise_for_status()
                        data = await result.json()

                        if data["task_status"] == "SUCCEED":
                            # 获取生成的图片
                            async with session.get(data["output_images"][0]) as image_response:
                                image_response.raise_for_status()
                                image_content = await image_response.read()
                                image = Image.open(BytesIO(image_content))
                                buffered = BytesIO()
                                image.save(buffered, format=image.format)
                                image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
                                await crud_history.update(db, _id, image_data=image_data, status=data["task_status"])
                                return image_data
                        else:
                            await crud_history.update(db, _id, status=data["task_status"])

                    # 等待5秒后继续轮询
                    await asyncio.sleep(5)


qwen_client = QwenClient()