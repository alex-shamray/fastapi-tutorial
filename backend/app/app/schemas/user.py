import gzip
from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from app.core.config import settings


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None

    @validator('password', check_fields=False)
    def password_minimum_length(cls, v):
        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(
                f"This password is too short. It must contain at least {settings.PASSWORD_MIN_LENGTH} characters.",
            )
        return v

    @validator('password', check_fields=False)
    def common_password(cls, v):
        password_list_path = settings.DEFAULT_PASSWORD_LIST_PATH
        try:
            with gzip.open(password_list_path, 'rt', encoding='utf-8') as f:
                passwords = {x.strip() for x in f}
        except OSError:
            with open(password_list_path) as f:
                passwords = {x.strip() for x in f}
        if v.lower().strip() in passwords:
            raise ValueError('This password is too common.')
        return v


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
