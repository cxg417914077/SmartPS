import aiohttp
from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr

from backend.app.models.user import UserLogin
from backend.app.crud.user import UserCRUD
from backend.app.api.deps import SessionDep
from backend.app.utils.jwt_token import generate_jwt_token
from pydantic import BaseModel


router = APIRouter()


"""
## 1. reCAPTCHA 验证 (可选)

*   **端点**: `/api/verify-captcha`
*   **方法**: `POST`
*   **请求体**:
    ```json
    {
      "email": "string",        // 用户邮箱
      "captchaToken": "string"  // reCAPTCHA v2 验证成功后获取的 token
    }
    ```
*   **响应**:
    *   **成功**: `200 OK`
        ```json
        { "message": "人机验证通过。" }
        ```
    *   **失败**: `400 Bad Request`
        ```json
        { "message": "人机验证失败，请重试。" }
        ```

---
"""
class CaptchaVerification(BaseModel):
    email: EmailStr
    captchaToken: str

@router.post("/api/verify-captcha")
async def verify_captcha(request: CaptchaVerification) -> dict:
    """
    Captcha verification endpoint
    """
    secret = "6Levxq0rAAAAAAkbPzH2EEKDckO9YT8-Xc0RAYaD"
    url = "https://www.google.com/recaptcha/api/siteverify"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={"secret": secret, "response": request.captchaToken}) as response:
            response_data = await response.json()
            if response_data["success"]:
                return {"message": "人机验证通过。"}
            return {"message": "人机验证失败，请重试。"}


@router.post("/api/register")
async def register(user_data: UserLogin, db: SessionDep):
    """
    User registration endpoint
    """
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


# 发送邮件code
@router.post("/api/send_verification_code")
async def send_verification_code(email: EmailStr) -> dict:
    return {"message": "验证码已发送，请在5分钟内使用。"}


@router.post("/api/login")
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