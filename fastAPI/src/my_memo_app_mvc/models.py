# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from database import Base
from pydantic import BaseModel

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(200))
    hashed_password = Column(String(512))

class Memo(Base):   # Base 클래스 상속
    __tablename__ = 'memo'
    # 각 열(column)을 정의. id는 기본 키(primary key)로 설정됨.
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))    # 아이디가 존재하는 경우만 메모 작성
    title = Column(String(100), unique=True, index=True)
    content = Column(String(1000))    