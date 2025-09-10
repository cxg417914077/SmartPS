from fastapi import APIRouter, Request
from pydantic import EmailStr, Field

from backend.app.crud.user import crud_user
from backend.app.api.deps import SessionDep, userDeps
from backend.app.models.user import User
from backend.app.utils.jwt_token import generate_jwt_token
from pydantic import BaseModel
from backend.app.utils.wechat import WeChatService

router = APIRouter()


class CaptchaVerification(BaseModel):
    email: EmailStr
    captchaToken: str


class EmailRequest(BaseModel):
    email: EmailStr


class UserLoginResponseData(BaseModel):
    token: str = Field(description="token放在 header authorization,需要拼接Bearer ")


class UserLoginResponseBody(BaseModel):
    data: UserLoginResponseData


class UserLoginByPhoneRequestBody(BaseModel):
    phone: str = Field(description="手机号")


class GetPhoneResponseData(BaseModel):
    phone: str = Field(description="手机号")


class GetPhoneResponseBody(BaseModel):
    data: GetPhoneResponseData


class GetPhoneByCodeRequestBody(BaseModel):
    code: str = Field(description="获取手机号的code")


class UserInfo(BaseModel):
    data: User


@router.post("/getPhoneByCode", response_model=GetPhoneResponseBody, summary="code换取手机号")
async def get_phone_by_code(request_body: GetPhoneByCodeRequestBody):
    phone = await WeChatService.get_phone_number(request_body.code)
    return {"data": {"phone": phone}}


@router.post("/loginByPhone", response_model=UserLoginResponseBody, summary="手机号登录")
async def login_by_phone(request_body: UserLoginByPhoneRequestBody, session: SessionDep):
    user = await crud_user.get_by(session, phone=request_body.phone)
    if not user:
        user = await crud_user.create(session, phone=request_body.phone)
    token = generate_jwt_token({"id": user.id, "phone": user.phone})
    return {"data": {"token": token}}


@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def me(user: userDeps, session: SessionDep):
    """
    Get current user info
    """
    user = await crud_user.get(session, user.id)
    return {"data": user}