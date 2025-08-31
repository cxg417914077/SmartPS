import base64

import requests
import time
import json
from PIL import Image
from io import BytesIO
from backend.app.core.config import settings


def image_edit(image_url: str, prompt: str):
    common_headers = {
        "Authorization": f"Bearer {settings.MODELSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    # 读取图片获取分辨率
    image = Image.open(image_url)
    width, height = image.size
    image.close()

    response = requests.post(
        f"{settings.MODELSCOPE_API_URL}v1/images/generations",
        headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
        data=json.dumps({
            "model": "Qwen/Qwen-Image-Edit",
            "prompt": prompt,
            "image_url": image_url,
            "size": f"{width}x{height}"
        }, ensure_ascii=False).encode('utf-8')
    )

    # 检查响应状态码并处理错误
    if response.status_code == 401:
        raise ValueError("Unauthorized: Invalid ModelScope API key.")
    response.raise_for_status()

    task_id = response.json()["task_id"]
    print(f"Task ID: {task_id}")

    while True:
        result = requests.get(
            f"{settings.MODELSCOPE_API_URL}v1/tasks/{task_id}",
            headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
        )
        result.raise_for_status()
        data = result.json()

        if data["task_status"] == "SUCCEED":
            image = Image.open(BytesIO(requests.get(data["output_images"][0]).content))
            buffered = BytesIO()
            image.save(buffered, format=image.format)
            image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return image_data
        elif data["task_status"] == "FAILED":
            raise Exception("Image Generation Failed.")

        time.sleep(5)
