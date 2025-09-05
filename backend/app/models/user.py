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