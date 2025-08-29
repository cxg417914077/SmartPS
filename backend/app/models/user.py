from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr


class User(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(
        index=True, 
        unique=True, 
        nullable=False,
        max_length=255
    )


class UserLogin(User):
    password: str = Field(nullable=False)


class UserRegister(UserLogin):
    code: str = Field(nullable=False)


class UserTable(User, table=True):
    __table_args__ = {'extend_existing': True}
    password_hash: str = Field(nullable=False)



