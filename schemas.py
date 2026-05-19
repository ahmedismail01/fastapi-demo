from datetime import date
from typing import Optional
from pydantic import BaseModel


# Auth schemas
class RegisterDto(BaseModel):
    email: str
    password: str
    name: str
    phone_number: str


# Posts schemas
class PostDto(BaseModel):
    title: str
    content: Optional[str] = None


class PostRead(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    date_created: date
    deleted: bool
    likes: int
    user_id: int


# Users schemas
class UserDto(BaseModel):
    name: str
    phone_number: str
    email: str
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    phone_number: str
    email: str
