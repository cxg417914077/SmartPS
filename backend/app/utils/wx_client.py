import asyncio
import json

from aiohttp import ClientSession, ClientTimeout
from pydantic import BaseModel

from backend.logger import logger
from backend.app.core.config import settings


class WeChatAccessToken(BaseModel):
    access_token: str
    expires_in: int


class WeChatUserAccess(BaseModel):
    openId: str
    sessionKey: str


class _WxClient:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret

    @staticmethod
    async def request_sth(method, url, **kwargs):
        try_times = 3
        while try_times > 0:
            try:
                async with ClientSession(timeout=ClientTimeout(total=3)) as sess:
                    async with sess.request(method, url, **kwargs) as resp:
                        assert resp.status == 200, "url invalid"
                        return await resp.json()
            except Exception as e:
                try_times -= 1
                if try_times <= 0:
                    print(f"request failed: {e}")
                    return b""
                await asyncio.sleep(0.5)

    async def get_sth(self, url):
        return await self.request_sth("GET", url)

    async def post_sth(self, url, json_data):
        return await self.request_sth("POST", url, json=json_data)

    async def get_access_token(self) -> WeChatAccessToken | None:
        """
        https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html
        """
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        resp = await self.get_sth(url)
        try:
            return WeChatAccessToken.model_validate(resp)
        except Exception as e:
            logger.exception(f"get access token, r: {resp} failed: {e}")

    async def get_phone_number(self, code, access_token):
        """
        https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-info/phone-number/getPhoneNumber.html
        """
        url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}"
        try:
            resp = await self.post_sth(url, json_data={"code": code})
            assert resp["errcode"] == 0, resp["errmsg"]
            return resp["phone_info"]["purePhoneNumber"]
        except Exception as e:
            logger.exception(f"get phone number failed: {e}")
            raise ValueError(f"获取手机号失败: {e}")

    async def get_user_session(self, code) -> WeChatUserAccess:
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid={self.app_id}&secret={self.app_secret}&js_code={code}&grant_type=authorization_code"
        try:
            resp = await self.get_sth(url)
            print(resp)
            return WeChatUserAccess.model_validate(resp)
        except Exception as e:
            logger.exception(f"get user session failed: {e}")
            raise ValueError(f"获取用户session_key失败: {e}")

    async def get_user_info(self, open_id: str, access_token: str):
        url = f"https://api.weixin.qq.com/sns/userinfo?openid={open_id}&access_token={access_token}"
        try:
            resp = await self.get_sth(url)
            return json.loads(resp)
        except Exception as e:
            logger.exception(f"get user info failed: {e}")
            raise ValueError(f"获取用户信息失败: {e}")



WxClient = _WxClient(settings.WechatAppId, settings.WechatAppSecret)


if __name__ == '__main__':
    async def main():
        print(await WxClient.get_access_token())

    asyncio.run(main())