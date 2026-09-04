from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

# 데이터베이스 설정을 위한 문자열을 정의. 이 문자열에는 사용자 이름, 비밀번호, 서버 주소, 데이터베이스 이름이 포함되어 있음.
# CREATE DATABASE fastapi DEFAULT CHARSET  utf8mb4 COLLATE  utf8mb4_general_ci;
DATABASE_URL = "mysql+pymysql://root:admin1234@localhost:3306/fastapi"
engine = create_engine(DATABASE_URL)

# SQLAlchemy의 모델 기본 클래스를 선언. 이 클래스를 상속받아 데이터베이스 테이블을 정의할 수 있음.
Base = declarative_base()

class User(Base):
    # 'users' 테이블 정의.
    __tablename__ = 'users'
    # 각 열(column)을 정의. id는 기본 키(primary key)로 설정됨.
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # 사용자 이름, 중복 불가능하고 인덱싱함.
    email = Column(String(120))  # 이메일 주소, 길이는 120자로 제한함.

# Pydantic 모델을 정의함. 이 모델은 클라이언트로부터 받은 데이터의 유효성을 검사하는 데 사용됨.
class UserCreate(BaseModel):
    username: str
    email: str

# 데이터베이스 세션을 생성하고 관리하는 의존성 함수를 정의함.
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

# 데이터베이스 엔진을 사용하여 모델을 기반으로 테이블을 생성함.
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션을 초기화.
app = FastAPI()

@app.get("/")
def read_root():
    # 루트 경로에 접근했을 때 메시지를 반환.
    return {"message": "Hello, World!"}

# 사용자를 생성하는 POST API 엔드포인트를 추가.
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Pydantic 모델을 사용하여 전달받은 데이터의 유효성을 검증하고, 새 User 인스턴스를 생성함.
    new_user = User(username=user.username, email=user.email)
    db.add(new_user)  # 생성된 User 인스턴스를 데이터베이스 세션에 추가함.
    db.commit()  # 데이터베이스에 대한 변경사항을 커밋함.
    db.refresh(new_user)  # 데이터베이스로부터 새 User 인스턴스의 최신 정보를 가져옴.
    # 새로 생성된 사용자의 정보를 반환함.
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

# 파일명을 main.py로 저장하고 FastAPI 애플리케이션을 실행함.
# uvicorn main:app --reload 명령을 사용하여 서버를 시작.