from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    chat_id: str
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str
    secret_key: Optional[str] = None