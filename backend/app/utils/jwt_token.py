from fastapi import HTTPException, status
import jwt
import datetime
from typing import Dict, Any


# 配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


def generate_jwt_token(payload: Dict[str, Any], expires_in: int = 3600) -> str:
    """生成 JWT token"""
    token_payload = payload.copy()
    token_payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    return jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
