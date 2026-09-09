# schemas.py
from pydantic import BaseModel
from typing import Optional

# 회원 가입 시 입력 데이터 검증(입력 데이터 구조화(고정))
# BaseModel 상속, 유효성 검증(pydantic이 자체 검증)
class UserCreate(BaseModel):  
    username: str
    email: str
    password: str

# 회원 로그인 시 데이터 검증
class UserLogin(BaseModel):
     username: str
     password: str

# Pydantic 모델을 정의함, 클라이언트로 부터 받은 데이터의 데이터의 유효성 검사
# 자료형 정의(구조화 함)
class MemoCreate(BaseModel):
    title: str
    content: str

class MemoUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None