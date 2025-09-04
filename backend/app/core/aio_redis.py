import redis.asyncio as redis
from backend.app.core.config import settings


def aio_redis_pool_init():
    # Redis client bound to pool of connections (auto-reconnecting).
    redis_client = redis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True)
    return redis_client


class RedisKeys(object):
    USER_TOKEN = "token:plat:{}:user:{}:token"  # loginPlatType, user_id
    USER_REFRESH_TOKEN = "token:plat:{}:user:{}:refresh_token"  # loginPlatType, user_id


aio_redis_client = aio_redis_pool_init()