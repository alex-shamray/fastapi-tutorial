import gzip
import re
from difflib import SequenceMatcher
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
    def password_user_attribute_similarity(cls, v, values, **kwargs):
        max_similarity = 0.7
        for attribute_name, value in values.items():
            if not value or not isinstance(value, str):
                continue
            value_parts = re.split(r'\W+', value) + [value]
            for value_part in value_parts:
                if SequenceMatcher(a=v.lower(), b=value_part.lower()).quick_ratio() >= max_similarity:
                    raise ValueError(
                        f'The password is too similar to the {attribute_name}.',
                    )
        return v

    @validator('password', check_fields=False)
    def password_common(cls, v):
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

    @validator('password', check_fields=False)
    def password_numeric(cls, v):
        if v.isdigit():
            raise ValueError('This password is entirely numeric.')
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
