import aiohttp
from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr

from backend.app.core.redis_tool import cache
from backend.app.models.base import MessageResponse, LoginResponse
from backend.app.models.user import UserLogin, UserRegister
from backend.app.crud.user import UserCRUD
from backend.app.api.deps import SessionDep
from backend.app.utils.email import send_email
from backend.app.utils.jwt_token import generate_jwt_token
from pydantic import BaseModel
from backend.app.core.config import settings


router = APIRouter()


class CaptchaVerification(BaseModel):
    email: EmailStr
    captchaToken: str


class EmailRequest(BaseModel):
    email: EmailStr

@router.post("/api/verify-captcha")
async def verify_captcha(request: CaptchaVerification) -> dict:
    """
    Captcha verification endpoint
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(settings.VERIFICATION_ENDPOINT, data={"secret": settings.RE_CAPTCHA_KEY, "response": request.captchaToken}) as response:
            response_data = await response.json()
            if response_data["success"]:
                return {"message": "人机验证通过。"}
            return {"message": "人机验证失败，请重试。"}


@router.post("/api/register", response_model=LoginResponse)
async def register(user_data: UserRegister, db: SessionDep):
    """
    User registration endpoint
    """
    # 检查邮箱验证码
    if not cache.verify_otp(user_data.email, user_data.code):
        return {"message": "验证码错误"}
    # 检查用户是否已存在
    existing_user = UserCRUD.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    try:
        user = UserCRUD.create_user(db, user_data)
        # 生成token
        token = generate_jwt_token({"user_id": user.id, "username": user.email})
        return {"message": "User registered successfully", "token": token}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/api/send-verification-code", response_model=MessageResponse)
async def send_verification_code(email: EmailRequest) -> dict:
    email = email.email
    if cache.can_send_otp(email):
        # 生成并存储验证码
        otp_code, _ = send_email(email)
        cache.store_otp(email, otp_code)
        return {"message": "验证码已发送，请在5分钟内使用。"}
    else:
        return {"message": "请求过于频繁，请稍后再试"}


@router.post("/api/login", response_model=LoginResponse)
async def login(user_data: UserLogin, db: SessionDep):
    """
    User login endpoint
    """
    user = UserCRUD.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # 生成token
    token = generate_jwt_token({"user_id": user.id, "username": user.email})
    return {"message": "Login successful", "token": token}