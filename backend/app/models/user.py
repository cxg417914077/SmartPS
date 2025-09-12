from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(
        index=True, 
        unique=True, 
        nullable=False,
        max_length=20
    )
    # 积分
    score: int = Field(default=30, sa_column_kwargs={"server_default": "30"})


class UserTable(User, table=True):
    __table_args__ = {'extend_existing': True}


# 历史记录
class History(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(nullable=False, max_length=36, index=True, unique=True)
    status: str = Field(default="PENDING")
    user_id: int = Field(nullable=False, index=True)
    task_id: Optional[str] = Field(default=None, max_length=256, index=True)
    prompt: str = Field(nullable=False, default="", max_length=2048)
    upload_image: str = Field(default="", description="用户上传的图片")
    image_data: str = Field(sa_column_kwargs={"server_default": ""}, description="生成的图片")