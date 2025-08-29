from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class LoginResponse(MessageResponse):
    token: str
