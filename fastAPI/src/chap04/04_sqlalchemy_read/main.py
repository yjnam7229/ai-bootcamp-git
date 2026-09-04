from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base   
from sqlalchemy import or_, desc

# DB 설정
DATABASE_URL = "mysql+pymysql://root:admin1234@localhost/fastapi"
engine = create_engine(DATABASE_URL)

# SQLAlchemy 모델
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True)  # 길이를 50으로 설정
    email = Column(String(120))  # 길이를 120으로 설정

# Session 초기화 의존성
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

# DB에 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 초기화
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Create 부분 추가
@app.post("/users/")
def create_user(username: str, email: str, db: Session = Depends(get_db)):
    new_user = User(username=username, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None:
        return {"error": "User not found"}
    
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}

@app.get("/users/")
def read_user_all(db: Session = Depends(get_db)):
    # db_user = db.query(User).all() # select * from users
    # db_user = db.query(User.username).all() # select username from users
    # db_user = db.query(User).filter(User.username=='Choie').first() # select * from users where username=='Choie'
    db_user = db.query(User).order_by(desc(User.id)).all()

    if db_user == []:
        return {"error": "User not found"}
    
    return {"db_user": db_user}