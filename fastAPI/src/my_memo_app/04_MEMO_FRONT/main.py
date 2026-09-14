# MEMO_FRONT
# 사용자별로 해당 메모 관리(사용자별 메모리 관리)
# 로그인 관련 필요 패키지 설치
# pip install passlib==1.7.4 bcrypt==3.2.2

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from pydantic import BaseModel
from typing import Optional

from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware

# 패스워드 Hash 알고리즘을 적용 -> 암복호화
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# 사용자 입력 패스워드 hash(암호화/복호회)
def get_password_hash(password: str):
    return pwd_context.hash(password)

# 패스워드 일치 여부 검증, plain_password : 사용자 입력 패스워드
def verify_password(plain_password, hash_password):   
    return pwd_context.verify(plain_password, hash_password)

# FastAPI 어플리케이션 초기화
app = FastAPI()

# 세션 미들웨어 추가, 'verysecret'는 실제 사용 시 안전한 키로 교체해야 합니다.
app.add_middleware(SessionMiddleware, secret_key='your-secret-key')

templates = Jinja2Templates(directory='templates')

# 데이터베이스 생성
# CREATE DATABASE my_memo_app DEFAULT CHARSET  utf8mb4 COLLATE  utf8mb4_general_ci;
DATABASE_URL = "mysql+pymysql://root:admin1234@localhost:3306/my_memo_app"
engine = create_engine(DATABASE_URL)

# SQLAlchemy의 모델 기본 클래스를 선언. 이 클래스를 상속받아 데이터베이스 테이블을 정의할 수 있음.
Base = declarative_base() # 테이블 생성 수행

# 회원 관리 시작
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(200))
    hashed_password = Column(String(512))

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
# 회원 관리 끝

class Memo(Base):   # Base 클래스 상속
    __tablename__ = 'memo'
    # 각 열(column)을 정의. id는 기본 키(primary key)로 설정됨.
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))    # 아이디가 존재하는 경우만 메모 작성
    title = Column(String(100), unique=True, index=True)
    content = Column(String(1000))

# Pydantic 모델을 정의함, 클라이언트로 부터 받은 데이터의 데이터의 유효성 검사
# 자료형 정의(구조화 함)
class MemoCreate(BaseModel):
    title: str
    content: str

class MemoUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# 데이터베이스 세션을 생성하고 관리하는 의존성 함수 정의
# Depends(함수) 방식
def get_db():
    db = Session(bind=engine)
    try:
        yield db    # yield : 제너레이터 함수(iterator 함수, 데이터를 하나 하나씩 꺼내옴)
    finally:
        db.close()        

# 데이터베이스 엔진을 사용하여 모델을 기반으로 테이블을 생성함
Base.metadata.create_all(bind=engine)

# 회원 가입
# UserCreate 자체적으로 유효성 검증(pydantic)
@app.post('/signup')
async def signup(signup_data: UserCreate, db: Session=Depends(get_db)): 
    # username 중복 체크
    existing_user = db.query(User).filter(User.username == signup_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='이미 동일한 사용자 이름이 가입되어 있습니다.')
    
    hashed_password = get_password_hash(signup_data.password)  # 패스워드 암복호화
    new_user = User(username=signup_data.username, email=signup_data.email, hashed_password=hashed_password)

    db.add(new_user)
    try:
        db.commit()
    except Exception as e:   
        print(e) 
        raise HTTPException(status_code=500, detail='회원 가입이 실패했습니다. 가입한 내용을 확인해 보세요.')
        
    db.refresh(new_user)
    return {'message:', '회원 가입이 성공 했습니다.'}

# 로그인
@app.post('/login')
async def login(request: Request, signin_data: UserLogin, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.username == signin_data.username).first()
    if user and verify_password(signin_data.password, user.hashed_password):
        request.session['username'] = user.username   # 쿠키의 저장소에 보관된 데이터 -> session에 전달
        return {'message:', 'Logged in successfully'}
    else:
        raise HTTPException(status_code=401, detail='Invalid credentials')

# 로그아웃
@app.post('/logout')
async def logout(request: Request):
    request.session.pop('username', None)  # pop() 꺼내옴 -> 버림
    return {'message': 'Logged out successfully'}


