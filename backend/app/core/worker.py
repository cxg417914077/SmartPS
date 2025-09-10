
import asyncio
import json
from backend.app.core.aio_redis import aio_redis_client
from backend.app.utils.qwen_image import qwen_client
from backend.app.crud.history import crud_history
from backend.app.core.db import AsyncSessionLocal
from backend.logger import logger

REDIS_QUEUE_KEY = "image_processing_queue"


async def image_processing_worker():
    logger.info("Starting image processing worker...")
    while True:
        try:
            # 使用 brpop 进行阻塞式等待，0表示无限期等待
            _, task_data = await aio_redis_client.brpop(REDIS_QUEUE_KEY)
            task = json.loads(task_data)
            logger.info(f"Processing task: {task['job_id']}")

            async with AsyncSessionLocal() as session:
                # 执行核心业务逻辑
                # 1. 写入历史记录
                history = await crud_history.create(
                    session,
                    user_id=task["user_id"],
                    job_id=task["job_id"],
                    task_id="",
                    prompt=task["prompt"],
                    upload_image=task["image_base64"],
                )

                # 2. 调用外部API
                task_id = await qwen_client.generate(
                    task["prompt"], task["image_url"], task["image_size"]
                )

                # 3. 获取结果并更新历史记录
                await qwen_client.result(task_id, history.id)

                logger.info(f"Task {task['task_id']} completed successfully.")

        except asyncio.CancelledError:
            logger.info("Image processing worker is shutting down.")
            break
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            # 可以在这里添加错误处理逻辑，例如将失败的任务移至死信队列
            await asyncio.sleep(1) # 避免在持续失败时快速消耗CPU
