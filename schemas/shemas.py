# For Data Validations
from pydantic import BaseModel, EmailStr


class UserAdd(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ChangeUserRole(BaseModel):
    role: str


class ChangeUserName(BaseModel):
    name: str


class AddTVShows(BaseModel):
    show_name: str
    tv_show_image: str