# 메모 생성(CRUD)
@app.post('/memos/')
async def create_memo(request:Request, memo: MemoCreate, db: Session=Depends(get_db)):
    username = request.session.get('username')
    if username is None:
            raise HTTPException(status_code=401, detail='Not authorized')

    user = db.query(User).filter(User.username == username).first()
    if user is None:
            raise HTTPException(status_code=404, detail='User not found')

    new_memo = Memo(user_id=user.id, title=memo.title, content=memo.content)

    db.add(new_memo)
    db.commit()
    db.refresh(new_memo)
    return ({'id': new_memo.id, 'title': new_memo.title, 'content': new_memo.content})

# 메모 조회(login한 사용자의 메모만 조회)
@app.get('/memos/')
async def list_memos(request: Request, db: Session=Depends(get_db)):
    username = request.session.get('username')
    if username is None:
        raise HTTPException(status_code=401, detail='Not authorized')

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')

    # 로그인한 사용자가 작성한 메모만 가져옴
    memos = db.query(Memo).filter(Memo.user_id == user.id).all() 
    return [{'id': memo.id,
             'title': memo.title,
             'content': memo.content} for memo in memos]  # List 자료구조


# 메모 수정
@app.put('/memos/{memo_id}')
async def update_memo(request: Request, memo_id: int, memo: MemoUpdate, db: Session=Depends(get_db)):
    # 로그인 여부 체크
    username = request.session.get('username')
    if username is None:
            raise HTTPException(status_code=401, detail='Not authorized')
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
            raise HTTPException(status_code=404, detail='User not found')

    db_memo = db.query(Memo).filter(Memo.user_id == user.id, Memo.id == memo_id).first()

    if db_memo is None:
        return {'error': 'Memo not found'}
    
    if memo.title is not None:
        db_memo.title = memo.title
    if memo.content is not None:
        db_memo.content = memo.content

    db.commit()
    db.refresh(db_memo)                
    return ({'id': db_memo.id, 'title': db_memo.title, 'content': db_memo.content})

# 메모 삭제 
@app.delete('/memos/{memo_id}')
async def delete_memo(request: Request, 
                      memo_id: int,
                      db: Session=Depends(get_db) 
                      ):

    # check = check_user_info()

    # 로그인 여부 체크
    username = request.session.get('username')
    if username is None:
            raise HTTPException(status_code=401, detail='Not authorized')
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
            raise HTTPException(status_code=404, detail='User not found')

    db_memo = db.query(Memo).filter(Memo.user_id == user.id, Memo.id == memo_id).first()

    if db_memo is None:
        return {'error': 'Memo not found.'}
    
    db.delete(db_memo)
    db.commit()
    return {'message': 'Memo deleted.'}


# @app.delete('/memos/{memo_id}')
# async def delete_memo(request: Request, memo_id: int, db: Session=Depends(get_db)):
#     check = check_user_info()
    
#     # 로그인 여부 체크
#     username = request.session.get('username')
#     if username is None:
#             raise HTTPException(status_code=401, detail='Not authorized')
    
#     user = db.query(User).filter(User.username == username).first()
#     if user is None:
#             raise HTTPException(status_code=404, detail='User not found')

#     db_memo = db.query(Memo).filter(Memo.user_id == user.id, Memo.id == memo_id).first()

#     if db_memo is None:
#         return {'error': 'Memo not found.'}
    
#     db.delete(db_memo)
#     db.commit()
#     return {'message': 'Memo deleted.'}


# 기본 라우팅
# curl http://127.0.0.1:8000/
@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse(
        request, 'home.html'
    )

# 확장 라우팅
@app.get('/about')
async def about():
    return {'message': '이것은 마이 메모 앱의 소개 페이지입니다.'}


# 작성 중
async def check_user_info(request: Request, db: Session=Depends(get_db)):
    # 로그인 여부 체크
    username = request.session.get('username')
    if username is None:
            raise HTTPException(status_code=401, detail='Not authorized')
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
            raise HTTPException(status_code=404, detail='User not found')

    return user

# 파일명을 main.py로 저장하고 FastAPI 애플리케이션을 실행.
# uvicorn main:app --reload 명령을 사용하여 서버를 시작.
# pip install jinja2    