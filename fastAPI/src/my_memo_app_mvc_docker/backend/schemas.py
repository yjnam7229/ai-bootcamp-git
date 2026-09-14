from pydantic import BaseModel
from typing import Optional

# 회원가입시 데이터 검증
class UserCreate(BaseModel):
    username:str
    email:str
    password: str

# 회원 로그인시 데이터 검증
class UserLogin(BaseModel):
    username: str
    password: str

class MemoCreate(BaseModel):
    title:str
    content:str

class MemoUpdate(BaseModel):
    title:Optional[str] = None
    content:Optional[str] = None
