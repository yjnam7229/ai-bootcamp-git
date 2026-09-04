# main.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.future import select
from typing import Optional

# 비동기 데이터베이스 설정을 위한 문자열 정의
# 이 문자열에는 사용자 이름, 비밀번호, 서버 주소, 데이터베이스 이름이 포함되어 있음
DATABASE_URL = "mysql+aiomysql://root:admin1234@localhost/fastapi"
# DATABASE_URL = "mysql+aiomysql://username:password@localhost/fastapi"

# SQLAlchemy의 비동기 엔진을 생성
engine = create_async_engine(DATABASE_URL, echo=True)   # ehco=True : SQL 쿼리가 콘솔이나 로그에 출력하라는 옵션

# 비동기 세션 생성을 위한 세션메이크를 정의
AsyncSessionLocal = sessionmaker(
    autocommit=False,  
    autoflush=False, 
    bind=engine, class_=AsyncSession    # 비동기 세션 팩토리를 생성
)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # 사용자 이름, 중복 불가능하고 인덱싱.
    email = Column(String(120))  # 이메일 주소, 길이는 120자로 제한.

# Pydantic v2 DTO
class UserCreate(BaseModel):
    username: str
    email: str

# 비동기 데이터베이스 세션을 생성하고 관리하는 의존성 함수를 정의
# 비동기 방식에서는 async와 await 키워드를 사용하여 비동기 작업 수행
# 비동기 I/O 작업을 처리
# async with 구문은 비동기 컨텍스트 메니저를 이용하여 세션의 생성과 소멸을 비동기적으로 관리
# session.commit() 세션의 변경 사항을 데이터베이스에 비동기적으로 커밋함
async def get_db():
    async with AsyncSessionLocal() as session:  
        yield session               # yield : 제너레이터 함수(Iterator함수, 데이터를 하나씩 꺼내옴)
        await session.commit()      # 대기 -> 제어권을 다른 어플, 쓰레드 에게 넘김으로써 병렬작업이 가능하게 함(속도향상)


# 데이터베이스 테이블 생성
@asynccontextmanager
async def app_lifespan(app: FastAPI):   # fastAPI 어플리케이션의 생명주기 동안 특정 작업을 수행함 
    # 애플리케이션 시작 시 실행될 로직
    # 비동기 컨텍스트 매니저 : 리소스의 비동기적 할당과 해제를 관리함
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  
    # 애플리케이션 종료 시 실행될 로직 (필요한 경우)

# fastAPI 어플리케이션을 초기화
app = FastAPI(lifespan=app_lifespan)

@app.post('/users/')
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = User(username=user.username, email=user.email)
    db.add(new_user)
    await db.commit()           # 반드시 비동기 await 
    await db.refresh(new_user)

    # 새로 생성된 사용자의 정보를 반환
    return {'id': new_user.id, 'username':new_user.username, 'email':new_user.email}

@app.get('/users/{user_id}')
async def read_user(user_id:int, db: AsyncSession = Depends(get_db)):
    # 비동기 세션을 사용하여 데이터베이스 쿼리를 실행
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalar_one_or_none()

    return db_user

# Pydantic v2 DTO
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

# 수정
@app.put('/users/{user_id}')
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    # 비동기 쿼리 실행
    result = await db.execute(select(User).filter(User.id == user_id)) # 데이터 존재 여부 확인
    db_user = result.scalars().first()

    if db_user is None:
        return {"error": "User not found"}

    if user.username is not None:
        db_user.username = user.username

    if user.email is not None:
        db_user.email = user.email

    # await 키워드 : DB와 실시간으로 연동 -> 비동기적 으로 처리
    await db.commit()
    await db.refresh(db_user)

    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}

# 삭제
@app.delete('/users/{user_id}')
async def delete_user(user_id: int, db: AsyncSession=Depends(get_db)):
    # 비동기 쿼리 실행
    result = await update_user(user_id)
    # result = await db.execute(select(User).filter(User.id == user_id))

    db_user = result.scalars().first()

    if db_user is None:
        return {"error": "사용자를 찾을 수 없습니다."}

    await db.delete(db_user)
    await db.commit()

    return {'message': '사용자가 성공적으로 삭제되었습니다.'}

    
        





 







