from typing import Annotated, Generator
from sqlmodel import Session
from fastapi import Depends
from backend.app.core.db import engine
from fastapi.security import OAuth2PasswordBearer
from backend.app.models.user import User
from backend.app.utils.jwt_token import verify_jwt_token


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="loginByPhone")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    一个依赖项，用于从请求头中提取、验证并解码 JWT，
    然后返回当前用户信息。
    这是保护 API 路由的关键。
    """
    # 解码 JWT
    return verify_jwt_token(token)


userDeps = Annotated[User, Depends(get_current_user)]
