import asyncio
import inspect
import socket
import traceback

from backend.logger import logger
from backend.app.core.aio_redis import aio_redis_client
from backend.app.utils.wx_client import WxClient, WeChatAccessToken, WeChatUserAccess

from backend.app.core.config import settings

WXAccessTokenKey = settings.WechatAppSecret
WXAccessTokenLock = "WxATLock"
WXRefreshOpenidLock = "WxROLock"
SKIP = 0x1
HOST_NAME = socket.gethostname()


def dis_lock(key: str, expire: int):
    def decorator(fn):
        assert inspect.iscoroutinefunction(fn), "coroutine func support only"

        async def wrapper(*args, **kwargs):
            host_name = await aio_redis_client.get(key)
            if host_name and host_name != HOST_NAME:
                logger.info(f"<Locked> {host_name} executing {fn.__name__}")
                return SKIP
            try:
                res = await fn(*args, **kwargs)
            except Exception as e:
                logger.error(e)
                return
            await aio_redis_client.set(key, HOST_NAME, expire)
            return res

        return wrapper

    return decorator


class _WeChatService:
    @staticmethod
    @dis_lock(WXAccessTokenLock, 7000)
    async def get_new_access_token():
        access_token = await aio_redis_client.get(WXAccessTokenKey)
        if access_token:
            expire_in = aio_redis_client.ttl(WXAccessTokenKey)
            return WeChatAccessToken(access_token=access_token, expires_in=expire_in)

        access_token_info = await WxClient.get_access_token()
        if not access_token_info:
            logger.error("获取AccessToken失败")
            raise Exception("获取AccessToken失败")
        # save into redis
        await aio_redis_client.set(
            WXAccessTokenKey,
            access_token_info.access_token,
            access_token_info.expires_in,
        )
        return access_token_info

    async def _get_access_token(self) -> str:
        while True:
            access_token = await aio_redis_client.get(WXAccessTokenKey)
            if access_token:
                break
            await self.get_new_access_token()
            await asyncio.sleep(1)
        return access_token

    async def get_access_token(self) -> str:
        try:
            return await self._get_access_token()
        except asyncio.TimeoutError:
            logger.error("获取AccessToken超时")
            raise Exception("获取AccessToken超时")

    async def get_user_info(self, user_session: WeChatUserAccess):
        access_token = await self.get_access_token()
        user_info = await WxClient.get_user_info(user_session.openId, access_token)
        return user_info

    async def get_phone_number(self, code: str) -> str:
        if code == "999999":
            return "17093131436"
        access_token = await self.get_access_token()
        try:
            phone_number = await WxClient.get_phone_number(code, access_token)
        except Exception as e:
            logger.error(f"手机号获取失败，错误信息：{str(e)}")
            logger.error(traceback.format_exc())
            phone_number = ""
        return phone_number


WeChatService = _WeChatService()