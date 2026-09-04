# FastAPI는 웹 프레임워크로서 웹 서버 구축에 다양한 기능을 제공하며, 이 중 템플릿 엔진 지원이 포함됨
# 이 기능은 HTML 파일 내에서 데이터를 동적으로 처리할 수 있도록 해줌
# FastAPI는 Jinja2라는 강력한 템플릿 엔진을 사용하여 HTML 내에서 파이썬 코드를 사용할 수 있게 해줌
# Jinja2는 FastAPI의 템플릿을 취급할 때 요구되는 중요한 패키지

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from pydantic import BaseModel
from typing import Optional

# FastAPI 어플리케이션 초기화
app = FastAPI()
templates = Jinja2Templates(directory='templates')

# 데이터베이스 생성
# CREATE DATABASE my_memo_app DEFAULT CHARSET  utf8mb4 COLLATE  utf8mb4_general_ci;
DATABASE_URL = "mysql+pymysql://root:admin1234@localhost:3306/my_memo_app"
engine = create_engine(DATABASE_URL)

# SQLAlchemy의 모델 기본 클래스를 선언. 이 클래스를 상속받아 데이터베이스 테이블을 정의할 수 있음.
Base = declarative_base() # 테이블 생성 수행

class Memo(Base):   # Base 클래스 상속
    __tablename__ = 'memo'
    # 각 열(column)을 정의. id는 기본 키(primary key)로 설정됨.
    id = Column(Integer, primary_key=True, index=True)
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

# 메모 생성
@app.post('/memos/')
async def create_memo(memo: MemoCreate, db: Session=Depends(get_db)):
    new_memo = Memo(title=memo.title, content=memo.content)
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo)
    return ({'id': new_memo.id, 'title': new_memo.title, 'content': new_memo.content})
    # return {'id': new_memo.id, 'title': new_memo.title, 'content': new_memo.content}

# 메모 조회
@app.get('/memos/')
async def list_memos(db: Session=Depends(get_db)):
    memos = db.query(Memo).all()
    return [{'id': memo.id,
             'title': memo.title,
             'content': memo.content} for memo in memos]  # List 자료구조


# 메모 수정
@app.put('/memos/{memo_id}')
async def update_memo(memo_id: int, memo: MemoUpdate, db: Session=Depends(get_db)):
    db_memo = db.query(Memo).filter(Memo.id == memo_id).first()

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
async def delete_memo(memo_id: int, db: Session=Depends(get_db)):
    db_memo = db.query(Memo).filter(Memo.id == memo_id).first()

    if db_memo is None:
        return {'error': 'Memo not found.'}
    
    db.delete(db_memo)
    db.commit()
    return {'message': 'Memo deleted.'}


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


# 파일명을 main.py로 저장하고 FastAPI 애플리케이션을 실행.
# uvicorn main:app --reload 명령을 사용하여 서버를 시작.
# pip install jinja2    