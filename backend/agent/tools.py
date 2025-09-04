import base64
import asyncio
import aiohttp
from PIL import Image
from io import BytesIO
from backend.app.core.config import settings


async def image_edit(image_url: str, prompt: str, image_size: str):
    common_headers = {
        "Authorization": f"Bearer {settings.MODELSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # 创建aiohttp客户端会话
    async with aiohttp.ClientSession() as session:
        # 发起初始请求
        async with session.post(
            f"{settings.MODELSCOPE_API_URL}v1/images/generations",
            headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
            json={
                "model": "Qwen/Qwen-Image-Edit",
                "prompt": prompt,
                "image_url": image_url,
                "size": image_size
            }
        ) as response:
            # 检查响应状态码并处理错误
            if response.status == 401:
                raise ValueError("Unauthorized: Invalid ModelScope API key.")
            response.raise_for_status()
            
            response_data = await response.json()
            task_id = response_data["task_id"]
            print(f"Task ID: {task_id}")

        # 轮询任务状态
        while True:
            async with session.get(
                f"{settings.MODELSCOPE_API_URL}v1/tasks/{task_id}",
                headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
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
                        return image_data
                elif data["task_status"] == "FAILED":
                    raise Exception("Image Generation Failed.")

            # 等待5秒后继续轮询
            await asyncio.sleep(5)